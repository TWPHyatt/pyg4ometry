from .Material import Material
from .Transformation import TRCL
from .Surfaces import Intersection, Union, Complement, Surface
import pyg4ometry


class Cell:
    def __init__(
        self,
        surfaces=None,
        geometry=None,
        reg=None,
        cellNumber=None,
        material=None,
        cellChildren=None,
        importance=None,
        transformation=None,
    ):
        self.surfaceList = (
            [] if surfaces is None else surfaces
        )  # todo can I delete? (replace writer surface list with geometry walk, bottom of tree surfaces)
        self.cellNumber = cellNumber
        self.geometry = geometry
        self.material = material
        self.cellChildrenList = [] if cellChildren is None else cellChildren
        self.importance = [] if importance is None else importance
        self.reg = reg
        self.transformation = transformation
        if importance:
            self.importance = [importance]
        if reg:
            reg.addCell(self)
            self.reg = reg

    def copy(self):
        """
        returns a copy of the cell, disconnected in memory
        """

        # SORT SURFACE NUMBERS AND CELL NUMBERS
        # NEED A NEW UNIQUE CELL FOR THE CELL
        # NEED NEW UNIQUE SURFACE NUMBERS FOR ITS SURFACES

        cell_p = Cell(
            surfaces=self.surfaces,
            geometry=self.geometry,
            reg=self.reg,
            cellNumber=self.cellNumber,
            material=self.material,
            cellChildren=self.cellChildren,
            importance=self.importance,
        )

        return cell_p

    def addChildCell(self, childCell):
        if childCell.geometry is None:
            msg = f"The child cell geometry is None"
            raise TypeError(msg)
        self.geometry = pyg4ometry.mcnp.Intersection(
            self.geometry, pyg4ometry.mcnp.Complement(childCell.geometry)
        )
        self.cellChildrenList.append(childCell)
        """
        for childSurface in childCell.surfaceList:
            if childSurface in self.surfaceList:
                self.surfaceList.remove(childSurface)
        """

        if self.reg:
            surfaceUpdateReg = []
            surfaceAddReg = []
            for regSurface in self.reg.surfaceDict:
                for childSurface in childCell.surfaceList:
                    if regSurface == childSurface:
                        surfaceUpdateReg.append(childSurface)
                    else:
                        surfaceAddReg.append(childSurface)

            self.reg.addSurfaces(surfaceUpdateReg, replace=True)
            self.reg.addSurfaces(surfaceAddReg, replace=False)

    def transform(
        self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0], angles=False
    ):
        """
        transform cell
        """
        TRCL1 = TRCL(
            *translation, *rotation[0], *rotation[1], *rotation[2], angles=angles, reg=self.reg
        )

        if self.reg:
            if TRCL1 not in self.reg.transformationDict:
                self.reg.addTransformation(TRCL1)

        if self.transformation:
            self.transformation.compositeTR(TRCL1)
        else:
            self.transformation = TRCL1

        # apply cell transform to all surfaces of the cell
        self._walkGeometryTreeAndTransformSurfaces(self.geometry, TRCL1)

        # if cell has children cells, need to go down hierarchy and apply composite transforms to surfaces
        if self.cellChildrenList is not None:
            for childCell in self.cellChildrenList:
                childCell._walkGeometryTreeAndTransformSurfaces(childCell.geometry, TRCL1)

    def _walkGeometryTreeAndTransformSurfaces(self, geometry, TRCL1):
        """
        walk geometry tree and at each surface apply the transformation to the surface
        """
        if isinstance(geometry, Surface):
            geometry.transform(rotation=TRCL1.rotationMatrix, translation=TRCL1.displacementVector)
        elif isinstance(geometry, Intersection):
            self._walkGeometryTreeAndTransformSurfaces(geometry.left, TRCL1)
            self._walkGeometryTreeAndTransformSurfaces(geometry.right, TRCL1)
        elif isinstance(geometry, Union):
            self._walkGeometryTreeAndTransformSurfaces(geometry.left, TRCL1)
            self._walkGeometryTreeAndTransformSurfaces(geometry.right, TRCL1)
        elif isinstance(geometry, Complement):
            self._walkGeometryTreeAndTransformSurfaces(geometry.item, TRCL1)

    def _walkCellHierarchyAndTransformSurfaces(self, geometry, TRCL1):
        """
        1. walk cell hierarchy
        2. stack the composite transformations recursively down the cell hierarchy
        3. at each surface apply the composite transformation SO FAR transformation to the surface
        """
        if isinstance(geometry, Surface):
            geometry.transform(rotation=None, translation=None)
        elif isinstance(geometry, Intersection):
            self._walkGeometryTreeAndTransformSurfaces(geometry.left, TRCL1)
            self._walkGeometryTreeAndTransformSurfaces(geometry.right, TRCL1)
        elif isinstance(geometry, Union):
            self._walkGeometryTreeAndTransformSurfaces(geometry.left, TRCL1)
            self._walkGeometryTreeAndTransformSurfaces(geometry.right, TRCL1)
        elif isinstance(geometry, Complement):
            self._walkGeometryTreeAndTransformSurfaces(geometry.item, TRCL1)

    def _bakeTransform(self):
        # cannot have TRCL number >999
        # so when reaching this limit we can instead bake-in the TRCL transforms
        # it will need to edit the surfaces of the cells and transform them according to the TRCL

        # easiest way to do this:
        #   - copy the cell
        #   - add a transformation to the surfaces in the copied cell, this transformation is the TRCL
        pass

    def addSurface(self, surface):
        if self.reg:
            if surface in self.reg.surfaceDict:
                surface = self.reg.surfaceDict[surface]
        self.surfaceList.append(surface)

    def addSurfaces(self, surfaces):
        for i, s in enumerate(surfaces):
            if s in self.reg.surfaceDict:
                surfaces[i] = self.reg.surfaceDict[s]
        self.surfaceList.extend(surfaces)

    def addMacrobody(self, macrobody):
        self.addSurface(macrobody)

    def addMacrobodies(self, macrobody):
        self.addSurfaces(macrobody)

    def addMaterial(self, material):
        self.material = material

    def addGeometry(self, geometry):
        self.geometry = geometry

    # there are multiple keyword parameters than can be added
    # reader "cellParams" dictionary
    # maybe this should be an addParamerter function?
    def addImportance(self, importance):
        if (self.material.materialNumber == 0) and (importance.xj != (0,)):
            # print(importance.xj)
            importance.xj = 0
            # print("Cell", self.cellNumber, "is void")
            # print(" > Overriding importance and setting to zero.")
        self.importance.append(importance)

    def toOutputString(self):
        return str(self.cellNumber)

    def mesh(self):
        return self.geometry.mesh()


class IMP:
    def __init__(self, pl, *xj):
        self.pl = pl
        self.xj = xj

    # todo the WWN card (presence of a WWN card will change IMP - manual 3.3.6.1)

    def toOutputString(self):
        x = ""
        if hasattr(self.xj, "__iter__"):
            if len(self.xj) > 1:
                for j in self.xj:
                    x += " " + str(j)
                return "IMP:" + str(self.pl) + x
            else:
                x = str(*self.xj)
                return "IMP:" + str(self.pl) + "=" + x
        else:
            x = str(self.xj)
            return "IMP:" + str(self.pl) + "=" + x
