import asyncio
import base64
import dataclasses
import typing as t

import numpy
from pane.converters import Converter
from pane.errors import ProductErrorNode, WrongTypeError, ParseInterrupt

T = t.TypeVar('T')

class _array_dummy():
    def __init__(self, array_interface: t.Any):
        self.__array_interface__ = array_interface


async def merge_streams(
    *its: t.AsyncIterable[T]
) -> t.AsyncIterator[T]:
    # TODO: better error handling here
    queue = asyncio.Queue(1)

    async def task(it: t.AsyncIterable[T]):
        async for item in it:
            await queue.put(item)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(task(it)) for it in its]

        while not all(task.done() for task in tasks):
            yield await queue.get()


def encode_obj(obj: t.Any, to_numpy: bool = True) -> t.Any:
    if isinstance(obj, numpy.ndarray):
        if not to_numpy:
            return obj.tolist()
        d = obj.__array_interface__
        d['data'] = base64.urlsafe_b64encode(obj.tobytes()).decode('ascii')
        d['_ty'] = 'numpy'
        return d

    if isinstance(obj, bytes):
        return {
            '_ty': 'bytes',
            'data': base64.urlsafe_b64encode(obj).decode('ascii')
        }

    if isinstance(obj, dict):
        d = obj
    elif dataclasses.is_dataclass(obj):
        d = obj.asdict()  # type: ignore
    else:
        return obj

    return {k: encode_obj(v, to_numpy and k not in ('sampling',)) for (k, v) in d.items()}


def decode_obj(obj: t.Any) -> t.Any:
    if isinstance(obj, dict):
        d = obj
    elif dataclasses.is_dataclass(obj):
        d = obj.asdict()  # type: ignore
    else:
        return obj

    if '_ty' not in d:
        return {k: decode_obj(v) for (k, v) in d.items()}
    ty = d.pop('_ty')

    if ty == 'numpy':
        d['data'] = base64.urlsafe_b64decode(d['data'].encode('utf-8'))
        d['shape'] = tuple(d['shape'])
        return numpy.array(_array_dummy(d))

    if ty == 'bytes':
        return base64.urlsafe_b64decode(d['data'].encode('utf-8'))

    raise ValueError(f"Unknown custom type '{ty}', while parsing reconstruction state update")


class ReconsStateConverter(Converter[t.Dict[str, t.Any]]):
    def __init__(self):
        ...

    def expected(self, plural: bool = False) -> str:
        return "reconstruction state"

    def into_data(self, val: t.Any) -> t.Any:
        return encode_obj(val)

    def try_convert(self, val: t.Any) -> t.Dict[str, t.Any]:
        try:
            val = decode_obj(val)
        except Exception:
            raise ParseInterrupt()
        #if not isinstance(val, t.Mapping) or ({'iter', 'wavelength'} - val.keys()):
        #    raise ParseInterrupt()

        return val  # type: ignore

    def collect_errors(self, val: t.Any) -> t.Union[ProductErrorNode, WrongTypeError, None]:
        try:
            val = decode_obj(val)
        except Exception as e:
            import traceback

            tb = e.__traceback__.tb_next  # type: ignore
            tb = traceback.TracebackException(type(e), e, tb)
            return WrongTypeError(self.expected(), val, tb)
        if not isinstance(val, t.Mapping):
            return WrongTypeError(self.expected(), val)
        #if (missing := {'iter', 'wavelength'} - val.keys()):
        #    return ProductErrorNode(self.expected(), {}, val, missing)

        return None