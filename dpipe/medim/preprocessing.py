from typing import Sequence, Union

import numpy as np
from scipy import ndimage

from dpipe.medim.patch import pad
from dpipe.medim.shape_utils import compute_shape_from_spatial
from dpipe.medim.utils import get_axes, build_slices


def normalize_scan(scan, mean=True, std=True, drop_percentile: int = None):
    """Normalize scan to make mean and std equal to (0, 1) if stated.
    Supports robust estimation with drop_percentile."""
    if drop_percentile is not None:
        bottom = np.percentile(scan, drop_percentile)
        top = np.percentile(scan, 100 - drop_percentile)

        mask = (scan > bottom) & (scan < top)
        vals = scan[mask]
    else:
        vals = scan.flatten()

    assert vals.ndim == 1

    if mean:
        scan = scan - vals.mean()

    if std:
        scan = scan / vals.std()

    return np.array(scan, dtype=np.float32)


def normalize_mscan(mscan, mean=True, std=True, drop_percentile: int = None):
    """Normalize multimodal scan (each modality independently) to make mean and std equal to (0, 1) if stated.
    Supports robust estimation with drop_percentile."""
    new_mscan = np.zeros_like(mscan, dtype=np.float32)
    for i in range(len(mscan)):
        new_mscan[i] = normalize_scan(mscan[i], mean=mean, std=std,
                                      drop_percentile=drop_percentile)
    return new_mscan


def rotate_image(image: np.ndarray, angles: Sequence, axes: Sequence = None, order: int = 1, reshape=False):
    """
    Rotate an image along the given axes.

    Parameters
    ----------
    image: np.ndarray
        image to rotate
    angles: Sequence
    axes: Sequence
        axes along which the image will be rotated. The length must be equal to len(angles) + 1
    order: int, optional
        interpolation order
    reshape: bool, optional
        whether to reshape the resulting image

    Returns
    -------
    rotated_image: np.ndarray
    """
    axes = get_axes(axes, len(angles) + 1)
    assert len(axes) == len(angles) + 1
    result = image.copy()
    for angle, *axis in zip(angles, axes, axes[1:]):
        result = ndimage.rotate(result, angle, axes=axis, reshape=reshape, order=order)
    return result


def scale_to_shape(x: np.ndarray, shape: Sequence, axes: Sequence = None, order: int = 1) -> np.ndarray:
    """
    Rescale a tensor to `shape` along the `axes`.

    Parameters
    ----------
    x: np.ndarray
        tensor to rescale
    shape: Sequence
        final tensor shape
    axes: Sequence, optional
        axes along which the tensor will be scaled.
        If None - the last `len(shape)` axes are used.
    order: int, optional
        order of interpolation

    Returns
    -------
    scaled_tensor: np.ndarray
    """
    old_shape = np.array(x.shape, 'float64')
    new_shape = np.array(compute_shape_from_spatial(x.shape, shape, axes), 'float64')

    return ndimage.zoom(x, new_shape / old_shape, order=order)


def pad_to_shape(x: np.ndarray, shape: Sequence, axes: Sequence = None,
                 padding_values: Union[float, Sequence] = 0) -> np.ndarray:
    """
    Pad a tensor to `shape` along the `axes`.

    Parameters
    ----------
    x: np.ndarray
        tensor to pad.
    shape: Sequence
        final tensor shape.
    padding_values: Sequence
        values to pad the tensor with.
    axes: Sequence, optional
        axes along which the tensor will be padded.
        If None - the last `len(shape)` axes are used.

    Returns
    -------
    padded_tensor: np.ndarray
    """
    old_shape, new_shape = np.array(x.shape), np.array(compute_shape_from_spatial(x.shape, shape, axes))
    if (old_shape > new_shape).any():
        raise ValueError(f'The resulting shape cannot be smaller than the original: {old_shape} vs {new_shape}')

    delta = new_shape - old_shape
    padding_width = np.array((delta // 2, (delta + 1) // 2)).T.astype(int)

    return pad(x, padding_width, padding_values)


def slice_to_shape(x: np.ndarray, shape: Sequence, axes: Sequence = None) -> np.ndarray:
    """
    Slice a tensor to `shape` along the `axes`.

    Parameters
    ----------
    x: np.ndarray
        tensor to pad
    shape: Sequence
        final tensor shape
    axes: Sequence, optional
        axes along which the tensor will be padded.
        If None - the last `len(shape)` axes are used.

    Returns
    -------
    sliced_tensor: np.ndarray
    """
    old_shape, new_shape = np.array(x.shape), np.array(compute_shape_from_spatial(x.shape, shape, axes))
    if (old_shape < new_shape).any():
        raise ValueError(f'The resulting shape cannot be greater than the original: {old_shape} vs {new_shape}')

    start = ((old_shape - new_shape) // 2).astype(int)
    return x[build_slices(start, start + new_shape)]
