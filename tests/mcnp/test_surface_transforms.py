import pyg4ometry.mcnp
import numpy as _np


def test_P_transform1():
    """
    general plane with normal (1,1,1) and translation of 5
    rotated 45 degrees about the y-axis, with no translation
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    P = pyg4ometry.mcnp.P(0, 1, 0, 5, reg=reg)
    Pp = P.transform(
        rotation=[
            [_np.cos(theta), 0.0, _np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-_np.sin(theta), 0.0, _np.cos(theta)],
        ],
        translation=[0, 0, 0],
    )
    print(Pp)


def test_PX_transform1():
    """
    x-plane rotated 45 degrees about the y-axis, with no translation
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
    PXp = PX.transform(
        rotation=[
            [_np.cos(theta), 0.0, _np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-_np.sin(theta), 0.0, _np.cos(theta)],
        ],
        translation=[0, 0, 0],
    )
    print(PXp)


def test_PX_transform2():
    """
    x-plane rotated 45 degrees about the y-axis, translated 10 in the +x direction
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
    PXp = PX.transform(
        rotation=[
            [_np.cos(theta), 0.0, _np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-_np.sin(theta), 0.0, _np.cos(theta)],
        ],
        translation=[10, 0, 0],
    )
    print(PXp)


def test_PX_transform3():
    """
    x-plane rotated 45 degrees about the y-axis, translated 10 in the +x
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
    PXp = PX.transform(
        rotation=[
            [_np.cos(theta), 0.0, _np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-_np.sin(theta), 0.0, _np.cos(theta)],
        ],
        translation=[0, 10, 0],
    )
    print(PXp)


def test_PX_transform4():
    """
    x-plane rotated 45 degrees about the y-axis,
    translated 10 in the +x and 10 in the +y direction (infinite plane so no change when doing y or z translations)
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
    PXp = PX.transform(
        rotation=[
            [_np.cos(theta), 0.0, _np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-_np.sin(theta), 0.0, _np.cos(theta)],
        ],
        translation=[10, 10, 0],
    )
    print(PXp)


def test_PX_transform5():
    """
    x-plane rotated 22.5 degrees about the y-axis, with no translation
    """
    theta = _np.pi / 8  # 22.5 degrees
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
    PXp = PX.transform(
        rotation=[
            [_np.cos(theta), 0.0, _np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-_np.sin(theta), 0.0, _np.cos(theta)],
        ],
        translation=[0, 0, 0],
    )
    print(PXp)


def test_PX_transform6():
    """
    x-plane rotated 25 degrees about the y-axis, with no translation
    """
    theta = _np.pi / 8  # 22.5 degrees
    reg = pyg4ometry.mcnp.Registry()
    PX = pyg4ometry.mcnp.PX(0, reg=reg)
    PXp = PX.transform(
        rotation=[
            [_np.cos(theta), -_np.sin(theta), 0.0],
            [_np.sin(theta), _np.cos(theta), 0.0],
            [0.0, 0.0, 1.0],
        ],
        translation=[0, 0, 0],
    )
    print(PXp)


def test_PY_transform1():
    """
    y-plane rotated 45 degrees about the z-axis, with no translation
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    PY = pyg4ometry.mcnp.PY(0, reg=reg)
    PYp = PY.transform(
        rotation=[
            [_np.cos(theta), -_np.sin(theta), 0.0],
            [_np.sin(theta), _np.cos(theta), 0.0],
            [0.0, 0.0, 1.0],
        ],
        translation=[0, 0, 0],
    )
    print(PYp)


def test_PZ_transform1():
    """
    z-plane rotated 45 degrees about the y-axis, with no translation
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    PZ = pyg4ometry.mcnp.PZ(0, reg=reg)
    PZp = PZ.transform(
        rotation=[
            [_np.cos(theta), 0.0, _np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-_np.sin(theta), 0.0, _np.cos(theta)],
        ],
        translation=[0, 0, 0],
    )
    print(PZp)


def test_PZ_transform2():
    """
    z-plane rotated 45 degrees about the x-axis, with no translation
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    PZ = pyg4ometry.mcnp.PZ(0, reg=reg)
    PZp = PZ.transform(
        rotation=[
            [1.0, 0.0, 0.0],
            [0.0, _np.cos(theta), -_np.sin(theta)],
            [0.0, _np.sin(theta), _np.cos(theta)],
        ],
        translation=[0, 0, 0],
    )
    print(PZp)


def test_BOX_transform1():
    """
    box centered at the origin with 3cm sides
    sides parallel to major axis rotated 45 degrees about the y-axis, with no translation
    """
    theta = _np.pi / 4  # 45 degrees
    reg = pyg4ometry.mcnp.Registry()
    BOX = pyg4ometry.mcnp.BOX(-2.5, -2.5, -2.5, 5, 0, 0, 0, 5, 0, 0, 0, 5, reg=reg)
    BOXp = BOX.transform(
        rotation=[
            [_np.cos(theta), 0.0, _np.sin(theta)],
            [0.0, 1.0, 0.0],
            [-_np.sin(theta), 0.0, _np.cos(theta)],
        ],
        translation=[0, 0, 0],
    )
    print(BOXp)
