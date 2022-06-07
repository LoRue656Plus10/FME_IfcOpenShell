import fme
import fmeobjects
import uuid
import time
import tempfile
import ifcopenshell
import sys


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
        
        # IFC template creation

        filename = feature.getAttribute('path_rootname')+"_FME.ifc"
        timestamp = int(time.time())
        timestring = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(timestamp))
        creator = "LRouth"
        organization = "SkunkWorks"
        application, application_version = "IfcOpenShell", "0.5"
        project_globalid, project_name = create_guid(), "FME_Python_IFC"
            
        # A template IFC file to quickly populate entity instances for an IfcProject with its dependencies
        template = """ISO-10303-21;
        HEADER;
        FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
        FILE_NAME('%(filename)s','%(timestring)s',('%(creator)s'),('%(organization)s'),'%(application)s','%(application)s','');
        FILE_SCHEMA(('IFC4'));
        ENDSEC;
        DATA;
        #1=IFCPERSON($,$,'%(creator)s',$,$,$,$,$);
        #2=IFCORGANIZATION($,'%(organization)s',$,$,$);
        #3=IFCPERSONANDORGANIZATION(#1,#2,$);
        #4=IFCAPPLICATION(#2,'%(application_version)s','%(application)s','');
        #5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,#3,#4,%(timestamp)s);
        #6=IFCDIRECTION((1.,0.,0.));
        #7=IFCDIRECTION((0.,0.,1.));
        #8=IFCCARTESIANPOINT((0.,0.,0.));
        #9=IFCAXIS2PLACEMENT3D(#8,#7,#6);
        #10=IFCDIRECTION((0.,1.,0.));
        #11=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#9,#10);
        #12=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
        #13=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
        #14=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
        #15=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
        #16=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
        #17=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
        #18=IFCCONVERSIONBASEDUNIT(#12,.PLANEANGLEUNIT.,'DEGREE',#17);
        #19=IFCUNITASSIGNMENT((#13,#14,#15,#18));
        #20=IFCPROJECT('%(project_globalid)s',#5,'%(project_name)s',$,$,$,$,(#11),#19);
        ENDSEC;
        END-ISO-10303-21;
        """ % locals()

        # Write the template to a temporary file 
        temp_handle, temp_filename = tempfile.mkstemp(suffix=".ifc")
        with open(temp_filename, "w") as f:
            f.write(template)
         
        # Obtain references to instances defined in template
        ifcfile = ifcopenshell.open(temp_filename)
        owner_history = ifcfile.by_type("IfcOwnerHistory")[0]
        project = ifcfile.by_type("IfcProject")[0]
        context = ifcfile.by_type("IfcGeometricRepresentationContext")[0]
        ifcfile_path = tempfile.NamedTemporaryFile()
        tempfilename = ifcfile_path.name

        if feature.getAttribute('ProjectUnit') != "METRE":
            dimex_length = ifcfile.createIfcDimensionalExponents(1,0,0,0,0,0,0)
            length_measure = ifcfile.createIfcLengthMeasure(0.0254)
            mwu_length = ifcfile.createIfcMeasureWithUnit(length_measure, ifcfile.by_type("IfcSIUnit")[0])
            length_unit = ifcfile.createIfcConversionBasedUnit(dimex_length, "LENGTHUNIT", feature.getAttribute('ProjectUnit'), mwu_length)
            
            dimex_area = ifcfile.createIfcDimensionalExponents(2,0,0,0,0,0,0)           
            area_measure = ifcfile.createIfcRatioMeasure(0.09290304)
            mwu_area = ifcfile.createIfcMeasureWithUnit(area_measure, ifcfile.by_type("IfcSIUnit")[1])            
            area_unit = ifcfile.createIfcConversionBasedUnit(dimex_area,"AREAUNIT",'SQUARE FOOT', mwu_area)
            
            dimex_cube = ifcfile.createIfcDimensionalExponents(3,0,0,0,0,0,0)
            cube_measure = ifcfile.createIfcRatioMeasure(0.028316846592)
            mwu_cube = ifcfile.createIfcMeasureWithUnit(cube_measure, ifcfile.by_type("IfcSIUnit")[2])            
            volume_unit = ifcfile.createIfcConversionBasedUnit(dimex_cube,"VOLUMEUNIT",'CUBIC FOOT', mwu_cube)
            
            unit_assignment = ifcfile.by_type("IfcUnitAssignment")[0]
            unit_assignment.Units = ([length_unit, area_unit, volume_unit])
            
 
        # IFC hierarchy creation
        site_placement = create_ifclocalplacement(ifcfile)
        site = ifcfile.createIfcSite(create_guid(), owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)

        building_placement = create_ifclocalplacement(ifcfile, relative_to=site_placement)
        building = ifcfile.createIfcBuilding(create_guid(), owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)

        #storey_placement = create_ifclocalplacement(ifcfile, relative_to=building_placement)
        
        #elevation = feature.getAttribute('LevelElevationInfo.Level 1')
              
        #building_storey = ifcfile.createIfcBuildingStorey(create_guid(), owner_history, 'Storey', None, None, storey_placement, None, None, "ELEMENT", elevation)

        #container_storey = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])
        container_site = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
        container_project = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Project Container", None, project, [site])

       

        # Write the contents of the file to disk
        ifcfile.write(filename)

        self.pyoutput(feature)

    def close(self):

        pass

    def process_group(self):

        pass
