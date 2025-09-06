from __future__ import annotations
import abc
import asyncio
from collections import deque
import datetime
import logging
from pathlib import Path
import random
import multiprocessing
import threading
import signal
import os
import sys
import time
import weakref
import typing as t

from quart import Quart, url_for, request
from typing_extensions import Self

from .types import (
    JobID, ValidationError, WorkerID,
    # worker - server communication
    WorkerMessage, JobResponse, SignalResponse, OkResponse, ServerResponse, Signal,
    # server - client communication
    WorkerStatus, WorkerState, WorkerUpdate, WorkersUpdate, LogRecord,
    JobStatus, JobState, JobStatusChange, JobUpdate, LogUpdate, JobStopped, JobMessage, JobsUpdate,
)

T = t.TypeVar('T')


class Shutdown(Exception):
    pass


async def raise_on_shutdown():
    await server.shutdown_event.wait()
    raise Shutdown()


class Subscribable(t.Generic[T]):
    def __init__(self):
        self.subscribers: set[asyncio.Queue[T]] = set()

    async def subscribe(self) -> t.AsyncIterator[T]:
        connection: asyncio.Queue[T] = asyncio.Queue()
        self.subscribers.add(connection)
        try:
            while True:
                yield await connection.get()
        finally:  # called when future is cancelled
            self.subscribers.remove(connection)

    async def message_subscribers(self, msg: T):
        for subscriber in self.subscribers:
            await subscriber.put(msg)


class Worker(Subscribable[WorkerUpdate], abc.ABC):
    def __init__(self, worker_id: WorkerID):
        super().__init__()
        self.status: WorkerStatus = 'queued'
        self.id: WorkerID = worker_id

        self.current_job: t.Optional[weakref.ref[Job]] = None
        self.start_time: t.Optional[datetime.datetime] = None
        """UTC time worker started running at"""
        self.hostname: t.Optional[str] = None
        """Hostname worker is running on"""
        self.backends: t.Optional[t.Dict[str, t.Tuple[str, ...]]] = None
        """Computational backends available to worker"""

    @abc.abstractmethod
    def worker_type(self) -> str:
        ...

    def state(self) -> WorkerState:
        links = {
            'shutdown': url_for('shutdown_worker', worker_id=self.id),
            'reload': url_for('reload_worker', worker_id=self.id),
        }
        current_job = job.id if self.current_job and (job := self.current_job()) else None
        return WorkerState(
            self.id, self.worker_type(), self.status, links=links,
            current_job=current_job, start_time=self.start_time,
            hostname=self.hostname, backends=self.backends,
        )

    async def cancel(self):
        if self.status == 'queued':
            await self.set_status('stopped')
        elif self.status not in ('stopping', 'stopped'):
            await self.set_status('stopping')

    async def reload(self):
        if self.status not in ('stopping', 'stopped'):
            await self.set_status('reloading')

    def action(self) -> t.Optional[Signal]:
        if self.status == 'stopping':
            return 'shutdown'
        elif self.status == 'reloading':
            return 'reload'
        return None

    async def set_status(self, status: WorkerStatus):
        self.status = status
        await self.message_subscribers(WorkerUpdate(self.id, status))

        if status == 'stopped':
            if self.current_job and (job := self.current_job()):
                await job.set_status('stopped')
            server.workers.schedule_for_removal(self.id, 5.0)

    async def handle_message(self, msg: WorkerMessage) -> ServerResponse:
        if msg.msg == 'shutdown':
            await self.set_status('stopped')
            return OkResponse()

        if msg.msg == 'connect':
            self.start_time = datetime.datetime.now(datetime.timezone.utc)
            self.hostname = 'localhost' if self.worker_type() == 'local' else msg.hostname
            self.backends = msg.backends
            await self.set_status('idle')

        if (job_id := getattr(msg, 'job_id', None)):
            job = server.jobs[job_id]
            await job.handle_update(msg)

            if job.should_cancel():
                return SignalResponse(self.action() or 'cancel')

        if (action := self.action()):
            return SignalResponse(action)

        if msg.msg in ('poll', 'job_result'):
            if len(server.job_queue):
                # send a new job if available
                job = server.job_queue.popleft()
                self.current_job = weakref.ref(job)
                await self.set_status('running')
                job.start_time = datetime.datetime.now(datetime.timezone.utc)
                await job.set_status('starting')
                return JobResponse(job.id, job.plan)
            else:
                # otherwise don't
                self.current_job = None
                await self.set_status('idle')

        return OkResponse()

    async def finalize(self):
        if self.status not in ('stopped', 'unknown'):
            logging.error(f"Job {self.id} finalized before completion")


