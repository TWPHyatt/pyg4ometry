import numpy as _np
import pytest

import pyg4ometry.mcnp

# surfaces


def test_Plane():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    print(surface)


def test_PlaneX():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.PX(1.1, reg=reg)
    print(surface)


def test_PlaneY():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.PY(1.2, reg=reg)
    print(surface)


def test_PlaneZ():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.PZ(1.3, reg=reg)
    print(surface)


def test_SphereO():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.SO(1.5, reg=reg)
    print(surface)


def test_Sphere():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.S(1.1, 1.2, 1.3, 1.5, reg=reg)
    print(surface)


def test_SphereX():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.SX(1.1, 1.5, reg=reg)
    print(surface)


def test_SphereY():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.SY(1.2, 1.5, reg=reg)
    print(surface)


def test_SphereZ():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.SZ(1.3, 1.5, reg=reg)
    print(surface)


def test_Cylinder_X():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.C_X(1.2, 1.3, 1.5, reg=reg)
    print(surface)


def test_Cylinder_Y():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.C_Y(1.1, 1.3, 1.5, reg=reg)
    print(surface)


def test_Cylinder_Z():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.C_Z(1.1, 1.2, 1.5, reg=reg)
    print(surface)


def test_CylinderX():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.CX(1.5, reg=reg)
    print(surface)


def test_CylinderY():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.CY(1.5, reg=reg)
    print(surface)


def test_CylinderZ():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.CZ(1.5, reg=reg)
    print(surface)


def test_Cone_X():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.K_X(1.1, 1.2, 1.3, 25, -1, reg=reg)
    print(surface)


def test_Cone_Y():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.K_Y(1.1, 1.2, 1.3, 25, -1, reg=reg)
    print(surface)


def test_Cone_Z():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.K_Z(1.1, 1.2, 1.3, 25, -1, reg=reg)
    print(surface)


def test_ConeX():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.KX(1.1, 25, -1, reg=reg)
    print(surface)


def test_ConeY():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.KY(1.2, 25, -1, reg=reg)
    print(surface)


def test_ConeZ():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.KY(1.3, 25, -1, reg=reg)
    print(surface)


# ...

# macrobody surfaces


def test_BOX():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.BOX(-1, -1, -1, 2, 0, 0, 0, 2, 0, 0, 0, 2, reg=reg)
    print(surface)


def test_RPP():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RPP(-1, 10, -1, 2, -20, 20, reg=reg)
    print(surface)


def test_SPH():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.XYZ(0, 4, 5, 5, reg=reg)
    print(surface)


def test_RCC1():
    """
    RCC about the y-axis
    base plane at x,y,z = 0,-5,0
    height of 10 and radius of 4
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RCC(0, -5, 0, 0, 10, 0, 4, reg=reg)
    print(surface)


def test_RCC2():
    """
    RCC rotated
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RCC(0, 0, 2, 3, 4, 0, 2, reg=reg)  # rotation
    print(surface)


def test_RHP_HEX1():
    """
    RHP (regular) about the z-axis
    base plane is at x,y,z = 0,0,0
    height of 8 and 1st face is normal to y-axis at y=2
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RHP_HEX(0, 0, 0, 0, 0, 8, 0, 2, 0, reg=reg)
    print(surface)


def test_RHP_HEX2():
    """
    RHP (regular) about the z-axis
    base plane is at x,y,z = 5,5,-4
    height of 8 and 1st face is normal to y-axis at y=2
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RHP_HEX(5, 5, -4, 0, 0, 8, 0, 2, 0, reg=reg)
    print(surface)


def test_RHP_HEX3():
    """
    RHP (regular) about the z-axis
    base plane is at x,y,z = 0,0,0
    height of 8 and 1st face is normal to y-axis at y=2
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RHP_HEX(0, 0, 0, 0, 8, 0, 2, 0, 0, reg=reg)
    print(surface)


def test_RHP_HEX4():
    """
    RHP (regular) rotated to be at 45 degrees between the z-axis and y-axis
    base plane is at x,y,z = 0,0,-4
    height of sqrt(2)*5.66=8.00 and 1st face is normal to y-axis at y=2
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RHP_HEX(0, 0, -4, 0, 5.66, 5.66, 0, 2, 0, reg=reg)
    print(surface)


def test_RHP_HEX5():
    """
    RHP (regular) rotated to be at a 22.5 degrees from the x-axis to the z-axis
    base plan at x,y,z = 0,0,0
    height of = [15cos(22.5), 0, 12sine(22.5)] = [13.85, 0, 5.74] = sqrt(13.85**2 + 0**2 + 5.74**2) = 14.99
    and 1st face is normal to the x-axis at x = [6-5, 0, 0] = [1, 0, 0]
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RHP_HEX(0, 0, 0, 0, 16.98, 16.98, 0, 4, 0, reg=reg)
    print(surface)


def test_RHP_HEX6():
    """
    RHP (regular) about the z-axis
    base plane is at x,y,z = 0,0,-4
    height of 15 and 1st face is normal to y-axis at y=2
    the s and t values form a regular hexagon
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RHP_HEX(
        0, 0, -4, 0, 0, 15, 0, 2, 0, 1.732, 1, 0, -1.732, 1, 0, reg=reg
    )
    print(surface)


def test_RHP_HEX7():
    """
    RHP (non-regular) about the z-axis
    base plane is at x,y,z = 0,0,0
    height of 5 and 1st face is normal to x-axis at x=2
    the s and t values form a non-regular hexagon in the xy plane
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.RHP_HEX(0, 0, 0, 0, 0, 5, 2, 0, 0, 1, 2, 0, -1, 2, 0, reg=reg)
    print(surface)


def test_REC():
    """
    REC about the y-axis
    centre of the base plane is at x,y,z = 0,-5,0
    major radius = 4 in the x-direction
    minor radius = 2 in the z-direction
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.REC(0, -5, 0, 0, 10, 0, 4, 0, 0, 2, reg=reg)
    print(surface)


# def test_REC():
#    reg = pyg4ometry.mcnp.Registry()
#    surface = pyg4ometry.mcnp.REC(, reg=reg)
#    print(surface)


# def test_REC():
#    reg = pyg4ometry.mcnp.Registry()
#    surface = pyg4ometry.mcnp.REC(, reg=reg)
#    print(surface)


def test_TRC():
    """
    TRC about the x-axis
    centre of the base plane is at x,y,z = -5,0,0
    top radius = 4 at x,y,z = -5,0,0
    bottom radius = 2 at x,y,z = 5,0,0
    """
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.TRC(-5, 0, 0, 10, 0, 0, 4, 2, reg=reg)
    print(surface)


# def test_TRC():
#    reg = pyg4ometry.mcnp.Registry()
#    surface = pyg4ometry.mcnp.TRC(, reg=reg)
#    print(surface)


# def test_TRC():
#    reg = pyg4ometry.mcnp.Registry()
#    surface = pyg4ometry.mcnp.TRC(, reg=reg)
#    print(surface)

"""
def test_ELL():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.ELL(, reg=reg)
    print(surface)

def test_WED():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.WED(, reg=reg)
    print(surface)

def test_ARB():
    reg = pyg4ometry.mcnp.Registry()
    surface = pyg4ometry.mcnp.ARB(, reg=reg)
    print(surface)
"""
