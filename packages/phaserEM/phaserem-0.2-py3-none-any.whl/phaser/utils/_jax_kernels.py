
from functools import partial
import typing as t

from numpy.typing import ArrayLike
import jax  # pyright: ignore[reportMissingImports]
import jax.numpy as jnp    # pyright: ignore[reportMissingImports]


def to_nd(arr: jax.Array, n: int) -> jax.Array:
    if arr.ndim > n:
        arr = arr.reshape(-1, *arr.shape[arr.ndim - n + 1:])
    elif arr.ndim < n:
        arr = jax.lax.expand_dims(arr, [0] * (n - arr.ndim))

    return arr

to_2d = partial(to_nd, n=2)
to_3d = partial(to_nd, n=3)


def _flatten_ndim(arr: jax.Array, n: int) -> jax.Array:
    return arr.reshape(-1, *arr.shape[n+1:])


@jax.jit
def set_cutouts(obj: jax.Array, cutouts: jax.Array, start_idxs: jax.Array) -> jax.Array:
    def inner(obj: jax.Array, v: t.Tuple[jax.Array, jax.Array]) -> t.Tuple[jax.Array, None]:
        (cutouts, start_idxs) = v
        obj = jax.vmap(lambda slice, cutouts: jax.lax.dynamic_update_slice(slice, cutouts, start_idxs))(obj, to_3d(cutouts))
        return (obj, None)

    start_idxs = jnp.atleast_2d(start_idxs)
    (cutouts, start_idxs) = map(lambda a: _flatten_ndim(a, start_idxs.ndim - 2), (cutouts, start_idxs))
    return jax.lax.scan(inner, to_3d(obj), (cutouts, start_idxs))[0].reshape(obj.shape)


@jax.jit
def add_cutouts(obj: jax.Array, cutouts: jax.Array, start_idxs: jax.Array) -> jax.Array:
    zero_obj = jax.numpy.zeros_like(obj, shape=obj.shape[-2:])

    def inner(obj: jax.Array, v: t.Tuple[jax.Array, jax.Array]) -> t.Tuple[jax.Array, None]:
        (cutouts, start_idxs) = v
        obj += jax.vmap(lambda cutouts: jax.lax.dynamic_update_slice(zero_obj, cutouts, start_idxs))(to_3d(cutouts))
        return (obj, None)

    start_idxs = jnp.atleast_2d(start_idxs)
    (cutouts, start_idxs) = map(lambda a: _flatten_ndim(a, start_idxs.ndim - 2), (cutouts, start_idxs))
    return jax.lax.scan(inner, to_3d(obj), (cutouts, start_idxs))[0].reshape(obj.shape)


@partial(jax.jit, static_argnums=2)
def get_cutouts(obj: jax.Array, start_idxs: jax.Array, cutout_shape: t.Tuple[int, int]) -> jax.Array:
    return jax.vmap(jax.vmap(lambda start_idx, obj: jax.lax.dynamic_slice(obj, start_idx, cutout_shape), (None, 0)), (0, None))(
        to_2d(start_idxs), to_3d(obj)
    ).reshape((*start_idxs.shape[:-1], *obj.shape[:-2], *cutout_shape))


@partial(jax.jit, static_argnums=0)
def outer(ufunc: t.Any, x: jax.Array, y: jax.Array) -> jax.Array:
    if x.ndim == 0 or y.ndim == 0:
        return ufunc(x, y)

    out_shape = (*x.shape, *y.shape)
    return jax.vmap(jax.vmap(ufunc, (None, 0)), (0, None))(x.ravel(), y.ravel()).reshape(out_shape)


@partial(jax.jit, static_argnames=('output_shape', 'order', 'mode', 'cval'))
def affine_transform(
    input: jax.Array,
    matrix: ArrayLike,
    offset: t.Optional[ArrayLike] = None,
    output_shape: t.Optional[t.Tuple[int, ...]] = None,
    order: int = 1,
    mode: str = 'constant',
    cval: t.Any = 0.0,
) -> jax.Array:
    import jax.scipy.ndimage
    jax_mode = {'grid-constant': 'constant', 'grid-wrap': 'wrap'}.get(mode, mode)

    if output_shape is None:
        output_shape = input.shape
    n_axes = len(output_shape)  # num axes to transform over

    indices = jnp.indices(output_shape, dtype=float)

    matrix = jnp.array(matrix)
    if matrix.shape == (n_axes + 1, n_axes + 1):
        # homogenous transform matrix
        coords = jnp.tensordot(
            matrix, jnp.stack((*indices, jnp.ones_like(indices[0])), axis=0), axes=1
        )[:-1]
    elif matrix.shape == (n_axes,):
        coords = (indices.T * matrix + jnp.array(offset)).T
    else:
        raise ValueError(f"Expected matrix of shape ({n_axes + 1}, {n_axes + 1}) or ({n_axes},), instead got shape {matrix.shape}")

    coords += jnp.finfo(coords.dtype).eps

    return jax.vmap(
        lambda a: jax.scipy.ndimage.map_coordinates(a, tuple(coords), order=order, mode=jax_mode, cval=cval),
    )(to_nd(input, n_axes + 1)).reshape((*input.shape[:-n_axes], *output_shape))