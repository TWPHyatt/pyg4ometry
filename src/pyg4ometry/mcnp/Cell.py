from .Material import Material
import pyg4ometry.mcnp


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
    ):
        self.surfaceList = (
            [] if surfaces is None else surfaces
        )  # todo can I delete? (replace writer surface list with geometry walk, bottom of tree surfaces)
        self.cellNumber = cellNumber
        self.geometry = geometry
        self.material = material
        self.cellChildrenList = [] if cellChildren is None else cellChildren
        self.importance = [] if importance is None else [importance]
        self.reg = reg
        if importance:
            self.importance = [importance]
        if reg:
            reg.addCell(self)
            self.reg = reg

    def addChildCell(self, childCell):
        if childCell.geometry is None:
            msg = f"The child cell geometry is None"
            raise TypeError(msg)
        self.geometry = pyg4ometry.mcnp.Intersection(
            self.geometry, pyg4ometry.mcnp.Complement(childCell.geometry)
        )
        self.cellChildrenList.append(childCell)
        for childSurface in childCell.surfaceList:
            if childSurface in self.surfaceList:
                self.surfaceList.remove(childSurface)

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

    def transformCell(self, rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation=[0, 0, 0]):
        surfaces_p = []
        for surface in self.surfaceList:
            surfaces_p.append(surface.transform(rotation=rotation, translation=translation))

        cell_p = Cell(
            surfaces=surfaces_p,
            geometry=self.geometry,
            reg=self.reg,
            cellNumber=self.cellNumber,
            material=self.material,
            cellChildren=self.cellChildrenList,
            importance=self.importance,
        )

        return cell_p

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

    def addDensity(self, density):
        self.density = density

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
