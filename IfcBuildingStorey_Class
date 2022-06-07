import fme
import fmeobjects
import uuid
import time
import tempfile
import ifcopenshell


class FeatureProcessor(object):
    
    def input(self, feature):    
    
        create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)
        

        filename = feature.getAttribute('path_rootname')+"_FME.ifc"
        ifcfile = ifcopenshell.open(filename)

        
        # Helper function definitions
     
        O = 0., 0., 0.
        X = 1., 0., 0.
        Y = 0., 1., 0.
        Z = 0., 0., 1.       
  
        # Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples
        def create_ifcaxis2placement(ifcfile, point=O, dir1=Z, dir2=X):
            point = ifcfile.createIfcCartesianPoint(point)
            dir1 = ifcfile.createIfcDirection(dir1)
            dir2 = ifcfile.createIfcDirection(dir2)
            axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
            return axis2placement

        # Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
        def create_ifclocalplacement(ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
            axis2placement = create_ifcaxis2placement(ifcfile,point,dir1,dir2)
            ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,axis2placement)
            return ifclocalplacement2
     
        # Obtain references for IfcBuildingStorey
        ifcfile = ifcopenshell.open(filename)
        owner_history = ifcfile.by_type("IfcOwnerHistory")[0]
        building = ifcfile.by_type("IfcBuilding")[0]
        building_placement = building.ObjectPlacement
        storey_placement = create_ifclocalplacement(ifcfile, relative_to=building_placement)
        elevation = float(feature.getAttribute('Elevation'))
        building_storey = ifcfile.createIfcBuildingStorey(create_guid(), owner_history, feature.getAttribute('_list'), None, None, storey_placement, None, None, "ELEMENT", elevation)

        container_storey = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])
  

        # Write the contents of the file to disk
        ifcfile.write(filename)

        self.pyoutput(feature)

    def close(self):

        pass

    def process_group(self):

        pass
