import fme
import fmeobjects
import uuid
import time
import tempfile
import ifcopenshell
import ifcopenshell.geom


class FeatureProcessor(object):
    
    def input(self, feature):    
    
        O = 0., 0., 0.
        X = 1., 0., 0.
        Y = 0., 1., 0.
        Z = 0., 0., 1.
   
        # Helper function definitions

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

        # Creates an IfcPolyLine from a list of points, specified as Python tuples
        def create_ifcpolyline(ifcfile, point_list):
            ifcpts = []
            for point in point_list:
                point = ifcfile.createIfcCartesianPoint(point)
                ifcpts.append(point)
            polyline = ifcfile.createIfcPolyLine(ifcpts)
            return polyline
            
        # Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples
        def create_ifcextrudedareasolid(ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
            polyline = create_ifcpolyline(ifcfile, point_list)
            ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
            ifcdir = ifcfile.createIfcDirection(extrude_dir)
            ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
            return ifcextrudedareasolid


        create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)
        

        # Obtain references to master file
        filename = FME_MacroValues['OUTPUT_FILE_PATH']
        ifcfile = ifcopenshell.open(filename)
        owner_history = ifcfile.by_type("IfcOwnerHistory")[0]
        project = ifcfile.by_type("IfcProject")[0]
        context = ifcfile.by_type("IfcGeometricRepresentationContext")[0]
        
        building_storey = ifcfile.by_guid(feature.getAttribute('storey_guid'))
        
        wall = ifcfile.by_guid(feature.getAttribute('wall_guid')) 
        wall_placement = wall.ObjectPlacement
   
 
        # create point list for polyline
        p0 = feature.getAttribute('axis_polyline{0}').split(',')
        point0 = [float(x) for x in p0]
        
        p1 = feature.getAttribute('axis_polyline{1}').split(',')
        point1 = [float(x) for x in p1]  

     
        # Create and associate an opening for the window in the wall
        opening_placement = create_ifclocalplacement(ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), wall_placement)
        opening_extrusion_placement = create_ifcaxis2placement(ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
        point_list_opening_extrusion_area = [feature.getAttribute('p0'), feature.getAttribute('p1'), feature.getAttribute('p2'), feature.getAttribute('p3'), feature.getAttribute('p4')]
        opening_solid = create_ifcextrudedareasolid(ifcfile, point_list_opening_extrusion_area, opening_extrusion_placement, (0.0, 0.0, 1.0), feature.getAttribute('Dimensions.Height'))
        opening_representation = ifcfile.createIfcShapeRepresentation(context, "Body", "SweptSolid", [opening_solid])
        opening_shape = ifcfile.createIfcProductDefinitionShape(None, None, [opening_representation])
        opening_element = ifcfile.createIfcOpeningElement(create_guid(), owner_history, "Opening", "An awesome opening", None, opening_placement, opening_shape, None, "OPENING")
        ifcfile.createIfcRelVoidsElement(create_guid(), owner_history, None, None, wall, opening_element)


        s = ifcopenshell.geom.settings()
        s.set(s.DISABLE_TRIANGULATION, True)
        s.set(s.USE_BREP_DATA, True)
        
        schema = ifcfile.schema
        geo = feature.getGeometry()
        w = ifcopenshell.geom.serialise(schema, "IfcWindow").geo
        
        
      
   
        # Create a simplified representation for the Window
        #window_placement = create_ifclocalplacement(ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), opening_placement)
        #window_extrusion_placement = create_ifcaxis2placement(ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
        #point_list_window_extrusion_area = [feature.getAttribute('p0'), feature.getAttribute('p1'), feature.getAttribute('p2'), feature.getAttribute('p3'), feature.getAttribute('p4')]
        #window_solid = create_ifcextrudedareasolid(ifcfile, point_list_window_extrusion_area, window_extrusion_placement, (0.0, 0.0, 1.0), feature.getAttribute('Dimensions.Height'))
        #window_representation = ifcfile.createIfcShapeRepresentation(context, "Body", "SweptSolid", [w])
        #window_shape = ifcfile.createIfcProductDefinitionShape(None, None, [window_representation])
        #window = ifcfile.createIfcWindow(create_guid(), owner_history, feature.getAttribute('FamilyType'), feature.getAttribute('Family'), None, window_placement, window_shape, None, None)


        # Relate the window to the opening element
        #ifcfile.createIfcRelFillsElement(create_guid(), owner_history, None, None, opening_element, window)
        # Relate the window and wall to the building storey
        #ifcfile.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, "Building Storey Container", None, [wall, window], building_storey)

  

        #feature.setAttribute('testwindow', str(new_window))
        feature.setAttribute('windowgeo', str(geo))
        #feature.setAttribute('window_geom_temp1', str(window_geom_temp1))
        feature.setAttribute('wall_placement', str(wall_placement))
        #feature.setAttribute('point_list_opening_extrusion_area', str(point_list_opening_extrusion_area))

        # Write the contents of the file to disk
         
        #ifcfile.write(filename)        

        self.pyoutput(feature)

        def close(self):

            pass

        def process_group(self):

            pass
