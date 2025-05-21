import pyg4ometry.mcnp
import numpy as _np


def test_PX_transform1():
    """
    x-plane rotated 45 degrees about the y-axis, with no translation
    """
    PX = pyg4ometry.mcnp.PX(0)
    PXp = PX.transform(
        rotation=[
            [_np.cos(45), 0.0, _np.sin(45)],
            [0.0, 1.0, 0.0],
            [-_np.sin(45), 0.0, _np.cos(45)],
        ],
        translation=[0, 0, 0],
    )
    print(PXp)


def test_PX_transform2():
    """
    x-plane rotated 45 degrees about the y-axis, translated 10 in the +x direction
    """
    PX = pyg4ometry.mcnp.PX(0)
    PXp = PX.transform(
        rotation=[
            [_np.cos(45), 0.0, _np.sin(45)],
            [0.0, 1.0, 0.0],
            [-_np.sin(45), 0.0, _np.cos(45)],
        ],
        translation=[10, 0, 0],
    )
    print(PXp)


def test_PX_transform3():
    """
    x-plane rotated 45 degrees about the y-axis, translated 10 in the +x
    """
    PX = pyg4ometry.mcnp.PX(0)
    PXp = PX.transform(
        rotation=[
            [_np.cos(45), 0.0, _np.sin(45)],
            [0.0, 1.0, 0.0],
            [-_np.sin(45), 0.0, _np.cos(45)],
        ],
        translation=[0, 10, 0],
    )
    print(PXp)


def test_PX_transform4():
    """
    x-plane rotated 45 degrees about the y-axis,
    translated 10 in the +x and 10 in the +y direction (infinite plane so no change when doing y or z translations)
    """
    PX = pyg4ometry.mcnp.PX(0)
    PXp = PX.transform(
        rotation=[
            [_np.cos(45), 0.0, _np.sin(45)],
            [0.0, 1.0, 0.0],
            [-_np.sin(45), 0.0, _np.cos(45)],
        ],
        translation=[10, 10, 0],
    )
    print(PXp)


def test_PX_transform5():
    """
    x-plane rotated 25 degrees about the y-axis, with no translation
    """
    PX = pyg4ometry.mcnp.PX(0)
    PXp = PX.transform(
        rotation=[
            [_np.cos(25), 0.0, _np.sin(25)],
            [0.0, 1.0, 0.0],
            [-_np.sin(25), 0.0, _np.cos(25)],
        ],
        translation=[0, 0, 0],
    )
    print(PXp)


def test_PX_transform6():
    """
    x-plane rotated 25 degrees about the y-axis, with no translation
    """
    PX = pyg4ometry.mcnp.PX(0)
    PXp = PX.transform(
        rotation=[
            [_np.cos(45), -_np.sin(45), 0.0],
            [_np.sin(45), _np.cos(45), 0.0],
            [0.0, 0.0, 1.0],
        ],
        translation=[0, 0, 0],
    )
    print(PXp)


def test_PY_transform1():
    """
    y-plane rotated 45 degrees about the z-axis, with no translation
    """
    PY = pyg4ometry.mcnp.PY(0)
    PYp = PY.transform(
        rotation=[
            [_np.cos(45), -_np.sin(45), 0.0],
            [_np.sin(45), _np.cos(45), 0.0],
            [0.0, 0.0, 1.0],
        ],
        translation=[0, 0, 0],
    )
    print(PYp)


def test_PZ_transform1():
    """
    z-plane rotated 45 degrees about the y-axis, with no translation
    """
    PZ = pyg4ometry.mcnp.PZ(0)
    PZp = PZ.transform(
        rotation=[
            [_np.cos(45), 0.0, _np.sin(45)],
            [0.0, 1.0, 0.0],
            [-_np.sin(45), 0.0, _np.cos(45)],
        ],
        translation=[0, 0, 0],
    )
    print(PZp)


def test_PZ_transform2():
    """
    z-plane rotated 45 degrees about the x-axis, with no translation
    """
    PZ = pyg4ometry.mcnp.PZ(0)
    PZp = PZ.transform(
        rotation=[
            [1.0, 0.0, 0.0],
            [0.0, _np.cos(45), -_np.sin(45)],
            [0.0, _np.sin(45), _np.cos(45)],
        ],
        translation=[0, 0, 0],
    )
    print(PZp)
