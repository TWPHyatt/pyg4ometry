import numpy as _np
import pyg4ometry.pycgal.Polygon_mesh_processing
import sympy as _sp

from .Transformation import TR
from ..pycgal.Point_3 import Point_3_ECER as _Point_3_ECER
from ..pycgal.Vector_3 import Vector_3_ECER as _Vector_3_ECER
from ..pycgal.Plane_3 import Plane_3_ECER as _Plane_3_ECER
from ..pycgal.Nef_polyhedron_3 import Nef_polyhedron_3_ECER as _Nef_polyhedron_3_ECER
from ..pycgal.Polyhedron_3 import Polyhedron_3_ECER as _Polyhedron_3_ECER
from ..pycgal import Surface_mesh as _Surface_mesh
from ..pycgal.Surface_mesh import Surface_mesh_ECER as _Surface_mesh_ECER
from ..pycgal.Surface_mesh import Surface_mesh_EPECK as _Surface_mesh_EPECK
from ..pycgal.CGAL import copy_face_graph as _copy_face_graph
from ..pycgal.core import CSG as _CSG

# for mesh()
from ..geant4.Registry import Registry as g4Reg
from ..geant4.solid import Orb
from ..geant4.solid import EllipticalTube
from ..geant4.solid import EllipticalCone
from ..geant4.solid import Torus
from ..transformation import matrix2axisangle

inf = 1e2


class Intersection:
    """
    mcnp : blank space between two surface numbers
    pyg4 : asterisk
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toOutputString(self):
        # if union downstream add parentheses (also read as an intersection like a " ")
        if isinstance(self.right, Union) and isinstance(self.left, Union):
            return "(" + self.left.toOutputString() + ") (" + self.right.toOutputString() + ")"
        elif isinstance(self.right, Union):
            return self.left.toOutputString() + " (" + self.right.toOutputString() + ")"
        elif isinstance(self.left, Union):
            return "(" + self.left.toOutputString() + ") " + self.right.toOutputString()
        else:
            return self.left.toOutputString() + " " + self.right.toOutputString()

    def mesh(self):
        # print(f" > i {type(self.left)} {type(self.right)}")
        return self.left.mesh().intersect(self.right.mesh())


class Union:
    """
    mcnp : colon
    pyg4 : plus
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toOutputString(self):
        return self.left.toOutputString() + ":" + self.right.toOutputString()

    def mesh(self):
        # print(f" > u {type(self.left)} {type(self.right)}")
        return self.left.mesh().union(self.right.mesh())


class Complement:
    """
    mcnp : hyphen for surface, hash for cell
    pyg4 : exclamation mark
    """

    def __init__(self, item):
        self.item = item

    def toOutputString(self):
        if isinstance(self.item, Surface):
            return "-" + str(self.item.surfaceNumber)
        elif isinstance(self.item, pyg4ometry.mcnp.Cell):
            return "#" + str(self.item.cellNumber)
        else:
            return "#(" + self.item.toOutputString() + ")"

    def mesh(self):
        # print(f" > c {type(self.item)}")
        mesh = self.item.mesh()
        bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        return bigBox.subtract(mesh)


class Surface:
    def __init__(self, reg=None, surfaceNumber=None, transformation=None):
        self.surfaceNumber = surfaceNumber
        self.transformation = transformation
        self.reg = reg
        if self.reg:
            reg.addSurface(self)

    def toOutputString(self):
        return str(self.surfaceNumber)

    def transform(
        self,
        rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        translation=[0, 0, 0],
        angles=False,
    ):
        """
        transform surface
        """

        TR1 = TR(
            *translation, *rotation[0], *rotation[1], *rotation[2], angles=angles, reg=self.reg
        )
        if self.reg:
            self.reg.addTransformation(TR1)

        if self.transformation:
            self.transformation.compositeTR(TR1)
        else:
            self.transformation = TR1

    def _rotationAboutAxis(self, a, b):
        a = a / _np.linalg.norm(a)
        b = b / _np.linalg.norm(b)

        # print("a: ", a)
        # print("b: ", b)

        axisIn = _np.cross(a, b)  # rotation axis
        axisInNorm = _np.linalg.norm(axisIn)
        # print("cross: ", axisIn)
        # print("cross norm", axisInNorm)

        dotProduct = _np.dot(a, b)
        angleRad = _np.arccos(dotProduct)
        angleDeg = _np.degrees(angleRad)
        # print("dot: ", dotProduct)
        # print("rad: ", axisInNorm)
        # print("deg: ", angleDeg)

        # print("return...")
        if axisInNorm < 1e-9:  # a and b vectors are aligned or opposite
            if dotProduct > 0:  # no rotation needed
                axisIn = _np.array([1, 0, 0])
                # print("Axis: ", axisIn, " Deg: ", angleDeg)
                return axisIn, 0.0
            else:  # 180-degree rotation to axis
                # a and b are opposite
                # need a perpendicular rotation axis
                # so find any vector perpendicular to a
                perp = _np.zeros(3)
                minIndex = _np.argmin(_np.abs(a))  # component with smallest magnitude
                perp[minIndex] = 1.0
                axisIn = _np.cross(a, perp)
                axisIn = axisIn / _np.linalg.norm(axisIn)
                # print("Axis: ", axisIn, " Deg: ", angleDeg)
                return axisIn, 180.0
        else:
            axisIn = axisIn / axisInNorm

        # print("Axis: ", axisIn, " Deg: ", angleDeg)
        return axisIn, angleDeg