class LocalWorker(Worker):
    def __init__(self, worker_id: WorkerID, url: str):
        super().__init__(worker_id)
        self.url = url

        self._start()
        self._fut: asyncio.Task[None] = asyncio.create_task(asyncio.to_thread(self._watch_process))

    def worker_type(self) -> str:
        return 'local'

    def _start(self):
        from phaser.web.worker import run_worker

        quiet = False
        self.process = multiprocessing.Process(target=run_worker, args=[self.url, quiet], daemon=True)
        self.status = 'starting'
        self.process.start()

    def _watch_process(self):
        while True:
            self.process.join()

            sig = t.cast(int, self.process.exitcode) - 128
            if sig == getattr(signal, 'SIGHUP', 1):
                # restart process
                self._start()
                continue
            else:
                # TODO call set_status here
                self.status = 'stopped'
            break

    async def finalize(self):
        self.process.terminate()
        await self._fut


class ManualWorker(Worker):
    def __init__(self, worker_id: WorkerID):
        self.url = server.get_worker_url(worker_id)
        logging.warning(f"Worker command: python -m phaser worker {self.url}")
        super().__init__(worker_id)

    def worker_type(self) -> str:
        return 'manual'


class Workers(Subscribable[WorkersUpdate]):
    def __init__(self):
        super().__init__()
        self.inner: t.Dict[WorkerID, Worker] = {}
        self._futs: t.List[asyncio.Task[None]] = []

    def state(self) -> t.List[WorkerState]:
        return [worker.state() for worker in self.inner.values()]

    async def _subscribe_to_worker(self, worker: Worker):
        async for msg in worker.subscribe():
            if msg.msg == 'status_change':
                await self.message_subscribers(
                    WorkersUpdate(msg, self.state())
                )

    async def add(self, worker: Worker):
        self.inner[worker.id] = worker

        event = WorkerUpdate(worker.id, worker.status)
        await self.message_subscribers(WorkersUpdate(event, self.state()))
        self._futs.append(asyncio.create_task(self._subscribe_to_worker(worker)))

    def schedule_for_removal(self, worker_id: WorkerID, delay: float = 30.0):
        if worker_id not in self:
            return

        async def task():
            async with server.app.app_context():
                await asyncio.sleep(delay)
                await self.remove(worker_id)

        self._futs.append(asyncio.create_task(task()))

    async def remove(self, worker_id: WorkerID):
        try:
            worker = self.inner.pop(worker_id)
        except KeyError:
            return

        await worker.finalize()
        await self.message_subscribers(
            WorkersUpdate(None, self.state())
        )

    def __contains__(self, item: WorkerID) -> bool:
        return self.inner.__contains__(item)

    def __getitem__(self, item: WorkerID) -> Worker:
        return self.inner[item]

    def items(self) -> t.ItemsView[WorkerID, Worker]:
        return self.inner.items()

    def keys(self) -> t.KeysView[WorkerID]:
        return self.inner.keys()

    def values(self) -> t.ValuesView[Worker]:
        return self.inner.values()

    async def finalize(self):
        for fut in self._futs:
            fut.cancel()
        await asyncio.gather(*(worker.finalize() for worker in self.inner.values()))


