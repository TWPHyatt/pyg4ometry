import pyg4ometry.mcnp
import numpy as _np


def test_P_transform1():
    """
    general plane with normal (1,1,1) and translation of 5
    rotated 45 degrees about the y-axis, with no translation
    """
    reg = pyg4ometry.mcnp.Registry()
    P = pyg4ometry.mcnp.P(0, 1, 0, 5, reg=reg)
    Pp = P.transform(
        rotation=[
            [_np.cos(45), 0.0, _np.sin(45)],
            [0.0, 1.0, 0.0],
            [-_np.sin(45), 0.0, _np.cos(45)],
        ],
        translation=[0, 0, 0],
    )
    print(Pp)


def test_PX_transform1():
    """
    x-plane rotated 45 degrees about the y-axis, with no translation
    """
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
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
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
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
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
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
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
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
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
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
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
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
    reg = pyg4ometry.mcnp.Registry()
    PY = pyg4ometry.mcnp.PY(0, reg=reg)
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
    reg = pyg4ometry.mcnp.Registry()
    PZ = pyg4ometry.mcnp.PZ(0, reg=reg)
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
    reg = pyg4ometry.mcnp.Registry()
    PZ = pyg4ometry.mcnp.PZ(0, reg=reg)
    PZp = PZ.transform(
        rotation=[
            [1.0, 0.0, 0.0],
            [0.0, _np.cos(45), -_np.sin(45)],
            [0.0, _np.sin(45), _np.cos(45)],
        ],
        translation=[0, 0, 0],
    )
    print(PZp)