class SurfaceSolve(Surface):
    def __init__(self, coordNum):
        super().__init__()
        self.numPoints = coordNum

    def _quadSolve(axis, points):
        """
        Solves for the coefficients A, B, C, D, E, F, G, x', y', z' of the SQ quadratic surface equation
        Returns coefficients {A, B, C, D, E, F, G, x', y', z'}
        SQ: A(x-x')^2 + B(y-y')^2  + C(z-z')^2 + 2D(x-x') + 2E(y-y') + 2F(z-z') + G = 0
        """

        (x1, r1), (x2, r2), (x3, r3) = points

        # construct matrix equations
        M = _np.array([[x1**2, x1, 1], [x2**2, x2, 1], [x3**2, x3, 1]])
        rhs = _np.array([r1**2, r2**2, r3**2])

        # solve for coefficients
        Aprime, Bprime, Cprime = _np.linalg.solve(M, rhs)

        # print(Aprime, Bprime, Cprime)

        A, B, C, D, E, F, G = 1, 1, 1, 0, 0, 0, 0

        # coefficients based on axis
        if axis == "X":
            Xprime = -Bprime / (2 * Aprime)
            Yprime, Zprime = 0, 0
            G = Aprime * (Xprime**2) - Cprime + (Bprime * Xprime)
            A = -Aprime
            D = 2 * Aprime * Xprime + Bprime
        elif axis == "Y":
            Yprime = -Bprime / (2 * Aprime)
            Xprime, Zprime = 0, 0
            G = Aprime * (Yprime**2) - Cprime + (Bprime * Yprime)
            B = -Aprime
            E = 2 * Aprime * Yprime + Bprime
        elif axis == "Z":
            Zprime = -Bprime / (2 * Aprime)
            Xprime, Yprime = 0, 0
            G = Aprime * (Zprime**2) - Cprime + (Bprime * Zprime)
            C = -Aprime
            F = 2 * Aprime * Zprime + Bprime
        else:
            msg = "Axis must be X, Y, or Z"
            raise ValueError(msg)

        result = {
            "A": A,
            "B": B,
            "C": C,
            "D": D,
            "E": E,
            "F": F,
            "G": G,
            "x*": Xprime,
            "y*": Yprime,
            "z*": Zprime,
        }

        return result

    def _sphereSolve(self, pi, ri):
        r0, p0 = _sp.symbols("r0 p0")  # center of the sphere (to find)
        payload = []

        if self.numPoints == 3:
            r1, r2, r3 = ri[0], ri[1], ri[2]
            p1, p2, p3 = pi[0], pi[1], pi[2]
            points = [(r1, p1), (r2, p2), (r3, p3)]
            # sphere equation (r - r0)^2 + (z - z0)^2 = R^2
            eq1 = (r1 - r0) ** 2 + (p1 - p0) ** 2  # (1) sphere eq for z1 r1
            eq2 = (r2 - r0) ** 2 + (p2 - p0) ** 2  # (2) sphere eq for z2 r2
            eq3 = (r3 - r0) ** 2 + (p3 - p0) ** 2  # (3) sphere eq for z3 r3

            # subtract equations (2) - (1) & (3) - (1), and solve for r0 z0
            solution = _sp.solve([eq2 - eq1, eq3 - eq1], (r0, p0))
            r0, z0 = solution[r0], solution[p0]
            R = _sp.sqrt(eq1.subs(solution))

            is_sphere = all(
                _sp.simplify((r - r0) ** 2 + (z - z0) ** 2 - R**2) == 0 for r, z in points
            )

            if is_sphere:
                payload = [r0, p0, R]
                return True, payload
            else:
                return False, payload

        else:
            msg = "invalid number of coordinate points for cone"
            raise TypeError(msg)

    def _coneSolve(self, pi, ri):
        k, p0 = _sp.symbols("k p0")  # Slope and vertex height
        r1, r2 = ri[0], ri[1]
        p1, p2 = pi[0], pi[1]
        points = [(r1, p1), (r2, p2)]
        sheet = 0

        # cone equation z^2 = x^2 + y^2
        # in cylindrical coords
        # cone equations r = k(z - z0) k->slope & z0 height of vertex
        eq1 = r1**2 - k**2 * (p1 - p0) ** 2
        eq2 = r2**2 - k**2 * (p2 - p0) ** 2

        if self.numPoints == 2:
            # Solve for k and z0
            solution = _sp.solve([eq2 - eq1], (k, p0))

        elif self.numPoints == 3:
            r3 = ri[2]
            p3 = pi[2]
            points.append((r3, p3))
            eq3 = r3**2 - k**2 * (p3 - p0) ** 2

            # Solve for k and z0
            solution = _sp.solve([eq2 - eq1, eq3 - eq1], (k, p0))

        else:
            msg = "invalid number of coordinate points for cone"
            raise TypeError(msg)

        # print("cone solutions:", solution)

        if not all(j.is_real for i in solution for j in i):
            return False, []
        else:
            if len(solution) > 1:
                # testing the k solution values
                if solution[0][0] > 0 and solution[1][0] < 0:
                    # solution[0] -> positive slope
                    sheet = 1
                    k, p0 = solution[0][0], solution[0][1]
                elif solution[1][0] > 0 and solution[0][0] < 0:
                    # solution[1] -> negative slope
                    sheet = -1
                    k, p0 = solution[1][0], solution[1][1]
                else:
                    msg = (
                        "error: multiple cone solutions and the slopes are not one +ve and one -ve"
                    )
                    raise TypeError(msg)
            else:
                msg = "only one solution to the cone exists"
                raise TypeError(msg)

            # Validate the solution for all coordinate pairs
            tolerance = (
                1e-6  # equation should = 0 but floating point precision so using tolerance of 1e-6
            )
            isCone = all(
                abs(_sp.simplify(r**2 - k**2 * (p - p0) ** 2).evalf()) < tolerance
                for r, p in points
            )

            if isCone:
                # print(f"Points lie on a cone with slope k={k} and vertex at p0={p0}")
                return True, [p0, k, sheet]

            else:
                # print("Points do not lie on a cone.")
                return False, []

    def _surfaceFromPoints(self, axis, pi, ri):
        """ """
        if axis != "x" and axis != "y" and axis != "z":
            msg = "axis can only be x, y, or z"
            raise TypeError(msg)

        # one coordinate pair
        if self.numPoints == 1:
            # print("1 coordinate pair")
            p1 = pi[0]  # distance from axis to plane
            if axis == "x":
                # print("> x plane")
                return PX(D=p1)  # x plane
            elif axis == "y":
                # print("> y plane")
                return PY(D=p1)  # y plane
            elif axis == "z":
                # print("> z plane")
                return PZ(D=p1)  # z plane

        # two coordinate pairs
        elif self.numPoints == 2:
            # print("2 coordinate pairs")
            r1, r2 = ri[0], ri[1]
            p1, p2 = pi[0], pi[1]
            if p1 == p2:
                if axis == "x":
                    # print("> x plane")
                    return PX(D=p1)  # x plane
                elif axis == "y":
                    # print("> y plane")
                    return PY(D=p1)  # y plane
                elif axis == "z":
                    # print("> z plane")
                    return PZ(D=p1)  # z plane
            elif r1 == r2:
                if axis == "x":
                    # print("> x cylinder")
                    return CX(R=r1)  # x cylinder
                elif axis == "y":
                    # print("> y cylinder")
                    return CY(R=r1)  # y cylinder
                elif axis == "z":
                    # print("> z cylinder")
                    return CZ(R=r1)  # z cylinder
            else:  # r1 != r2
                isCone, data = self._coneSolve(pi, ri)
                if isCone:
                    if axis == "x":
                        # print("> x cone")
                        return KX(x=data[0], t_sqr=data[1] ** 2, sign=data[2])  # x cone
                    elif axis == "y":
                        # print("> y cone")
                        return KY(y=data[0], t_sqr=data[1] ** 2, sign=data[2])  # y cone
                    elif axis == "z":
                        # print("> z cone")
                        return KZ(z=data[0], t_sqr=data[1] ** 2, sign=data[2])  # z cone
                else:
                    msg = "could not find a surface for two coordinate pairs"
                    raise TypeError(msg)

        # three coordinate pairs
        elif self.numPoints == 3:
            isCone = False
            isSphere = False
            # print("3 coordinate pairs")
            r1, r2, r3 = ri[0], ri[1], ri[2]
            p1, p2, p3 = pi[0], pi[1], pi[2]
            # print("is cone?")
            isCone, data = self._coneSolve(pi, ri)
            # print(isCone)
            if not isCone:
                # print("is sphere?")
                isSphere, data = self._sphereSolve(pi, ri)
                # print(isSphere)
            if p1 == p2 == p3:
                if axis == "x":
                    # print("> x plane")
                    return PX(D=p1)  # x plane
                elif axis == "y":
                    # print("> y plane")
                    return PY(D=p1)  # y plane
                elif axis == "z":
                    # print("> z plane")
                    return PZ(D=p1)  # z plane
            elif r1 == r2 == r3:
                if axis == "x":
                    # print("> x cylinder")
                    return CX(R=r1)  # x cylinder
                elif axis == "y":
                    # print("> y cylinder")
                    return CY(R=r1)  # y cylinder
                elif axis == "z":
                    # print("> z cylinder")
                    return CZ(R=r1)  # z cylinder
            elif isCone:
                if axis == "x":
                    # print("> x cone")
                    return KX(x=data[0], t_sqr=data[1] ** 2, sign=data[2])  # x cone
                elif axis == "y":
                    # print("> y cone")
                    return KY(y=data[0], t_sqr=data[1] ** 2, sign=data[2])  # y cone
                elif axis == "z":
                    # print("> z cone")
                    return KZ(z=data[0], t_sqr=data[1] ** 2, sign=data[2])  # z cone
            elif isSphere:
                if data[1] == 0:
                    return SO(R=data[2])  # sphere centered at origin
                else:
                    if axis == "x":
                        # print("> x sphere")
                        return SX(x=data[0], R=data[2])  # x sphere
                    elif axis == "y":
                        # print("> y sphere")
                        return SY(y=data[0], R=data[2])  # y sphere
                    elif axis == "z":
                        # print("> z sphere")
                        return SZ(z=data[0], R=data[2])  # z sphere
            else:
                # print("> quadratic...")
                coeffs = self._quadSolve(axis)

                # print(
                #    f'A {coeffs["A"]} B {coeffs["B"]} C {coeffs["C"]} \n'
                #    f'D {coeffs["D"]} E {coeffs["E"]} F {coeffs["F"]} \n'
                #    f'G {coeffs["F"]}'
                # )
                msg = "Quadratic equations from surface point definitions not yet fully implemented"
                raise TypeError(msg)
                # todo
                """
                # if A B positive -> Ellipsoid
                if A > 0 and B > 0:
                    print("> Ellipsoid")
                # if A B C have mixed signed -> Hyperboloid
                if not (all(v > 0 for v in [A, B, C]) or all(v < 0 for v in [A, B, C])):  # A B C have mixed signed
                    print("> Hyperboloid")
                # if equation reduces to r^2 = ap + b -> paraboloid
                if B == 0 and C == 0 and D < 0 and E == 0:
                    print("> Paraboloid")

                # Alternative method, general quadratic equation Ax^2 + By^2 + Cz^2 + Dxy + Exz ...
                # and classify the surface based on eigenvalues of its quadratic coefficient matrix.
                """
        # number of coordinate pair(s) < 1 or > 3 invalid
        else:
            msg = f"invalid number of coordinate points for surface: {self.numPoints}"
            raise TypeError(msg)


class X(SurfaceSolve):
    """
    Surface Point for a surface symmetric about the x-axis
    Used to describe surfaces by coordinate points rather
    than by equation coefficients.
    """

    def __init__(self, *coordinatePairs, reg=None, surfaceNumber=None):
        super().__init__(len(coordinatePairs))
        self.xi = []  # coordinate of point i
        self.ri = []  # ri = sqrt((yi**2 + zi**2)**2)
        for i in coordinatePairs:
            if not isinstance(i, tuple):
                errorString = (
                    "every coordinate pair should be specified in a tuple: (x1,r1), (x2,r2), ..."
                )
                raise TypeError(errorString)
            if not len(i) == 2:
                errorString = "every coordinate pair needs x and r: (xi,ri)"
                raise TypeError(errorString)
            self.xi.append(i[0])
            self.ri.append(i[1])

    def __repr__(self):
        return "X " + " ".join(f"{x} {r}" for x, r in zip(self.xi, self.ri))

    def mesh(self):
        solid = self._surfaceFromPoints("x", self.xi, self.ri)
        mesh = solid.mesh()
        return mesh


