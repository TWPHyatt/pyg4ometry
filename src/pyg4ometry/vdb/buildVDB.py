import numpy as _np
import openvdb as _vdb
from pyg4ometry.visualisation import ViewerBase
from pyg4ometry import transformation as _transformation


class geometryVDB(ViewerBase):
    """
    VDB exporter for PyG4ometry geometry. Inherits mesh and placement storage from ViewerBase.
    Builds OpenVDB level set grids for the full geometry and per-material surfaces.
    """

    def __init__(self):
        super().__init__()

    def buildVDBGrids(self, voxelSize=2.0, halfWidth=3.0):
        """
        Build all OpenVDB grids: one per material and one combined geometry grid.
        Must call addLogicalVolume() first to populate mesh and placement data.
        :param voxelSize: voxel size in mm
        :param halfWidth: narrowband half-width in voxels
        """
        transform = _vdb.createLinearTransform(voxelSize)
        materialGrids = self._buildMaterialGrids(transform, halfWidth)
        geometryGrid = self._buildGeometryGrid(materialGrids)
        return [*materialGrids, geometryGrid]

    def _applyTransform(self, vertices, mtra, tra):
        """
        Apply a world-space placement transform to an array of vertices.
        :param vertices: array in local space
        :param mtra: 3x3 rotation matrix from instancePlacements
        :param tra: 3-vector translation from instancePlacements
        """
        return ((mtra @ vertices.T).T + tra).astype(_np.float32)

    def _meshesToPointsAndTriangles(self, meshNames):
        """
        Collect and concatenate world-space vertices and triangles for a
        list of mesh names, applying all instance transforms.
        :param meshNames: iterable of mesh name keys into self.localmeshes
        """
        allPoints = []
        allTriangles = []
        vertexOffset = 0

        for meshName in meshNames:
            if meshName not in self.localmeshes:
                continue

            mesh = self.localmeshes[meshName]
            vertices, polygons, _ = mesh.toVerticesAndPolygons()
            if not vertices or not polygons:
                continue

            pts = _np.array(vertices, dtype=_np.float64)
            tris = _np.array(polygons, dtype=_np.uint32)

            for placement in self.instancePlacements.get(meshName, []):
                mtra = placement["transformation"]
                tra = _np.array(placement["translation"], dtype=_np.float64)

                worldPts = self._applyTransform(pts, mtra, tra)
                allPoints.append(worldPts)
                allTriangles.append(tris + vertexOffset)
                vertexOffset += len(pts)

        if not allPoints:
            return None, None

        return (_np.concatenate(allPoints, axis=0), _np.concatenate(allTriangles, axis=0))

    def _buildMaterialGrids(self, transform, halfWidth=3.0):
        """
        Build one level set grid per unique material. Meshes sharing a material
        are merged by concatenating vertices and offsetting polygon indices.
        Instance transforms are applied so each grid is in world space.
        :param transform: openvdb linear transform
        :param halfWidth: narrowband half-width in voxels
        """
        # group mesh names by material
        materialToMeshNames = {}
        for meshName, matList in self.instanceMaterials.items():
            matName = matList[0]
            if matName not in materialToMeshNames:
                materialToMeshNames[matName] = []
            materialToMeshNames[matName].append(meshName)

        grids = []
        for matName, meshNames in materialToMeshNames.items():
            points, triangles = self._meshesToPointsAndTriangles(meshNames)
            if points is None:
                continue

            grid = _vdb.FloatGrid.createLevelSetFromPolygons(
                points=points, triangles=triangles, transform=transform, halfWidth=float(halfWidth)
            )
            grid.name = f"material_{matName}"
            grid["material"] = matName
            grid["grid_type"] = "material_levelset"
            grids.append(grid)

        return grids

    def _buildGeometryGrid(self, materialGrids=None):
        """
        Build the combined geometry grid by merging all per-material level sets
        using CSG union (minimum value at each voxel). This preserves every
        surface from every material grid in the combined result.

        Taking the minimum of two signed distance fields at each voxel gives
        the CSG union (both zero crossings (surfaces) are preserved because
        whichever surface is closer at any given voxel wins).

        Note: combine() leaves the source grid (b) empty after the operation,
        so work on deep copies to preserve the original material grids.

        :param materialGrids: list of per-material FloatGrids already built
        """
        if not materialGrids:
            return None

        # deep copy the first grid as the starting point so the original
        # material grid is not emptied by combine()
        combined = materialGrids[0].deepCopy()
        combined.name = "geometry_all"
        combined["grid_type"] = "geometry_levelset"

        for g in materialGrids[1:]:
            # deep copy each source grid before combining because
            # combine() empties grid b as a side effect
            gCopy = g.deepCopy()
            combined.combine(gCopy, lambda a, b: min(a, b))

        return combined

    def verifyGeometryGrid(self, materialGrids, geometryGrid):
        """
        Verify that geometry_all contains the surfaces of all material grids
        by comparing active voxel counts and bounding boxes.

        A correct geometry_all should:
        - have an active voxel count >= any individual material grid
        - have a bounding box that contains all material grid bounding boxes
        - have the same bounding box as the largest material grid

        :param materialGrids: list of per-material FloatGrids
        :param geometryGrid: the combined geometry_all FloatGrid
        """
        # print("[VDB] Geometry grid verification")
        # print("-" * 50)

        geomBB = geometryGrid.evalActiveVoxelBoundingBox()
        geomCount = geometryGrid.activeVoxelCount()

        # print(f"geometry_all: {geomCount} active voxels, bb={geomBB}")
        # print()

        allContained = True
        for g in materialGrids:
            matBB = g.evalActiveVoxelBoundingBox()
            matCount = g.activeVoxelCount()

            # check bounding box is contained within geometry_all bounding box
            bbContained = (
                matBB[0][0] >= geomBB[0][0]
                and matBB[0][1] >= geomBB[0][1]
                and matBB[0][2] >= geomBB[0][2]
                and matBB[1][0] <= geomBB[1][0]
                and matBB[1][1] <= geomBB[1][1]
                and matBB[1][2] <= geomBB[1][2]
            )

            # check geometry_all has at least as many voxels as this material
            countOk = geomCount >= matCount

            status = "OK" if (bbContained and countOk) else "FAIL"
            # print(f"  {g.name}: {matCount} active voxels, bb={matBB} [{status}]")

            if not bbContained:
                # print(f"    WARNING: bounding box not contained in geometry_all")
                allContained = False
            if not countOk:
                # print(f"    WARNING: geometry_all has fewer voxels than this material grid")
                allContained = False

        # print()
        if allContained:
            pass
            # print("[VDB] verification PASSED: geometry_all contains all material surfaces")
        else:
            pass
            # print("[VDB] verification FAILED: some material surfaces missing from geometry_all")
        # print("-" * 50)
