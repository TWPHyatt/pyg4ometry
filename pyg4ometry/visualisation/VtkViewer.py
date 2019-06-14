import numpy as _np
import vtk as _vtk
import pyg4ometry.transformation as _transformation
import logging as _log

class VtkViewer:
    def __init__(self,size=(1024,768)):
        
        # create a renderer
        self.ren = _vtk.vtkRenderer()
        
        # create a rendering window
        self.renWin = _vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)

        # create a rendering window interactor 
        self.iren = _vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        self.ren.SetBackground(1.0, 1.0, 1.0)
        self.renWin.SetSize(*size)

        # local meshes 
        self.localmeshes = {}
        self.localmeshesOverlap = {}

        # filters (per mesh)
        self.filters = {}
        self.filtersOverlap = {}
        
        # mappers (per mesh) 
        self.mappers = []
        self.physicalMapperMap = {}
        self.mappersOverlap = []
        self.physicalMapperMapOverlap = {}

        # actors (per placement) 
        self.actors = []
        self.physicalActorMap = {}
        self.actorsOverlap = [] 
        self.physicalActorMapOverlap = {}

    def addAxes(self, length = 20.0, origin = (0,0,0)):
        self.axes = _vtk.vtkAxesActor()
        # axes.SetTotalLength([self.xrange,self.yrange,self.xrange]);
        self.axes.SetTotalLength(length,length,length)
        self.axes.SetOrigin(origin[0], origin[1], origin[2])
        self.ren.AddActor(self.axes)
        
    def setOpacity(self,v):
        for a in self.actors:
            p = a.GetProperty().SetOpacity(v)
    
    def addLogicalVolume(self, logical, mrot=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra=_np.array([0,0,0])) :
        if logical.type == "logical" :
            self.addLogicalVolumeBounding(logical)
        self.addLogicalVolumeRecursive(logical, mrot, tra)

    def addLogicalVolumeBounding(self, logical):
        # add logical solid as wireframe 
        lvm    = logical.mesh.localmesh
        lvmPD  = pycsgMeshToVtkPolyData(lvm)
        lvmFLT = _vtk.vtkTriangleFilter()
        lvmFLT.AddInputData(lvmPD)        
        lvmMAP = _vtk.vtkPolyDataMapper()
        lvmMAP.ScalarVisibilityOff()
        lvmMAP.SetInputConnection(lvmFLT.GetOutputPort())        
        lvmActor = _vtk.vtkActor()
        lvmActor.SetMapper(lvmMAP)         
        lvmActor.GetProperty().SetRepresentationToWireframe()
        self.ren.AddActor(lvmActor)
        
    def addLogicalVolumeRecursive(self, logical, mrot = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra = _np.array([0,0,0])):
        for pv in logical.daughterVolumes:
            if pv.logicalVolume.type == "logical":
                _log.info('VtkViewer.addLogicalVolume> Daughter %s %s %s ' % (pv.name, pv.logicalVolume.name, pv.logicalVolume.solid.name))
            elif pv.logicalVolume.type == "assembly":
                _log.info('VtkViewer.addLogicalVolume> Daughter %s %s' % (pv.name, pv.logicalVolume.name))
                self.addLogicalVolumeRecursive(pv.logicalVolume, mrot, tra)
                continue

            # get the local vtkPolyData
            solid_name = pv.logicalVolume.solid.name
            pv_name = pv.name

            if pv.type == "placement":
                # pv transform
                pvmrot = _transformation.tbxyz2matrix(pv.rotation.eval())
                pvtra = _np.array(pv.position.eval())
                
                # pv compound transform
                new_mrot = mrot * pvmrot
                new_tra = (_np.array(mrot.dot(pvtra)) + tra)[0]

                mesh = pv.logicalVolume.mesh.localmesh
                self.addMesh(pv_name, solid_name, mesh, new_mrot, new_tra, self.localmeshes, self.filters, 
                             self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap)
                self.addLogicalVolumeRecursive(pv.logicalVolume,new_mrot,new_tra)
            elif pv.type == "replica":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0])
                    pvtra = _np.array(trans[1])
                    
                    # pv compound transform
                    new_mrot = mrot * pvmrot
                    new_tra = (_np.array(mrot.dot(pvtra)) + tra)[0]                    

                    self.addMesh(pv_name, mesh.solid.name, mesh.localmesh, new_mrot, new_tra, self.localmeshes, self.filters, 
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap)                    
            elif pv.type == "parametrised":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0].eval())
                    pvtra = _np.array(trans[1].eval())

                    # pv compound transform
                    new_mrot = mrot * pvmrot
                    new_tra = (_np.array(mrot.dot(pvtra)) + tra)[0]

                    self.addMesh(pv_name, mesh.solid.name, mesh.localmesh, new_mrot, new_tra, self.localmeshes,
                                 self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap)
            elif pv.type == "division":
                pass


    def addMesh(self, pv_name, solid_name, mesh, mrot, tra, localmeshes, filters, 
                mappers, mapperMap, actors, actorMap, visOptions = None):
        # VtkPolyData : check if mesh is in localmeshes dict
        _log.info('VtkViewer.addLogicalVolume> vtkPD')

        if localmeshes.has_key(solid_name) :
            vtkPD = localmeshes[solid_name]
        else : 
            vtkPD = pycsgMeshToVtkPolyData(mesh)
            localmeshes[solid_name] = vtkPD    
        
        # Filter : check if filter is in the filters dict 
        _log.info('VtkViewer.addLogicalVolume> vtkFLT')
        filtername = solid_name+"_filter"
        if filters.has_key(filtername) :
            vtkFLT = filters[filtername]
        else : 
            vtkFLT = _vtk.vtkTriangleFilter()
            vtkFLT.AddInputData(vtkPD)                    
            filters[filtername]  = vtkFLT

        # Mapper 
        _log.info('VtkViewer.addLogicalVolume> vtkMAP')            
        mappername = pv_name+"_mapper" 
        vtkMAP = _vtk.vtkPolyDataMapper()
        vtkMAP.ScalarVisibilityOff()
        vtkMAP.SetInputConnection(vtkFLT.GetOutputPort())
        mappers.append(vtkMAP)

        if not mapperMap.has_key(mappername) :
            mapperMap[mappername] = vtkMAP
            
        # Actor
        actorname = pv_name+"_actor"             
        vtkActor = _vtk.vtkActor() 
        vtkActor.SetMapper(vtkMAP)        
        rotaa = _transformation.matrix2axisangle(mrot)  
        vtkActor.SetPosition(tra[0],tra[1],tra[2])
        vtkActor.RotateWXYZ(-rotaa[1]/_np.pi*180.0,rotaa[0][0],rotaa[0][1],rotaa[0][2])

        if not actorMap.has_key(actorname) :
            actorMap[actorname] = vtkActor
    
        # set visualisation properties
        if visOptions :             
            vtkActor.GetProperty().SetColor(visOptions.color[0],
                                            visOptions.color[1],
                                            visOptions.color[2])
            vtkActor.GetProperty().SetOpacity(visOptions.alpha)
            if visOptions.representation == "surface" :
                vtkActor.GetProperty().SetRepresentationToSurface()
            elif visOptions.representation == "wireframe" :
                vtkActor.GetProperty().SetRepresentationToWireframe()
        else : 
            vtkActor.GetProperty().SetColor(1,0,0)

        actors.append(vtkActor)
        self.ren.AddActor(vtkActor)

        
    def view(self, interactive = True):
        # enable user interface interactor
        # self.iren.Initialize()

        # Camera setup
        camera =_vtk.vtkCamera();
        self.ren.SetActiveCamera(camera);
        self.ren.ResetCamera()

        # Render 
        self.renWin.Render()

        if interactive : 
            self.iren.Start()    

    '''
    def addLogicalVolumeOld(self, logical, mrot=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra=_np.array([0,0,0])) :
        if logical.type == "logical" : 
            self.addLogicalVolumeBounding(logical)
        self.addLogicalVolumeRecursive(logical, mrot, tra)
    
    def addLogicalVolumeRecursiveOld(self, logical, mrot = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra = _np.array([0,0,0])):
        _log.info('VtkViewer.addLogicalVolume> %s' % (logical.name))

        for pv in logical.daughterVolumes : 

            # pv transform 
            pvmrot = _transformation.tbxyz2matrix(pv.rotation.eval())
            pvtra = _np.array(pv.position.eval())

            # pv compound transform 
            new_mrot = mrot*pvmrot
            new_tra = (_np.array(mrot.dot(pvtra)) + tra)[0]
  
            if pv.logicalVolume.type == "logical" : 
                _log.info('VtkViewer.addLogicalVolume> Daughter %s %s %s ' % (pv.name, pv.logicalVolume.name, pv.logicalVolume.solid.name))
            elif pv.logicalVolume.type == "assembly" : 
                _log.info('VtkViewer.addLogicalVolume> Daughter %s %s' % (pv.name, pv.logicalVolume.name))
                self.addLogicalVolumeRecursive(pv.logicalVolume,new_mrot,new_tra)
                continue

            # get the local vtkPolyData 
            _log.info('VtkViewer.addLogicalVolume> vtkPD')
            solidname = pv.logicalVolume.solid.name
            try : 
                vtkPD = self.localmeshes[solidname]
            except KeyError : 
                localmesh = pv.logicalVolume.mesh.localmesh
                vtkPD     = pycsgMeshToVtkPolyData(localmesh)
                self.localmeshes[solidname] = vtkPD

            # get the local overlap vtkPolyData
            try : 
                vtkPDOverlap = self.localmeshesOverlap[solidname] 
            except KeyError : 
                localmeshOverlap = pv.logicalVolume.mesh.overlapmeshes
                vtkPDOverlap = [] 
                for mol in localmeshOverlap : 
                    vtkPDOverlap.append(pycsgMeshToVtkPolyData(mol))
                    self.localmeshesOverlap[solidname] = vtkPDOverlap

            # triangle filter    
            _log.info('VtkViewer.addLogicalVolume> vtkFLT')
            filtername = solidname+"_filter"
            try : 
                vtkFLT = self.filters[filtername] 
            except KeyError :  
                vtkFLT = _vtk.vtkTriangleFilter()
                vtkFLT.AddInputData(vtkPD)
                # vtkFLT.Update()
                self.filters[filtername] = vtkFLT

            # triangle filters for overlaps 
            try : 
                vtkFLTOverlap = self.filtersOverlap[filtername] 
            except KeyError : 
                self.filtersOverlap[filtername] = []
                for pdo in vtkPDOverlap : 
                    vtkFLTOverlap = _vtk.vtkTriangleFilter()
                    vtkFLTOverlap.AddInputData(pdo)
                    self.filtersOverlap[filtername].append(vtkFLTOverlap)
            
            # mapper 
            _log.info('VtkViewer.addLogicalVolume> vtkMAP')

            mappername = solidname+"_mapper" 
            vtkMAP = _vtk.vtkPolyDataMapper()
            vtkMAP.ScalarVisibilityOff()
            vtkMAP.SetInputConnection(vtkFLT.GetOutputPort())
            self.mappers.append(vtkMAP)

            # mapper for overlaps 
            vtkMAPOverlaps = [] 
            for flt in self.filtersOverlap[filtername] :                 
                vtkMAPOverlap = _vtk.vtkPolyDataMapper() 
                vtkMAPOverlap.ScalarVisibilityOff()
                vtkMAPOverlap.SetInputConnection(flt.GetOutputPort())
                self.mappersOverlap.append(vtkMAPOverlap)
                vtkMAPOverlaps.append(vtkMAPOverlap)
            
            # mapper look up dictionary 
            try : 
                self.physicalMapperMap[pv.name].append(vtkMAP)
            except KeyError : 
                self.physicalMapperMap[pv.name] = [vtkMAP]
            
            # actor
            _log.info('VtkViewer.addLogicalVolume> vtkActor')

            actorname = pv.name+"_actor"             
            vtkActor = _vtk.vtkActor() 

            # store actor (need to increment count if exists)
            self.actors.append(vtkActor)
            
            # actor look up dictionary
            try : 
                self.physicalActorMap[pv.name].append(vtkActor)
            except KeyError : 
                self.physicalActorMap[pv.name] = [vtkActor]

            vtkActor.SetMapper(vtkMAP)        

            rotaa = _transformation.matrix2axisangle(new_mrot)

            vtkActor.SetPosition(new_tra[0],new_tra[1],new_tra[2])
            vtkActor.RotateWXYZ(-rotaa[1]/_np.pi*180.0,rotaa[0][0],rotaa[0][1],rotaa[0][2])

            # set visualisation properties
            vtkActor.GetProperty().SetColor(pv.visOptions.color[0],
                                            pv.visOptions.color[1],
                                            pv.visOptions.color[2])
            vtkActor.GetProperty().SetOpacity(pv.visOptions.alpha)
            if pv.visOptions.representation == "surface" :
                vtkActor.GetProperty().SetRepresentationToSurface()
            elif pv.visOptions.representation == "wireframe" :
                vtkActor.GetProperty().SetRepresentationToWireframe()
            
            _log.info('VtkViewer.addLogicalVolume> Add actor')
            self.ren.AddActor(vtkActor)

            # actors for overlaps 
            for m in vtkMAPOverlaps : 
                vtkActorOverlap = _vtk.vtkActor() 
                self.actorsOverlap.append(vtkActorOverlap)
                vtkActorOverlap.SetMapper(m)
                vtkActorOverlap.SetPosition(new_tra[0],new_tra[1],new_tra[2])
                vtkActorOverlap.RotateWXYZ(rotaa[1]/_np.pi*180.0,rotaa[0][0],rotaa[0][1],rotaa[0][2])
                vtkActorOverlap.GetProperty().SetColor(1,0,0)
                self.ren.AddActor(vtkActorOverlap)

            self.addLogicalVolumeRecursive(pv.logicalVolume,new_mrot,new_tra)
    '''            
        