class Y(SurfaceSolve):
    """
    Surface Point for a surface symmetric about the y-axis
    Used to describe surfaces by coordinate points rather
    than by equation coefficients.
    """

    def __init__(self, *coordinatePairs, reg=None, surfaceNumber=None):
        super().__init__(len(coordinatePairs))
        self.yi = []  # coordinate of point i
        self.ri = []  # ri = sqrt((yi**2 + zi**2)**2)
        for i in coordinatePairs:
            if not isinstance(i, tuple):
                errorString = (
                    "every coordinate pair should be specified in a tuple: (y1,r1), (y2,r2), ..."
                )
                raise TypeError(errorString)
            if not len(i) == 2:
                errorString = "every coordinate pair needs y and r: (yi,ri)"
                raise TypeError(errorString)
            self.yi.append(i[0])
            self.ri.append(i[1])

    def __repr__(self):
        return "Y " + " ".join(f"{y} {r}" for y, r in zip(self.yi, self.ri))

    def mesh(self):
        solid = self._surfaceFromPoints("y", self.yi, self.ri)
        mesh = solid.mesh()
        return mesh


class Z(SurfaceSolve):
    """
    Surface Point for a surface symmetric about the z-axis
    Used to describe surfaces by coordinate points rather
    than by equation coefficients.
    """

    def __init__(self, *coordinatePairs, reg=None, surfaceNumber=None):
        super().__init__(len(coordinatePairs))
        self.zi = []  # coordinate of point i
        self.ri = []  # ri = sqrt((yi**2 + zi**2)**2)
        for i in coordinatePairs:
            if not isinstance(i, tuple):
                msg = "every coordinate pair should be specified in a tuple: (z1,r1), (z2,r2), ..."
                raise TypeError(msg)
            if not len(i) == 2:
                msg = "every coordinate pair needs y and r: (zi,ri)"
                raise TypeError(msg)
            self.zi.append(i[0])
            self.ri.append(i[1])

    def __repr__(self):
        return "Z " + " ".join(f"{z} {r}" for z, r in zip(self.zi, self.ri))

    def mesh(self):
        solid = self._surfaceFromPoints("z", self.zi, self.ri)
        mesh = solid.mesh()
        return mesh


class P(Surface):
    """
    Plane (general)
    """

    def __init__(self, A, B, C, D, reg=None, surfaceNumber=None):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"P {self.A} {self.B} {self.C} {self.D}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)

        # plane
        normal = _np.array([self.A, self.B, self.C])  # normal vector
        D = self.D

        if _np.array_equal(rotation, _np.eye(rotation.shape[0])):
            # no rotation
            if _np.array_equal(translation, _np.array([0, 0, 0])):
                # no translation
                return self
            else:
                # translation only
                # transformed plane (prime)
                unitNormal = normal / _np.linalg.norm(normal)  # unit normal
                point = self.D * unitNormal
                point_p = point + translation
                D_p = normal @ point_p

                # new surface (prime)
                s_p = P(self.A, self.B, self.C, D_p)
                s_p.surfaceNumber = self.surfaceNumber

                return s_p

        else:  # rotation and possibly translation
            # transformed plane (prime)
            unitNormal = normal / _np.linalg.norm(normal)  # unit normal
            point = self.D * unitNormal

            normal_p = rotation @ unitNormal
            point_p = rotation @ point + translation
            D_p = normal_p @ point_p

            # new surface (prime)
            s_p = P(normal_p[0], normal_p[1], normal_p[2], D_p)
            s_p.surfaceNumber = self.surfaceNumber

            return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
            s = s_p
        else:
            s = self

        # print(f"surface plane mesh")
        n1 = _Nef_polyhedron_3_ECER(
            _Plane_3_ECER(_Point_3_ECER(0, 0, inf), _Vector_3_ECER(0, 0, 1))
        )
        n2 = _Nef_polyhedron_3_ECER(
            _Plane_3_ECER(_Point_3_ECER(0, 0, -inf), _Vector_3_ECER(0, 0, -1))
        )
        n3 = _Nef_polyhedron_3_ECER(
            _Plane_3_ECER(_Point_3_ECER(0, inf, 0), _Vector_3_ECER(0, 1, 0))
        )
        n4 = _Nef_polyhedron_3_ECER(
            _Plane_3_ECER(_Point_3_ECER(0, -inf, 0), _Vector_3_ECER(0, -1, 0))
        )
        n5 = _Nef_polyhedron_3_ECER(
            _Plane_3_ECER(_Point_3_ECER(inf, 0, 0), _Vector_3_ECER(1, 0, 0))
        )
        n6 = _Nef_polyhedron_3_ECER(
            _Plane_3_ECER(_Point_3_ECER(-inf, 0, 0), _Vector_3_ECER(-1, 0, 0))
        )

        mag = _np.sqrt(s.A**2 + s.B**2 + s.C**2)
        n7 = _Nef_polyhedron_3_ECER(
            _Plane_3_ECER(
                _Point_3_ECER(s.A / mag * s.D, s.B / mag * s.D, s.C / mag * s.D),
                _Vector_3_ECER(-s.A / mag, -s.B / mag, -s.C / mag),
            )
        )

        n = n1 * n2 * n3 * n4 * n5 * n6 * n7

        p = _Polyhedron_3_ECER()
        n.convert_to_polyhedron(p)

        sm_ecer = _Surface_mesh_ECER()
        sm_epeck = _Surface_mesh_EPECK()

        _copy_face_graph(p, sm_ecer)
        _Surface_mesh.toCGALSurfaceMesh(sm_epeck, sm_ecer)

        mesh = _CSG(sm_epeck)

        return mesh


class PX(Surface):
    """
    Plane (normal to x-axis)
    """

    def __init__(self, D, reg=None, surfaceNumber=None):
        self.D = D
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"PX {self.D}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)
        normal = _np.array([1, 0, 0])  # PX normal

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        # rotate the normal
        normal_p = rotation @ normal
        unitNormal_p = normal_p / _np.linalg.norm(normal_p)

        # point on original plane
        p0 = self.D * normal
        p0_p = rotation @ p0 + translation

        D_p = unitNormal_p @ p0_p

        # new surface (prime)
        s_p = P(*unitNormal_p, D_p)
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            s_p = P(A=1, B=0, C=0, D=self.D)
        mesh = s_p.mesh()
        return mesh


class PY(Surface):
    """
    Plane (normal to y-axis)
    """

    def __init__(self, D, reg=None, surfaceNumber=None):
        self.D = D
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"PY {self.D}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)
        normal = _np.array([0, 1, 0])  # PY normal

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        # rotate the normal
        normal_p = rotation @ normal
        unitNormal_p = normal_p / _np.linalg.norm(normal_p)

        # point on original plane
        p0 = self.D * normal
        p0_p = rotation @ p0 + translation

        D_p = unitNormal_p @ p0_p

        # new surface (prime)
        s_p = P(*unitNormal_p, D_p)
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            s_p = P(A=0, B=1, C=0, D=self.D)
        mesh = s_p.mesh()
        return mesh


class PZ(Surface):
    """
    Plane (normal to z-axis)
    """

    def __init__(self, D, reg=None, surfaceNumber=None):
        self.D = D
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"PZ {self.D}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)
        normal = _np.array([0, 0, 1])  # PZ normal

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        # rotate the normal
        normal_p = rotation @ normal
        unitNormal_p = normal_p / _np.linalg.norm(normal_p)

        # point on original plane
        p0 = self.D * normal
        p0_p = rotation @ p0 + translation

        D_p = unitNormal_p @ p0_p

        # new surface (prime)
        s_p = P(*unitNormal_p, D_p)
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            s_p = P(A=0, B=0, C=1, D=self.D)
        mesh = s_p.mesh()
        return mesh


class SO(Surface):
    """
    Sphere (centered at origin)
    """

    def __init__(self, R, reg=None, surfaceNumber=None):
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"SO {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        s_p = S(x=translation[0], y=translation[1], z=translation[2], R=self.R)
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            reg = g4Reg()
            s_p = Orb(
                name="",
                pRMax=self.R,
                registry=reg,
            )
        mesh = s_p.mesh()
        # bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        # mesh = bigBox.subtract(mesh)
        return mesh


