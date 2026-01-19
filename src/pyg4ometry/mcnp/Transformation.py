import numpy as _np


class TR:
    """
    Coordinate Transformation

    :param o1: x-component of displacement vector of the transformation
    :param o2: y-component of displacement vector of the transformation
    :param o3: z-component of displacement vector of the transformation
    :param rotxx: x x' component of rotation matrix. Other parameters are as below in the default matrix.
    :param displacementOrigin: Displacement vector origin - either 1 or -1
    :param transformationNumber: Number assigned to the transformation
    :param angles: True for angles in degrees, False for cosines of the angles

    The default rotation matrix

        xx' & yx' & zx'
        xy' & yy' & zy'
        xz' & yz' & zz'

        1 & 0 & 0
        0 & 1 & 0
        0 & 0 & 1

    For `displacementOrigin = 1` the displacement vector is the location of the origin of the
    auxiliary coordinate system, defined in the main system. (DEFAULT). For `displacementOrigin = -1`,
    the displacement vector is the location of the origin of the main coordinate system, defined
    in the auxiliary system.

    Angles or cosines example: rotation around y-axis by 45 degrees
      cos(0) = 1
      cos(90) = 0
      cos(45) = 0.7071
      cos(135) = -0.7071

    angles = False
      TR1 0 0 0 0.7071 0 0.7071 0 1 0 -0.7071 0 0.7071
    angles = True
      *TR1 0 0 0 45 90 45 90 0 90 135 90 45

    Axis Rotation Matrices:
      R_x = [[1, 0, 0], [0, cos(Φ), -sin(Φ)], [0, sin(Φ), cos(Φ)]]
      R_y = [[cos(Φ), 0, sin(Φ)], [0, 1, 0], [-sin(Φ), 0, cos(Φ)]]
      R_z = [[cos(Φ), -sin(Φ), 0], [sin(Φ), cos(Φ), 0], [0, 0, 1]]
    Cosines (45° axis-rotation):
      R_x = [[1, 0, 0], [0, 0.7071, -0.7071], [0, 0.7071, 0.7071]]
      R_y = [[0.7071, 0, 0.7071], [0, 1, 0], [-0.7071, 0, 0.7071]]
      R_z = [[0.7071, -0.7071, 0], [0.7071, 0.7071, 0], [0, 0, 1]]
    Angles (45° axis-rotation):
      R_x = [[0, 90, 90], [90, 45, 135], [90, 45, 45]]
      R_y = [[45, 90, 45], [90, 0, 90], [135, 90, 45]]
      R_z = [[45, 135, 90], [45, 45, 90], [90, 90, 0]]
    """

    def __init__(
        self,
        o1=0.0,
        o2=0.0,
        o3=0.0,
        rotxx=1.0,
        rotyx=0.0,
        rotzx=0.0,
        rotxy=0.0,
        rotyy=1.0,
        rotzy=0.0,
        rotxz=0.0,
        rotyz=0.0,
        rotzz=1.0,
        displacementOrigin=1.0,
        angles=False,
        reg=None,
        transformationNumber=None,
    ):
        if angles:
            rotxx = _np.cos(rotxx)
            rotyx = _np.cos(rotyx)
            rotzx = _np.cos(rotzx)
            rotxy = _np.cos(rotxy)
            rotyy = _np.cos(rotyy)
            rotzy = _np.cos(rotzy)
            rotxz = _np.cos(rotxz)
            rotyz = _np.cos(rotyz)
            rotzz = _np.cos(rotzz)

        self.angles = angles

        self.displacementVector = [o1, o2, o3]
        self.rotationMatrix = _np.array(
            [[rotxx, rotyx, rotzx], [rotxy, rotyy, rotzy], [rotxz, rotyz, rotzz]]
        )

        self.displacementOrigin = displacementOrigin
        self.transformationNumber = transformationNumber
        self.angles = angles

        if reg:
            reg.addTransformation(self)
            self.reg = reg

    def copy(self):
        copyTR = TR(
            *self.displacementVector,
            *self.rotationMatrix[0],
            *self.rotationMatrix[1],
            *self.rotationMatrix[2],
            angles=self.angles,
            displacementOrigin=self.displacementOrigin,
        )
        return copyTR

    def compositeTR(self, TR2):
        """
        combines two transformations
        """
        self.displacementVector[0] = self.displacementVector[0] + TR2.displacementVector[0]
        self.displacementVector[1] = self.displacementVector[1] + TR2.displacementVector[1]
        self.displacementVector[2] = self.displacementVector[2] + TR2.displacementVector[2]
        self.rotationMatrix = self.rotationMatrix @ TR2.rotationMatrix

    def __repr__(self):
        return (
            f"TR: {self.displacementVector}, "
            f"{self.rotationMatrix.tolist()}, "
            f"{self.displacementOrigin}"
        )

    def toOutputString(self):
        return (
            f"TR{self.transformationNumber} "
            f"{self.displacementVector[0]}  {self.displacementVector[1]} {self.displacementVector[2]} "
            f"{self.rotationMatrix[0][0]} {self.rotationMatrix[0][1]} {self.rotationMatrix[0][2]} "
            f"{self.rotationMatrix[1][0]} {self.rotationMatrix[1][1]} {self.rotationMatrix[1][2]} "
            f"{self.rotationMatrix[2][0]} {self.rotationMatrix[2][1]} {self.rotationMatrix[2][2]} "
            f"{self.displacementOrigin}"
        )


class TRCL(TR):
    def __init__(
        self,
        o1=0,
        o2=0,
        o3=0,
        rotxx=1,
        rotyx=0,
        rotzx=0,
        rotxy=0,
        rotyy=1,
        rotzy=0,
        rotxz=0,
        rotyz=0,
        rotzz=1,
        displacementOrigin=1,
        angles=False,
        reg=None,
        transformationNumber=None,
    ):
        super().__init__(
            o1,
            o2,
            o3,
            rotxx,
            rotyx,
            rotzx,
            rotxy,
            rotyy,
            rotzy,
            rotxz,
            rotyz,
            rotzz,
            displacementOrigin,
            angles,
            reg,
            transformationNumber,
        )

    def __repr__(self):
        return (
            f"TRCL: {self.displacementVector} "
            f"{self.rotationMatrix.tolist()} "
            f"{self.displacementOrigin}"
        )

    def toOutputString(self):
        return (
            f"TRCL{self.transformationNumber} "
            f"{self.displacementVector[0]}  {self.displacementVector[1]} {self.displacementVector[2]} "
            f"{self.rotationMatrix[0][0]} {self.rotationMatrix[0][1]} {self.rotationMatrix[0][2]} "
            f"{self.rotationMatrix[1][0]} {self.rotationMatrix[1][1]} {self.rotationMatrix[1][2]} "
            f"{self.rotationMatrix[2][0]} {self.rotationMatrix[2][1]} {self.rotationMatrix[2][2]} "
            f"{self.displacementOrigin}"
        )