# python iterable to vtkIdList
def mkVtkIdList(it):
    vil = _vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil

# convert pycsh mesh to vtkPolyData
def pycsgMeshToVtkPolyData(mesh):

    # refine mesh 
    # mesh.refine()

    verts, cells, count = mesh.toVerticesAndPolygons()
    meshPolyData = _vtk.vtkPolyData() 
    points       = _vtk.vtkPoints()
    polys        = _vtk.vtkCellArray()
    scalars      = _vtk.vtkFloatArray()

    for v in verts :
        points.InsertNextPoint(v)

    for p in cells :
        polys.InsertNextCell(mkVtkIdList(p))

    for i in range(0,count) :
        scalars.InsertTuple1(i,1)

    meshPolyData.SetPoints(points)
    meshPolyData.SetPolys(polys)
    meshPolyData.GetPointData().SetScalars(scalars)

    del points
    del polys
    del scalars
        
    return meshPolyData

def writeVtkPolyDataAsSTLFile(fileName, meshes):
# Convert vtkPolyData to STL mesh
    ''' meshes : list of triFilters '''

    appendFilter = _vtk.vtkAppendPolyData()

    for m in meshes:
        if m :
            appendFilter.AddInputConnection(m.GetOutputPort())

    # append mesh to filter
    appendFilter.Update()

    # remove duplicate points
    cleanFilter = _vtk.vtkCleanPolyData()
    cleanFilter.SetInputConnection(appendFilter.GetOutputPort())
    cleanFilter.Update()

    # write STL file
    print 'stlWriter'
    stlWriter = _vtk.vtkSTLWriter()
    print 'setFileName'
    stlWriter.SetFileName(fileName)
    print 'inputConnection'
    stlWriter.SetInputConnection(appendFilter.GetOutputPort())
    print 'write'
    stlWriter.Write()
    print 'done'
    return stlWriter