class S(Surface):
    """
    Sphere (general)
    """

    def __init__(self, x, y, z, R, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"S {self.x} {self.y} {self.z} {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        s_p = S(x=translation[0], y=translation[1], z=translation[2], R=self.R)
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            reg = g4Reg()
            s_p = Orb(
                name="",
                pRMax=self.R,
                registry=reg,
            )

        mesh = s_p.mesh()
        disp = [self.x, self.y, self.z]
        mesh.translate(disp)
        # bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        # mesh = bigBox.subtract(mesh)
        return mesh


class SX(Surface):
    """
    Sphere (centered on x-axis)
    """

    def __init__(self, x, R, reg=None, surfaceNumber=None):
        self.x = x
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"SX {self.x} {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        s_p = S(x=translation[0], y=translation[1], z=translation[2], R=self.R)
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            reg = g4Reg()
            s_p = Orb(
                name="",
                pRMax=self.R,
                registry=reg,
            )
        mesh = s_p.mesh()
        disp = [self.x, 0, 0]
        mesh.translate(disp)
        return mesh


class SY(Surface):
    """
    Sphere (centered on y-axis)
    """

    def __init__(self, y, R, reg=None, surfaceNumber=None):
        self.y = y
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"SY {self.y} {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        s_p = S(x=translation[0], y=translation[1], z=translation[2], R=self.R)
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            reg = g4Reg()
            s_p = Orb(
                name="",
                pRMax=self.R,
                registry=reg,
            )
        mesh = s_p.mesh()
        disp = [0, self.y, 0]
        mesh.translate(disp)
        return mesh


class SZ(Surface):
    """
    Sphere (centered on z-axis)
    """

    def __init__(self, z, R, reg=None, surfaceNumber=None):
        self.z = z
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"SZ {self.z} {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        s_p = S(x=translation[0], y=translation[1], z=translation[2], R=self.R)
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            reg = g4Reg()
            s_p = Orb(
                name="",
                pRMax=self.R,
                registry=reg,
            )
        mesh = s_p.mesh()
        disp = [0, 0, self.z]
        mesh.translate(disp)
        return mesh


class C_X(Surface):
    """
    Cylinder (parallel to x-axis)
    """

    def __init__(self, y, z, R, reg=None, surfaceNumber=None):
        self.y = y
        self.z = z
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"C/X {self.y} {self.z} {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalTube(
            name="",
            pDx=self.R,
            pDy=self.R,
            pDz=inf,
            registry=reg,
        )

        mesh = s_p.mesh()
        axisIn = [0, 1, 0]
        angleDeg = -90
        mesh.rotate(axisIn, angleDeg)
        disp = [0.0, self.y, self.z]
        mesh.translate(disp)

        return mesh


class C_Y(Surface):
    """
    Cylinder (parallel to y-axis)
    """

    def __init__(self, x, z, R, reg=None, surfaceNumber=None):
        self.x = x
        self.z = z
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"C/Y {self.x} {self.z} {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalTube(
            name="",
            pDx=self.R,
            pDy=self.R,
            pDz=inf,
            registry=reg,
        )

        mesh = s_p.mesh()
        axisIn = [1, 0, 0]
        angleDeg = 90
        mesh.rotate(axisIn, angleDeg)
        disp = [self.x, 0.0, self.z]
        mesh.translate(disp)

        return mesh


class C_Z(Surface):
    """
    Cylinder (parallel to z-axis)
    """

    def __init__(self, x, y, R, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"C/Z {self.x} {self.y} {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalTube(
            name="",
            pDx=self.R,
            pDy=self.R,
            pDz=inf,
            registry=reg,
        )

        mesh = s_p.mesh()
        disp = [self.x, self.y, 0.0]
        mesh.translate(disp)

        return mesh


class CX(Surface):
    """
    Cylinder (on x-axis)
    """

    def __init__(self, R, reg=None, surfaceNumber=None):
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"CX {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalTube(
            name="",
            pDx=self.R,
            pDy=self.R,
            pDz=inf,
            registry=reg,
        )

        mesh = s_p.mesh()
        axisIn = [0, 1, 0]
        angleDeg = -90
        mesh.rotate(axisIn, angleDeg)

        return mesh


class CY(Surface):
    """
    Cylinder (on y-axis)
    """

    def __init__(self, R, reg=None, surfaceNumber=None):
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"CY {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalTube(
            name="",
            pDx=self.R,
            pDy=self.R,
            pDz=inf,
            registry=reg,
        )

        mesh = s_p.mesh()
        axisIn = [1, 0, 0]
        angleDeg = 90
        mesh.rotate(axisIn, angleDeg)

        return mesh


class CZ(Surface):
    """
    Cylinder (on z-axis)
    """

    def __init__(self, R, reg=None, surfaceNumber=None):
        self.R = R
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"CZ {self.R}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalTube(
            name="",
            pDx=self.R,
            pDy=self.R,
            pDz=inf,
            registry=reg,
        )

        mesh = s_p.mesh()

        return mesh


""" surface: Cone

:param sign: choice positive slope or negative slope.

The quadratic equation for a cone describes a cone of two sheets. One sheet is a
cone of positive slope, and the other has a negative slope. The parameter sign
provides the option to select either of the two sheets. The +1 or the -1 entry on
the cone surface card causes the one sheet cone treatment to be used. If the sign
of the entry is positive, the specified sheet is the one that extends to infinity
in the positive direction of the coordinate axis to which the cone axis is parallel.
The converse is true for a negative entry.
"""


class K_X(Surface):
    """
    Cone (parallel to x-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, x, y, z, t_sqr, sign, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.t_sqr = t_sqr
        self.sign = sign
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"K/X {self.x} {self.y} {self.z} {self.t_sqr} {self.sign}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalCone(
            name="",
            pxSemiAxis=self.t_sqr**0.5,
            pySemiAxis=self.t_sqr**0.5,
            zMax=inf,
            pzTopCut=inf * 0.9999999999,
            registry=reg,
        )
        mesh = s_p.mesh()

        if self.sign > 0:
            axisIn = [0, 1, 0]
            angleDeg = 180
            mesh.rotate(axisIn, angleDeg)
            disp = [0, 0, inf * 0.9999999999]
            mesh.translate(disp)
        else:
            disp = [0, 0, inf * -0.9999999999]
            mesh.translate(disp)

        axisIn = [0, 1, 0]
        angleDeg = -90
        mesh.rotate(axisIn, angleDeg)

        disp = [self.x, self.y, self.z]
        mesh.translate(disp)

        return mesh


class K_Y(Surface):
    """
    Cone (parallel to y-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, x, y, z, t_sqr, sign, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.t_sqr = t_sqr
        self.sign = sign
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"K/Y {self.x} {self.y} {self.z} {self.t_sqr} {self.sign}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalCone(
            name="",
            pxSemiAxis=self.t_sqr**0.5,
            pySemiAxis=self.t_sqr**0.5,
            zMax=inf,
            pzTopCut=inf * 0.9999999999,
            registry=reg,
        )
        mesh = s_p.mesh()

        if self.sign > 0:
            axisIn = [0, 1, 0]
            angleDeg = 180
            mesh.rotate(axisIn, angleDeg)
            disp = [0, 0, inf * 0.9999999999]
            mesh.translate(disp)
        else:
            disp = [0, 0, inf * -0.9999999999]
            mesh.translate(disp)

        axisIn = [1, 0, 0]
        angleDeg = 90
        mesh.rotate(axisIn, angleDeg)

        disp = [self.x, self.y, self.z]
        mesh.translate(disp)

        return mesh


class K_Z(Surface):
    """
    Cone (parallel to z-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, x, y, z, t_sqr, sign, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.t_sqr = t_sqr
        self.sign = sign
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"K/Z {self.x} {self.y} {self.z} {self.t_sqr} {self.sign}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalCone(
            name="",
            pxSemiAxis=self.t_sqr**0.5,
            pySemiAxis=self.t_sqr**0.5,
            zMax=inf,
            pzTopCut=inf * 0.9999999999,
            registry=reg,
        )
        mesh = s_p.mesh()

        if self.sign > 0:
            axisIn = [0, 1, 0]
            angleDeg = 180
            mesh.rotate(axisIn, angleDeg)
            disp = [0, 0, inf * 0.9999999999]
            mesh.translate(disp)
        else:
            disp = [0, 0, inf * -0.9999999999]
            mesh.translate(disp)

        disp = [self.x, self.y, self.z]
        mesh.translate(disp)

        return mesh


class KX(Surface):
    """
    Cone (on x-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, x, t_sqr, sign, reg=None, surfaceNumber=None):
        self.x = x
        self.t_sqr = t_sqr
        self.sign = sign
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"KX {self.x} {self.t_sqr} {self.sign}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalCone(
            name="",
            pxSemiAxis=self.t_sqr**0.5,
            pySemiAxis=self.t_sqr**0.5,
            zMax=inf,
            pzTopCut=inf * 0.9999999999,
            registry=reg,
        )
        mesh = s_p.mesh()

        if self.sign > 0:
            axisIn = [0, 1, 0]
            angleDeg = 180
            mesh.rotate(axisIn, angleDeg)
            disp = [0, 0, inf * 0.9999999999]
            mesh.translate(disp)
        else:
            disp = [0, 0, inf * -0.9999999999]
            mesh.translate(disp)

        axisIn = [0, 1, 0]
        angleDeg = -90
        mesh.rotate(axisIn, angleDeg)

        disp = [self.x, 0, 0]
        mesh.translate(disp)

        return mesh