class Job(Subscribable[JobMessage]):
    def __init__(self, id: JobID, plan: str, name: t.Optional[str] = None):
        super().__init__()
        self.id: JobID = id
        self.plan: str = plan
        self.job_name: t.Optional[str] = name
        """Name of job"""
        self.status: JobStatus = 'queued'
        self.cache: t.Dict[str, t.Any] = {}
        """Cache of job state"""
        self.logs: t.List[LogRecord] = []
        """Cache of recorded messages"""
        self.start_time: t.Optional[datetime.datetime] = None
        """Time job was started at"""

    @classmethod
    async def from_path(cls, path: t.Union[str, Path]) -> t.List[Self]:
        process = await asyncio.create_subprocess_exec(
            sys.executable, '-m', 'phaser', 'validate', '--json', str(path),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await process.communicate()
        return await cls._process_validate_result(stdout)

    @classmethod
    async def from_yaml(cls, plan: t.Union[str, bytes]) -> t.List[Self]:
        process = await asyncio.create_subprocess_exec(
            sys.executable, '-m', 'phaser', 'validate', '--json',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        assert process.stdin is not None
        process.stdin.write(plan if isinstance(plan, (bytes, bytearray, memoryview)) else plan.encode('utf-8'))
        stdout, _ = await process.communicate()
        return await cls._process_validate_result(stdout)

    @classmethod
    async def _process_validate_result(cls, stdout: bytes) -> t.List[Self]:
        import json
        result = json.loads(stdout)
        if result['result'] == 'error':
            raise ValidationError(result['error'])

        assert result['result'] == 'success'
        jobs = [
            cls(server.make_jobid(), json.dumps(plan), name)
            for (name, plan) in result['plans']
        ]
        for job in jobs:
            await server.jobs.add(job)
        return jobs

    async def set_status(self, status: JobStatus):
        if self.status == status:
            return
        self.status = status
        await self.message_subscribers(
            JobStatusChange(status, self.id)
        )

    async def cancel(self):
        if self.status == 'queued':
            await self.set_status('stopped')
        elif self.status not in ('stopping', 'stopped'):
            await self.set_status('stopping')

    def should_cancel(self) -> bool:
        return self.status == 'stopping'

    async def delete(self):
        if self.status not in ('queued', 'stopped'):
            raise RuntimeError("Cannot delete a running job")
        if self.status != 'stopped':
            await self.set_status('stopped')
        await server.jobs.remove(self.id)

    def state(self, full: bool = False) -> JobState:
        state = self.cache if full else {k: v for (k, v) in self.cache.items() if k == 'iter'}
        links = {
            'dashboard': url_for('job_dashboard', job_id=self.id),
            'cancel': url_for('cancel_job', job_id=self.id), 
            'delete': url_for('delete_job', job_id=self.id), 
            'logs': url_for('job_logs', job_id=self.id),
        }
        return JobState.make_unchecked(
            self.id, self.status, links, job_name=self.job_name, start_time=self.start_time, state=state,
        )

    async def handle_update(self, msg: WorkerMessage):
        if msg.msg == 'job_update':
            if self.status in ('queued', 'starting'):
                await self.set_status('running')

            self.cache.update(msg.state)
            await self.message_subscribers(
                JobUpdate.make_unchecked(msg.state, msg.job_id)
            )
        elif msg.msg == 'log':
            record = msg.into_record(len(self.logs))
            self.logs.append(record)
            await self.message_subscribers(
                LogUpdate.make_unchecked([record])
            )
        elif msg.msg == 'job_result':
            self.status = 'stopped'
            await self.message_subscribers(
                JobStopped(msg.result, msg.error)
            )

    async def finalize(self):
        if self.status != 'stopped':
            logging.error(f"Job {self.id} finalized before completion")


class Jobs(Subscribable[JobsUpdate]):
    def __init__(self):
        super().__init__()
        self.inner: t.Dict[JobID, Job] = {}
        self._futs: t.List[asyncio.Task[None]] = []

    def state(self) -> t.List[JobState]:
        return [job.state() for job in self.inner.values()]

    async def _subscribe_to_job(self, job: Job):
        total_iter = job.cache.get('iter', {}).get('total_iter', None)
        async for msg in job.subscribe():
            # update if status changed or iteration # changed
            if (new_total_iter := job.cache.get('iter', {}).get('total_iter', None)) != total_iter or msg.msg in ('status_change', 'job_stopped'):
                total_iter = new_total_iter
                await self.message_subscribers(
                    JobsUpdate.make_unchecked(msg, self.state())
                )

    async def add(self, job: Job):
        self.inner[job.id] = job
        self._futs.append(asyncio.create_task(self._subscribe_to_job(job)))
        server.job_queue.append(job)

        event = JobStatusChange(job.status, job.id)
        await self.message_subscribers(
            JobsUpdate.make_unchecked(event, self.state())
        )

    async def remove(self, job_id: JobID):
        try:
            job = self.inner.pop(job_id)
        except KeyError:
            return

        await job.finalize()
        await self.message_subscribers(
            JobsUpdate(None, self.state())
        )

    def __contains__(self, item: JobID) -> bool:
        return self.inner.__contains__(item)

    def __getitem__(self, item: JobID) -> Job:
        return self.inner[item]

    def items(self) -> t.ItemsView[JobID, Job]:
        return self.inner.items()

    def keys(self) -> t.KeysView[JobID]:
        return self.inner.keys()

    def values(self) -> t.ValuesView[Job]:
        return self.inner.values()

    async def finalize(self):
        for fut in self._futs:
            fut.cancel()
        await asyncio.gather(*(job.finalize() for job in self.inner.values()))


_ID_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


class Server:
    def __init__(self):
        self.app: Quart = Quart(
            __name__,
            static_url_path="/static",
            static_folder="dist",
        )
        self.app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 5
        self.app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024  # 512 MiB

        @self.app.after_serving
        async def shutdown():
            logging.info("Shutting down...")
            try:
                async with asyncio.timeout(5):
                    await asyncio.gather(self.jobs.finalize(), self.workers.finalize(), self.slurm_manager.finalize(), *self.futs)
            except TimeoutError:
                logging.warning("Cleanup didn't finish in time")

    def get_worker_url(self, worker_id: WorkerID) -> str:
        assert self.host is not None
        url_adapter = self.app.url_map.bind(self.host, self.root_path, url_scheme='http')
        url = url_adapter.build('worker_update', dict(worker_id=worker_id), method='POST', force_external=True)
        return url

    def make_workerid(self) -> WorkerID:
        while True:
            id = "".join(_ID_CHARS[random.randrange(0, len(_ID_CHARS))] for _ in range(10))
            if id not in self.workers:
                return id

    def make_jobid(self) -> JobID:
        while True:
            id = "".join(_ID_CHARS[random.randrange(0, len(_ID_CHARS))] for _ in range(10))
            if id not in self.jobs:
                return id

    def _set_signals(self, loop: asyncio.AbstractEventLoop):
        last_time: t.Optional[float] = None

        def _signal_handler(signal: str) -> None:
            if signal != 'SIGINT':
                logging.warning(f"Received {signal}. Stopping...")
                self.shutdown_event.set()
                return

            if not loop.is_running():
                return

            nonlocal last_time
            t = time.monotonic()

            if last_time is not None and t - last_time < 2:
                self.shutdown_event.set()
                return

            logging.warning("Workers interrupted. Press CTRL + C twice to quit server")
            last_time = t

        for signal_name in ("SIGINT", "SIGTERM", "SIGBREAK", "SIGQUIT"):
            if hasattr(signal, signal_name):
                try:
                    loop.add_signal_handler(getattr(signal, signal_name), _signal_handler, signal_name)
                except NotImplementedError:
                    # Add signal handler may not be implemented on Windows
                    signal.signal(getattr(signal, signal_name), lambda _sig, _frame: _signal_handler(signal_name))

    def run(
            self,
            hostname: str = 'localhost',
            port: t.Optional[int] = None,
            root_path: t.Optional[str] = None,
            verbosity: int = 0,
            serving_cb: t.Optional[t.Callable[[], t.Any]] = None,
    ):
        self.workers: Workers = Workers()
        self.jobs: Jobs = Jobs()
        self.job_queue: deque[Job] = deque()
        self.futs: t.List[t.Awaitable[t.Any]] = []

        self.shutdown_event: asyncio.Event = asyncio.Event()

        from .slurm import SlurmManager

        self.slurm_manager: SlurmManager = SlurmManager()

        self.host = f"{hostname}:{port or 5050}"
        self.root_path = root_path or os.environ.get("SCRIPT_NAME")

        if serving_cb:
            self.app.before_serving(serving_cb)

        logging.basicConfig(level=logging.INFO if verbosity == 0 else logging.DEBUG)

        if verbosity > 0:
            @self.app.before_request
            async def log_request():
                logging.debug(f"{request.method} {request.path} {request.user_agent}")

            self.app.config['DEBUG'] = True

        multiprocessing.set_start_method('spawn', True)

        loop = asyncio.new_event_loop()
        loop.set_debug(verbosity > 1)
        asyncio.set_event_loop(loop)

        if threading.current_thread() is threading.main_thread():
            self._set_signals(loop)

        from hypercorn.config import Config
        from hypercorn.asyncio import serve

        try:
            loop.run_until_complete(
                serve(self.app, Config.from_mapping(
                    bind=self.host,
                    root_path=self.root_path,
                    #websocket_max_message_size="512MiB",
                    #wsgi_max_body_size="512MiB",
                ), shutdown_trigger=self.shutdown_event.wait)
            )
        finally:
            #loop.run_until_complete(self.app.shutdown())
            try:
                _cancel_all_tasks(loop)
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                asyncio.set_event_loop(None)
                loop.close()


def _cancel_all_tasks(loop: asyncio.AbstractEventLoop) -> None:
    tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
    if not tasks:
        return

    for task in tasks:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

    for task in tasks:
        if not task.cancelled() and task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


server: Server = Server()

from . import routes  # noqa: E402, F401