class KY(Surface):
    """
    Cone (on y-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, y, t_sqr, sign, reg=None, surfaceNumber=None):
        self.y = y
        self.t_sqr = t_sqr
        self.sign = sign
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"KY {self.y} {self.t_sqr} {self.sign}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalCone(
            name="",
            pxSemiAxis=self.t_sqr**0.5,
            pySemiAxis=self.t_sqr**0.5,
            zMax=inf,
            pzTopCut=inf * 0.9999999999,
            registry=reg,
        )
        mesh = s_p.mesh()

        if self.sign > 0:
            axisIn = [0, 1, 0]
            angleDeg = 180
            mesh.rotate(axisIn, angleDeg)
            disp = [0, 0, inf * 0.9999999999]
            mesh.translate(disp)
        else:
            disp = [0, 0, inf * -0.9999999999]
            mesh.translate(disp)

        axisIn = [1, 0, 0]
        angleDeg = 90
        mesh.rotate(axisIn, angleDeg)

        disp = [0, self.y, 0]
        mesh.translate(disp)

        return mesh


class KZ(Surface):
    """
    Cone (on z-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, z, t_sqr, sign, reg=None, surfaceNumber=None):
        self.z = z
        self.t_sqr = t_sqr
        self.sign = sign
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"KZ {self.z} {self.t_sqr} {self.sign}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        # this will be a quadric surface if transformed (GQ or SQ in MCNP)
        # SB can now mesh quadrics
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        # else:
        reg = g4Reg()
        s_p = EllipticalCone(
            name="",
            pxSemiAxis=self.t_sqr**0.5,
            pySemiAxis=self.t_sqr**0.5,
            zMax=inf,
            pzTopCut=inf * 0.9999999999,
            registry=reg,
        )
        mesh = s_p.mesh()

        if self.sign > 0:
            axisIn = [0, 1, 0]
            angleDeg = 180
            mesh.rotate(axisIn, angleDeg)
            disp = [0, 0, inf * 0.9999999999]
            mesh.translate(disp)
        else:
            disp = [0, 0, inf * -0.9999999999]
            mesh.translate(disp)

        disp = [0, 0, self.z]
        mesh.translate(disp)

        return mesh


class SQ(Surface):
    """
    Ellipsoid, Hyperboloid, Paraboloid
    (axes parallel to x-, y-, or z-axis)
    """

    def __init__(self, A, B, C, D, E, F, G, x, y, z, reg=None, surfaceNumber=None):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.E = E
        self.F = F
        self.G = G
        self.x = x
        self.y = y
        self.z = z
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return (
            f"SQ {self.A} {self.B} {self.C} {self.D} {self.E}"
            f" {self.F} {self.G} {self.x} {self.y} {self.z}"
        )

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        pass

    def mesh(self):
        # SB can now mesh quadrics
        pass


class GQ(Surface):
    """
    Cylinder, Cone, Ellipsoid, Hyperboloid, Paraboloid
    (axes not parallel to x-, y-, or z-axis)
    """

    def __init__(self, A, B, C, D, E, F, G, H, J, K, reg=None, surfaceNumber=None):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.E = E
        self.F = F
        self.G = G
        self.H = H
        self.J = J
        self.K = K
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return (
            f"GQ {self.A} {self.B} {self.C} {self.D} {self.E}"
            f" {self.F} {self.G} {self.H} {self.J} {self.K}"
        )

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # ToDo
        pass

    def mesh(self):
        # SB can now mesh quadrics
        pass


class TX(Surface):
    """
    Elliptical or Circular Torus
    (axis is parallel to x-, y-, or z-axis)
    rotationally symmetric about axes parallel to the x-axes
    """

    def __init__(self, x, y, z, A, B, C, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.A = A
        self.B = B
        self.C = C
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"TX {self.x} {self.y} {self.z} {self.A} {self.B} {self.C}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # I DONT THINK THIS IS POSSIBLE AS A TORUS CANNOT BE REPRESENTED BY 2ND-DEGREE POLYNOMIAL, SO NO GQ OR SQ???
        pass

    def mesh(self):
        reg = g4Reg()
        solid = Torus(
            name="",
            pRmin=0,
            pRmax=self.C,
            pRtor=self.A,
            pSPhi=0,
            pDPhi=2 * _np.pi,
            registry=reg,
            nslice=50,
            nstack=30,
        )
        mesh = solid.mesh()

        axisIn = [0, 1, 0]
        angleDeg = -90
        mesh.rotate(axisIn, angleDeg)

        disp = [self.x, self.y, self.z]
        mesh.translate(disp)

        return mesh


class TY(Surface):
    """
    Elliptical or Circular Torus
    (axis is parallel to x-, y-, or z-axis)
    rotationally symmetric about axes parallel to the y-axes
    """

    def __init__(self, x, y, z, A, B, C, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.A = A
        self.B = B
        self.C = C
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"TY {self.x} {self.y} {self.z} {self.A} {self.B} {self.C}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # I DONT THINK THIS IS POSSIBLE AS A TORUS CANNOT BE REPRESENTED BY 2ND-DEGREE POLYNOMIAL, SO NO GQ OR SQ???
        pass

    def mesh(self):
        reg = g4Reg()
        solid = Torus(
            name="",
            pRmin=0,
            pRmax=self.C,
            pRtor=self.A,
            pSPhi=0,
            pDPhi=2 * _np.pi,
            registry=reg,
            nslice=50,
            nstack=30,
        )
        mesh = solid.mesh()

        axisIn = [1, 0, 0]
        angleDeg = 90
        mesh.rotate(axisIn, angleDeg)

        disp = [self.x, self.y, self.z]
        mesh.translate(disp)

        return mesh


class TZ(Surface):
    """
    Elliptical or Circular Torus
    (axis is parallel to x-, y-, or z-axis)
    rotationally symmetric about axes parallel to the z-axes
    """

    def __init__(self, x, y, z, A, B, C, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.A = A
        self.B = B
        self.C = C
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"TZ {self.x} {self.y} {self.z} {self.A} {self.B} {self.C} "

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        # I DONT THINK THIS IS POSSIBLE AS A TORUS CANNOT BE REPRESENTED BY 2ND-DEGREE POLYNOMIAL, SO NO GQ OR SQ???
        pass

    def mesh(self):
        reg = g4Reg()
        solid = Torus(
            name="",
            pRmin=0,
            pRmax=self.C,
            pRtor=self.A,
            pSPhi=0,
            pDPhi=2 * _np.pi,
            registry=reg,
            nslice=50,
            nstack=30,
        )

        mesh = solid.mesh()
        disp = [self.x, self.y, self.z]
        mesh.translate(disp)

        return mesh


class BOX(Surface):
    """
    Macrobody: Box
    arbitrarily oriented orthogonal box
    all corner angels are 90 degrees

    :param vx, vy, vz: The x,y,z coordinates of a corner of the box.
    :param a1x, a1y, a1z: Vector of 1st side from the specified corner coordinates.
    :param a2x, a2y, a2z: Vector of 2nd side from the specified corner coordinates.
    :param a3x, a3y, a3z: Vector of 3rd side from the specified corner coordinates.
    """

    def __init__(
        self, vx, vy, vz, a1x, a1y, a1z, a2x, a2y, a2z, a3x, a3y, a3z, reg=None, surfaceNumber=None
    ):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.a1x = a1x
        self.a1y = a1y
        self.a1z = a1z
        self.a2x = a2x
        self.a2y = a2y
        self.a2z = a2z
        self.a3x = a3x
        self.a3y = a3y
        self.a3z = a3z

        v = _np.array([vx, vy, vz])
        a1 = _np.array([a1x, a1y, a1z])
        a2 = _np.array([a2x, a2y, a2z])
        a3 = _np.array([a3x, a3y, a3z])
        #  checks for correct user BOX definition
        a1_a2 = _np.dot(a1, a2)
        a1_a3 = _np.dot(a1, a3)
        a2_a3 = _np.dot(a2, a3)

        if abs(a1_a2) > 1e-9:
            msg = "The vectors a1 and a2 must be orthogonal"
            raise TypeError(msg)
        if abs(a1_a3) > 1e-9:
            msg = "The vectors a1 and a3 must be orthogonal"
            raise TypeError(msg)
        if abs(a2_a3) > 1e-9:
            msg = "The vectors a2 and a3 must be orthogonal"
            raise TypeError(msg)

        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return (
            f"BOX {self.vx} {self.vy} {self.vz} {self.a1x} {self.a1y} {self.a1z} "
            f" {self.a2x} {self.a2y} {self.a2z} {self.a3x} {self.a3y} {self.a3z}"
        )

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)
        # box
        v = _np.array([self.vx, self.vy, self.vz])
        a1 = _np.array([self.a1x, self.a1y, self.a1z])
        a2 = _np.array([self.a2x, self.a2y, self.a2z])
        a3 = _np.array([self.a3x, self.a3y, self.a3z])

        if _np.array_equal(rotation, _np.eye(rotation.shape[0])):
            # no rotation
            if _np.array_equal(translation, _np.array([0, 0, 0])):
                # no translation
                return self
            else:
                v_p = v + translation

                # new surface (prime)
                s_p = BOX(*v_p, *a1, *a2, *a3)  # box translation
                s_p.surfaceNumber = self.surfaceNumber

                return s_p

        else:  # rotation
            # transformed box (prime)
            # rotate each side vector
            a1_p = rotation @ a1
            a2_p = rotation @ a2
            a3_p = rotation @ a3
            # rotate and translate corner point
            v_p = rotation @ v + translation

            # new surface (prime)
            s_p = BOX(*v_p, *a1_p, *a2_p, *a3_p)  # box translation
            s_p.surfaceNumber = self.surfaceNumber

            return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
            s = s_p
        else:
            s = self

        p1 = P(
            A=s.a1x,
            B=s.a1y,
            C=s.a1z,
            D=(s.a1x * s.vx) + (s.a1y * s.vy) + (s.a1z * s.vz),
        )
        # print("d1=", (self.a1x * self.vx) + (self.a1y * self.vy) + (self.a1z * self.vz))
        p2 = P(
            A=s.a1x,
            B=s.a1y,
            C=s.a1z,
            D=s.a1x * (s.vx + s.a1x) + s.a1y * (s.vy + s.a1y) + s.a1z * (s.vz + s.a1z),
        )
        # print("d2=", (self.a2x * self.vx) + (self.a2y * self.vy) + (self.a2z * self.vz))
        p3 = P(
            A=s.a2x,
            B=s.a2y,
            C=s.a2z,
            D=(s.a2x * s.vx) + (s.a2y * s.vy) + (s.a2z * s.vz),
        )
        # print("d3=", self.a2x * (self.vx + self.a2x) + self.a2y * (self.vy + self.a2y) + self.a2z * (self.vz + self.a2z))
        p4 = P(
            A=s.a2x,
            B=s.a2y,
            C=s.a2z,
            D=s.a2x * (s.vx + s.a2x) + s.a2y * (s.vy + s.a2y) + s.a2z * (s.vz + s.a2z),
        )
        # print("d4=", (self.a3x * self.vx) + (self.a3y * self.vy) + (self.a3z * self.vz))
        p5 = P(
            A=s.a3x,
            B=s.a3y,
            C=s.a3z,
            D=(s.a3x * s.vx) + (s.a3y * s.vy) + (s.a3z * s.vz),
        )
        # print("d5=", (self.a3x * self.vx) + (self.a3y * self.vy) + (self.a3z * self.vz))
        p6 = P(
            A=s.a3x,
            B=s.a3y,
            C=s.a3z,
            D=s.a3x * (s.vx + s.a3x) + s.a3y * (s.vy + s.a3y) + s.a3z * (s.vz + s.a3z),
        )
        # print("d6=", self.a3x * (self.vx + self.a3x) + self.a3y * (self.vy + self.a3y) + self.a3z * (self.vz + self.a3z))

        geom1 = Intersection(p1, Complement(p2))
        geom2 = Intersection(p3, Complement(p4))
        geom3 = Intersection(p5, Complement(p6))

        geom4 = Intersection(geom1, geom2)
        geom5 = Intersection(geom3, geom4)

        mesh = geom5.mesh()
        bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        mesh = bigBox.subtract(mesh)

        return mesh


class RPP(Surface):
    """
    Macrobody: Rectangular Parallelepiped
    RPP surfaces will only be normal to the x-, y-, and z-axes
    x,y,z values are relative to the origin

    :param xmin, xmax: Termini of box sides normal to the x-axis.
    :param ymin, ymax: Termini of box sides normal to the y-axis.
    :param zmin, zmax: Termini of box sides normal to the z-axis.
    """

    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax, reg=None, surfaceNumber=None):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return (
            f"RPP {self.xmin} {self.xmax} {self.ymin} "
            f" {self.ymin} {self.ymax} {self.zmin} {self.zmax}"
        )

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        s_p = BOX(
            vx=self.xmin,
            vy=self.ymin,
            vz=self.zmin,
            a1x=self.xmax - self.xmin,
            a1y=0,
            a1z=0,
            a2x=0,
            a2y=self.ymax - self.ymin,
            a2z=0,
            a3x=0,
            a3y=0,
            a3z=self.zmax - self.zmin,
        )
        s_p = s_p._transform(rotation=rotation, translation=translation)
        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
            mesh = s_p.mesh()
        else:
            p1 = PX(self.xmin)
            p2 = PX(self.xmax)
            p3 = PY(self.ymin)
            p4 = PY(self.ymax)
            p5 = PZ(self.zmin)
            p6 = PZ(self.zmax)

            geom1 = Intersection(p1, Complement(p2))
            geom2 = Intersection(p3, Complement(p4))
            geom3 = Intersection(p5, Complement(p6))

            geom4 = Intersection(geom1, geom2)
            geom5 = Intersection(geom3, geom4)

            mesh = geom5.mesh()

            bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
            mesh = bigBox.subtract(mesh)

        return mesh


class SPH(Surface):
    """
    Macrobody: Sphere

    :param vx, vy, vz: The x,y,z coordinates of the center of the sphere.
    :param r: Radius of sphere.
    """

    def __init__(self, vx, vy, vz, r, reg=None, surfaceNumber=None):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.r = r
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"SPH {self.vx} {self.vy} {self.vz} {self.r}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)

        if _np.allclose(rotation, _np.eye(3)) and _np.allclose(translation, [0, 0, 0]):
            return self

        # transform to prime (_p)
        s_p = S(
            x=self.vx + translation[0],
            y=self.vy + translation[1],
            z=self.vz + translation[2],
            R=self.r,
        )
        s_p.surfaceNumber = self.surfaceNumber

        return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
        else:
            s_p = S(self.vx, self.vy, self.vz, self.r)

        mesh = s_p.mesh()
        bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        mesh = bigBox.subtract(mesh)

        return mesh


class RCC(Surface):
    """
    Macrobody: Right Circular Cylinder

    :param vx, vy, vz: The x,y,z coordinates at the center of the base for the right circular cylinder.
    :param hx, hy, hz: Right circular cylinder axis vector, which provides both the orientation and the \
    height of the cylinder.
    :param r: Radius of right circular cylinder.
    """

    def __init__(self, vx, vy, vz, hx, hy, hz, r, reg=None, surfaceNumber=None):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.r = r
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"RCC {self.vx} {self.vy} {self.vz} {self.hx} {self.hy} {self.hz} {self.r}"

    def _transform(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        rotation = _np.array(rotation)
        translation = _np.array(translation)
        # rcc
        v = _np.array([self.vx, self.vy, self.vz])
        h = _np.array([self.hx, self.hy, self.hz])

        # print(f"h: {h}")
        # print(f"v: {v}")

        if _np.allclose(rotation, _np.eye(3)):
            # no rotation
            # print(f"N rotation")
            if _np.allclose(translation, [0, 0, 0]):
                # print(f"N translation")
                # no translation
                return self
            else:
                # print(f"Y translation")
                v_p = v + translation

                # new surface (prime)
                s_p = RCC(*v_p, *h, self.r)  # rcc translation
                s_p.surfaceNumber = self.surfaceNumber

                return s_p

        else:  # rotation
            # transform rcc (prime _p)
            # rotate and translate the point at the centre of the base
            v_p = rotation @ v + translation
            # rotate height vector
            h_p = rotation @ h

            # new surface (prime)
            s_p = RCC(*v_p, *h_p, self.r)  # rcc translation
            s_p.surfaceNumber = self.surfaceNumber

            return s_p

    def mesh(self):
        if self.transformation:
            s_p = self._transform(
                rotation=self.transformation.rotationMatrix,
                translation=self.transformation.displacementVector,
            )
            s = s_p
        else:
            s = self

        reg = g4Reg()
        solid = EllipticalTube(
            name="",
            pDx=s.r,
            pDy=s.r,
            pDz=inf,
            registry=reg,
        )

        h = _np.array([s.hx, s.hy, s.hz])
        hMag = _np.sqrt(s.hx**2 + s.hy**2 + s.hz**2)
        p1 = PZ(0)
        p2 = PZ(hMag)

        geom1 = Intersection(p1, Complement(p2))
        geom2 = Intersection(geom1, solid)

        mesh = geom2.mesh()

        axisIn, angleDeg = self._rotationAboutAxis(h, [0, 0, 1])
        mesh.rotate(axisIn, angleDeg)
        disp = [s.vx, s.vy, s.vz]
        mesh.translate(disp)

        bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        mesh = bigBox.subtract(mesh)

        return mesh


class RHP_HEX(Surface):
    """
    Macrobody: Right Hexagonal Prism

    :param vx, vy, vz: The x,y,z coordinates of the bottom of the hexagonal prism.
    :param h1, h2, h3: Vector from the bottom to the top of the hexagonal prism. \
    For a z-hex with height h, h1, h2, and h3= 0 0 h.
    :param r1, r2, r3: Vector from the axis to the center of the 1st facet. \
    For a pitch 2p facet normal to y-axis, r1, r2, and r3= 0 p 0.
    :param s1, s2, s3: Vector to center of the 2nd facet.
    :param t1, t2, t3: Vector to center of the 3rd facet.
    """

    def __init__(
        self,
        v1,
        v2,
        v3,
        h1,
        h2,
        h3,
        r1,
        r2,
        r3,
        s1=None,
        s2=None,
        s3=None,
        t1=None,
        t2=None,
        t3=None,
        reg=None,
        surfaceNumber=None,
    ):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.h1 = h1
        self.h2 = h2
        self.h3 = h3
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return (
            f"RHP {self.v1} {self.v2} {self.v3}"
            f" {self.h1} {self.h2} {self.h3}"
            f" {self.r1} {self.r2} {self.r3}"
            f" {self.s1} {self.s2} {self.s3}"
            f" {self.t1} {self.t2} {self.t3}"
        )

    def _transform(self):
        # ToDo
        # will requre repositioning 8 planes with rotations and translations
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        #    s = s_p
        # else:
        #    s = self

        v = _np.array([self.v1, self.v2, self.v3])
        r = _np.array([self.r1, self.r2, self.r3])
        s = _np.array([self.s1, self.s2, self.s3])
        t = _np.array([self.t1, self.t2, self.t3])
        h = _np.array([self.h1, self.h2, self.h3])

        reg = g4Reg()
        if (
            self.s1 is None
            and self.s2 is None
            and self.s3 is None
            and self.t1 is None
            and self.t2 is None
            and self.t3 is None
        ):  # regular hexagon
            s1 = _np.sqrt(3) / 2 * r[1] + 1 / 2 * r[0]
            s2 = _np.sqrt(3) / 2 * r[0] - 1 / 2 * r[1]
            s3 = 0
            t1 = -_np.sqrt(3) / 2 * r[1] + 1 / 2 * r[0]
            t2 = -_np.sqrt(3) / 2 * r[0] - 1 / 2 * r[1]
            t3 = 0
            s = _np.array([s1, s2, s3])
            t = _np.array([t1, t2, t3])

        A, B, C = 0, 0, 1
        D1 = _np.linalg.norm(h)
        D2 = _np.linalg.norm([0, 0, 0])
        p1 = P(A, B, C, D1)  # top face
        p2 = P(A, B, C, D2)  # bottom face

        A, B, C = r * 2
        D1 = _np.linalg.norm(r)
        D2 = -_np.linalg.norm(r)
        p3 = P(A, B, C, D1)  # r face
        p4 = P(A, B, C, D2)  # r opposite side

        A, B, C = s
        D1 = _np.linalg.norm(s)
        D2 = -_np.linalg.norm(s)
        p5 = P(A, B, C, D1)  # s face
        p6 = P(A, B, C, D2)  # s opposite side

        A, B, C = t
        D1 = _np.linalg.norm(t)
        D2 = -_np.linalg.norm(t)
        p7 = P(A, B, C, D1)  # t face
        p8 = P(A, B, C, D2)  # t opposite side

        geom1 = Intersection(p2, Complement(p1))  # top and bottom
        geom2 = Intersection(p4, Complement(p3))  # r
        geom3 = Intersection(p6, Complement(p5))  # s
        geom4 = Intersection(p8, Complement(p7))  # t

        geom5 = Intersection(geom1, geom2)
        geom6 = Intersection(geom3, geom4)
        geom7 = Intersection(geom5, geom6)

        mesh = geom7.mesh()
        bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        mesh = bigBox.subtract(mesh)

        axisIn, angleDeg = self._rotationAboutAxis(h, [0, 0, 1])
        mesh.rotate(axisIn, angleDeg)
        disp = v
        mesh.translate(disp)

        return mesh


class REC(Surface):
    """
    Macrobody: Right Elliptical Cylinder

    :param vx, vy, vz: The x,y,z coordinates of the cylinder bottom.
    :param hx, hy, hz: Cylinder axis height vector.
    :param v1x, v1y, v1z: Ellipse major axis vector (normal to hx hy hz).
    :param v1x, v1y, v1z: Ellipse minor axis vector (orthogonal to vectors h and v1).
    """

    def __init__(
        self,
        vx,
        vy,
        vz,
        hx,
        hy,
        hz,
        v1x,
        v1y,
        v1z,
        v2x,
        v2y=None,
        v2z=None,
        reg=None,
        surfaceNumber=None,
    ):  # if 10 entries instead of 12, the 10th entry (v2x) is the minor axis radius
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.v1x = v1x
        self.v1y = v1y
        self.v1z = v1z
        self.v2x = v2x
        self.v2y = v2y
        self.v2z = v2z

        h = _np.array([hx, hy, hz])
        v1 = _np.array([v1x, v1y, v1z])
        v2 = _np.array([v2x, v2y, v2z])

        if (
            self.v2y is None and self.v2z is None
        ):  # with 10 entries, v2x becomes the minor axis radius
            v2 = _np.cross(
                h, v1
            )  # direction of minor axis is determined from the cross product of h and v1 vectors
            if _np.allclose(v2, _np.zeros(len(v2))):
                msg = "The vectors h and v1 must be orthogonal"
                raise ValueError(msg)
            else:
                v2 = v2 / _np.linalg.norm(v2) * self.v2x
        else:
            v2 = _np.array([self.v2x, self.v2y, self.v2z])

            # extra checks for correct user REC definition
            h_v1 = _np.dot(h, v1)
            h_v2 = _np.dot(h, v2)
            v1_v2 = _np.dot(v1, v2)

            if abs(h_v1) > 1e-9:
                msg = "The vectors v1 and h must be orthogonal"
                raise TypeError(msg)
            if abs(h_v2) > 1e-9:
                msg = "The vectors v2 and h must be orthogonal"
                raise TypeError(msg)
            if abs(v1_v2) > 1e-9:
                msg = "The vectors v2 and v1 must be orthogonal"
                raise TypeError(msg)

        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        if self.v2y is None and self.v2z is None:
            return (
                f"REC {self.vx} {self.vy} {self.vz}"
                f" {self.hx} {self.hy} {self.hz}"
                f" {self.v1x} {self.v1y} {self.v1z}"
                f" {self.v2x}"  # with 10 entries, v2x becomes the minor axis radius
            )
        else:
            return (
                f"REC {self.vx} {self.vy} {self.vz}"
                f" {self.hx} {self.hy} {self.hz}"
                f" {self.v1x} {self.v1y} {self.v1z}"
                f" {self.v2x} {self.v2y} {self.v2z}"
            )

    def _transform(self):
        # ToDo
        pass

    def mesh(self):
        v = _np.array([self.vx, self.vy, self.vz])
        h = _np.array([self.hx, self.hy, self.hz])
        v1 = _np.array([self.v1x, self.v1y, self.v1z])
        v2 = _np.array([self.v2x, self.v2y, self.v2z])

        if (
            self.v2y is None and self.v2z is None
        ):  # with 10 entries, v2x becomes the minor axis radius
            # direction of minor axis is determined from the cross product of h and v1 vectors
            msg = "v2y and v2z are None"
            # print(msg)
            v2 = _np.cross(h, v1)
            if _np.allclose(v2, _np.zeros(len(v2))):
                msg = "The vectors h and v1 must be orthogonal"
                raise ValueError(msg)
            else:
                v2 = v2 / _np.linalg.norm(v2) * self.v2x
                # print(v2)
        else:
            v2 = _np.array([self.v2x, self.v2y, self.v2z])

        reg = g4Reg()

        solid = EllipticalTube(
            name="",
            pDx=_np.linalg.norm(v1),  # ellipse major axis
            pDy=_np.linalg.norm(v2),  # ellipse minor axis
            pDz=inf,
            registry=reg,
        )

        h = _np.array([self.hx, self.hy, self.hz])
        hMag = _np.sqrt(self.hx**2 + self.hy**2 + self.hz**2)
        p1 = PZ(0)
        p2 = PZ(hMag)

        geom1 = Intersection(p1, Complement(p2))
        geom2 = Intersection(geom1, solid)

        mesh = geom2.mesh()
        bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        mesh = bigBox.subtract(mesh)

        v1Norm = v1 / _np.linalg.norm(v1)
        v2Norm = v2 / _np.linalg.norm(v2)
        hNorm = h / _np.linalg.norm(h)
        M = _np.array([v1Norm, v2Norm, hNorm])
        output = matrix2axisangle(M)
        mesh.rotate(output[0], _np.rad2deg(output[1]))
        disp = [self.vx, self.vy, self.vz]
        mesh.translate(disp)

        return mesh


class TRC(Surface):
    """
    Macrobody: Truncated Right-Angle Cone

    :param vx, vy, vz: the x,y,z coordinates of the cone bottom
    :param hx, hy, hz: cone axis height vector
    :param r1: radius of lower cone base
    :param r2: radius of upper cone base, where r1>r2
    """

    def __init__(self, vx, vy, vz, hx, hy, hz, r1, r2, reg=None, surfaceNumber=None):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.r1 = r1
        if r2 >= r1:
            msg = "r1 must be greater than r2"
            raise ValueError(msg)
        self.r2 = r2
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return (
            f"TRC {self.vx} {self.vy} {self.vz}"
            f" {self.hx} {self.hy} {self.hz}"
            f" {self.r1} {self.r2}"
        )

    def _transform(self):
        # ToDo
        pass

    def mesh(self):
        # if self.transformation:
        #    s_p = self._transform(rotation=self.transformation.rotationMatrix, translation=self.transformation.displacementVector)
        #    s = s_p
        # else:
        #    s = self

        reg = g4Reg()

        # G4 cone has eqn: (x/xSemiAxis)**2 + (y/ySemiAxis)**2 = (zHeight - z)**2
        # G4 elliptical sections: dx = xSemiAxis * zHeight dy = ySemiAxis * zHeight
        # xSemiAxis and ySemiAxis are scaling factors figured out from elliptical sections at z=0
        # R(z=0) = xSemiAxis * zHeight   >>>    xSemiAxis = R(z=0) / zHeight
        # R(z=-zTopCut) = r1
        # R(z=+zTopCut) = r2
        # >>> r1 = xSemiAxis * (zHeight + zTopCut)
        #   & r2 = xSemiAxis * (zHeight - zTopCut)
        # r1 - r2 = xSemiAxis * (2*zTopCut)
        # >>> xSemiAxis = (r1 - r2) / (2 * zTopCut)  {*}
        # r2 = {(r1 - r2) / (2 * zTopCut)} * (zHeight - zTopCut)
        # >>> r2 * (2 * zTopCut) = (r1 - r2) * (zHeight - zTopCut)
        # >>> zHeight = ((r2 * (2 * zTopCut)) / (r1 - r2)) + zTopCut   =   (((r2 * 2) / (r1 - r2)) + 1) * zTopCut  {*}

        h = _np.array([self.hx, self.hy, self.hz])
        hMag = _np.sqrt(self.hx**2 + self.hy**2 + self.hz**2)
        zTopCut = hMag / 2
        zHeight = zTopCut * (1 + ((2 * self.r2) / (self.r1 - self.r2)))
        xSemiAxis = (self.r1 - self.r2) / (2 * zTopCut)
        ySemiAxis = xSemiAxis

        solid = EllipticalCone(
            name="",
            # pxSemiAxis=xSemiAxis,
            # pySemiAxis=ySemiAxis,
            pxSemiAxis=0.1,
            pySemiAxis=0.5,
            zMax=zHeight,
            pzTopCut=zTopCut,
            registry=reg,
        )

        p1 = PZ(-zTopCut)

        geom1 = Intersection(p1, Complement(solid))
        mesh = geom1.mesh()
        bigBox = mesh.cube(center=[0, 0, 0], radius=[inf, inf, inf])  # big box (universe)
        mesh = bigBox.subtract(mesh)

        disp = [0, 0, zTopCut]
        mesh.translate(disp)

        axisIn, angleDeg = self._rotationAboutAxis(h, [0, 0, 1])
        mesh.rotate(axisIn, angleDeg)
        disp = [self.vx, self.vy, self.vz]
        mesh.translate(disp)

        return mesh


class ELL(Surface):
    """
    Macrobody: Ellipsoid

    :param v1x, v1y, v1z: /
        if rm>0, the coordinates of the 1st focus /
        if rm<0, the coordinates of the center of the ellipsoid
    :param v2x, v2y, v2z:
        if rm>0, the coordinates of the 2nd focus /
        if rm<0, major axis vector (vector from the center of the ellipsoid through a focus to the vertex; /
        length = major radius)
    :param rm:
        if rm>0, major radius length /
        if rm<0, minor radius length
    """

    def __init__(self, v1x, v1y, v1z, v2x, v2y, v2z, rm, reg=None, surfaceNumber=None):
        self.v1x = v1x
        self.v1y = v1y
        self.v1z = v1z
        self.v2x = v2x
        self.v2y = v2y
        self.v2z = v2z
        self.rm = rm
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return f"ELL {self.v1x} {self.v1y} {self.v1z} {self.v2x} {self.v2y} {self.v2z} {self.rm}"

    def _transform(self):
        # ToDo
        pass

    def mesh(self):
        reg = g4Reg()
        # TODO


class WED(Surface):
    """
    Macrobody: Wedge

    :param vx, vy, vz: the x,y,z coordinates of wedge vertex
    :param v1x, v1y, v1z: vector of 1st side of triangular base
    :param v2x, v2y, v2z: vector of 2nd side of triangular base
    :param v3x, v3y, v3z: height vector
    """

    def __init__(
        self, vx, vy, vz, v1x, v1y, v1z, v2x, v2y, v2z, v3x, v3y, v3z, reg=None, surfaceNumber=None
    ):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.vx = v1x
        self.vy = v1y
        self.vz = v1z
        self.vx = v2x
        self.vy = v2y
        self.vz = v2z
        self.vx = v3x
        self.vy = v3y
        self.vz = v3z
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return (
            f"WED {self.vx} {self.vy} {self.vz}"
            f" {self.v1x} {self.v1y} {self.v1z}"
            f" {self.v2x} {self.v2y} {self.v2z}"
            f" {self.v3x} {self.v3y} {self.v3z}"
        )

    def _transform(self):
        # ToDo
        pass

    def mesh(self):
        reg = g4Reg()
        # TODO


class ARB(Surface):
    """
    Macrobody: Arbitrary Polyhedron

    :param ax, ay, az, bx, by, bz, cx, cy, cz, dx, dy, dz, /
    ex, ey, ez, fx, fy, fz, gx, gy, gz, hx, hy, hz: /
    The x-, y-, z-coordinates of the 1st through 8th corners of the polyhedron. \
    There must be eight x,y,z triplets to describe the eight corners of the polyhedron.
    :param n1, n2, n3, n4, n5, n6: /
    Four-digit numbers describing a side of the polyhedron in terms of its corresponding corners. /
    E.g., n1=1278 is a plane/side bounded by corners 1, 2, 7, and 8 (a, b, g, and h).
    """

    def __init__(
        self,
        ax,
        ay,
        az,
        bx,
        by,
        bz,
        cx,
        cy,
        cz,
        dx,
        dy,
        dz,
        ex,
        ey,
        ez,
        fx,
        fy,
        fz,
        gx,
        gy,
        gz,
        hx,
        hy,
        hz,
        n1,
        n2,
        n3,
        n4,
        n5,
        n6,
        surfaceNumber=None,
        reg=None,
    ):
        self.ax = ax
        self.ay = ay
        self.az = az
        self.bx = bx
        self.by = by
        self.bz = bz
        self.cx = cx
        self.cy = cy
        self.cz = cz
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.ex = ex
        self.ey = ey
        self.ez = ez
        self.fx = fx
        self.fy = fy
        self.fz = fz
        self.gx = gx
        self.gy = gy
        self.gz = gz
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        self.n5 = n5
        self.n6 = n6
        super().__init__(reg, surfaceNumber)

    def __repr__(self):
        return (
            f"ARB {self.ax} {self.ay} {self.az}"
            f" {self.bx} {self.by} {self.bz}"
            f" {self.cx} {self.cy} {self.cz}"
            f" {self.dx} {self.dy} {self.dz}"
            f" {self.ex} {self.ey} {self.ez}"
            f" {self.fx} {self.fy} {self.fz}"
            f" {self.gx} {self.gy} {self.gz}"
            f" {self.hx} {self.hy} {self.hz}"
            f" {self.n1} {self.n2} {self.n3}"
            f" {self.n4} {self.n5} {self.n6}"
        )

    def _transform(self):
        # ToDo
        pass

    def mesh(self):
        reg = g4Reg()
        # TODO
