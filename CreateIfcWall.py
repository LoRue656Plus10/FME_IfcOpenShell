import fme
import fmeobjects
import uuid
import ifcopenshell
import ifcopenshell.util
from ifcopenshell.util.selector import Selector
import sys
import lark


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

        # Obtain references to instances defined in template
        ifcfile = ifcopenshell.open(filename)
        level = feature.getAttribute('BuildingLevel')
        selector = Selector()
        storey_level = selector.parse(ifcfile, '.IfcBuildingStorey[Name *= "Level 1"]')[0]
        storey_placement = storey_level.ObjectPlacement
        context = ifcfile.by_type("IfcGeometricRepresentationContext")[0]
        owner_history = ifcfile.by_type("IfcOwnerHistory")[0]


        # Wall creation: Define the wall shape as a polyline axis and an extruded area solid
        
        wall_placement = create_ifclocalplacement(ifcfile, relative_to=storey_placement)
        polyline = create_ifcpolyline(ifcfile, [(feature.getAttribute('axis_indices{0}.x'),feature.getAttribute('axis_indices{0}.y'),feature.getAttribute('axis_indices{0}.z')), (feature.getAttribute('axis_indices{1}.x'), feature.getAttribute('axis_indices{1}.y'), feature.getAttribute('axis_indices{1}.z'))])
        axis_representation = ifcfile.createIfcShapeRepresentation(context, "Axis", "Curve2D", [polyline])

        extrusion_placement = create_ifcaxis2placement(ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
        point_list_extrusion_area = [feature.getAttribute('p0'), feature.getAttribute('p1'), feature.getAttribute('p2'), feature.getAttribute('p3'), feature.getAttribute('p4')]
        
        solid = create_ifcextrudedareasolid(ifcfile, point_list_extrusion_area, extrusion_placement, (0.0, 0.0, 1.0), feature.getAttribute('Constraints.UnconnectedHeight'))
        body_representation = ifcfile.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])

        product_shape = ifcfile.createIfcProductDefinitionShape(None, None, [axis_representation, body_representation])

        wall = ifcfile.createIfcWall(create_guid(), owner_history, feature.getAttribute('FamilyType'), feature.getAttribute('Family'), None, wall_placement, product_shape, None)

        # Define and associate the wall material
        material = ifcfile.createIfcMaterial("Default Wall")
        material_layer = ifcfile.createIfcMaterialLayer(material, feature.getAttribute('LayerThickness'), None)
        material_layer_set = ifcfile.createIfcMaterialLayerSet([material_layer], None)
        material_layer_set_usage = ifcfile.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "NEGATIVE", (feature.getAttribute('LayerThickness')*0.5))
        ifcfile.createIfcRelAssociatesMaterial(create_guid(), owner_history, RelatedObjects=[wall], RelatingMaterial=material_layer_set_usage)

        # Create and assign property sets
        # Pset_WallCommon
        wallcommon_values = [
        ifcfile.createIfcPropertySingleValue("Reference", "Reference", ifcfile.create_entity("IfcText", feature.getAttribute('FamilyType')), None),
        ifcfile.createIfcPropertySingleValue("IsExternal", "IsExternal", ifcfile.create_entity("IfcBoolean", feature.getAttribute('InExteriorShell')), None),
        ifcfile.createIfcPropertySingleValue("ThermalTransmittance", "ThermalTransmittance", ifcfile.create_entity("IfcReal", 2.569), None),
        ifcfile.createIfcPropertySingleValue("IntValue", "IntValue", ifcfile.create_entity("IfcInteger", 2), None)
        ]
        pset_wallcommon = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Pset_WallCommon", None, wallcommon_values)
        
        # pset Constraints
        constraint_values = [
        ifcfile.createIfcPropertySingleValue("Base Constraint", "Base Constraint", ifcfile.create_entity("IfcText", f"Level {feature.getAttribute('BuildingLevel')}"), None), 
        ifcfile.createIfcPropertySingleValue("Base Extension Distance", "Base Extension Distance", ifcfile.create_entity("IfcLengthMeasure", feature.getAttribute('Constraints.BaseExtensionDistance')), None), 
        ifcfile.createIfcPropertySingleValue("Base is Attached", "Base is Attached", ifcfile.create_entity("IfcBoolean", False), None),
        ifcfile.createIfcPropertySingleValue("Base Offset", "Base Offset", ifcfile.create_entity("IfcLengthMeasure", feature.getAttribute('Constraints.BaseOffset')), None),
        ifcfile.createIfcPropertySingleValue("Cross-Section", "Cross-Section", ifcfile.create_entity("IfcIdentifier", "Vertical"), None),
        ifcfile.createIfcPropertySingleValue("Location Line", "Location Line", ifcfile.create_entity("IfcIdentifier", "Wall Centerline"), None),
        ifcfile.createIfcPropertySingleValue("Related to Mass", "Related to Mass", ifcfile.create_entity("IfcBoolean", False), None),
        ifcfile.createIfcPropertySingleValue("Room Bounding", "Room Bounding", ifcfile.create_entity("IfcBoolean", True), None),
        ifcfile.createIfcPropertySingleValue("Top Extension Distance", "Top Extension Distance", ifcfile.create_entity("IfcLengthMeasure", feature.getAttribute('Constraints.TopExtensionDistance')),None),
        ifcfile.createIfcPropertySingleValue("Top is Attached", "Top is Attached", ifcfile.create_entity("IfcBoolean", False), None),
        ifcfile.createIfcPropertySingleValue("Top Offset", "Top Offset", ifcfile.create_entity("IfcLengthMeasure", feature.getAttribute('Constraints.TopOffset')), None), 
        ifcfile.createIfcPropertySingleValue("Unconnected Height", "Unconnected Height", ifcfile.create_entity("IfcLengthMeasure", feature.getAttribute('Constraints.UnconnectedHeight')), None)
        ]
        
        pset_constraints = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Constraints", None, constraint_values)
        
        #pset Other
        other_values = [
		ifcfile.createIfcPropertySingleValue("Category", "Category", ifcfile.create_entity("IfcLabel", feature.getAttribute('Category')), None),
        ifcfile.createIfcPropertySingleValue("Family", "Family", ifcfile.create_entity("IfcLabel", feature.getAttribute('Family')), None),
        ifcfile.createIfcPropertySingleValue("Family and Type", "Family and Type", ifcfile.create_entity("IfcLabel", feature.getAttribute('FamilyAndType')), None),
        ifcfile.createIfcPropertySingleValue("Type", "Type", ifcfile.create_entity("IfcLabel", feature.getAttribute('FamilyAndType')), None),
        ifcfile.createIfcPropertySingleValue("Type Id", "Type Id", ifcfile.create_entity("IfcLabel", feature.getAttribute('FamilyAndType')), None)
        ]
		
        pset_other = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Other", None, other_values)
 
        # Pset Construction
        const_values = [
        ifcfile.createIfcPropertySingleValue("Function", "Function", ifcfile.create_entity("IfcIdentifier", feature.getAttribute('Function')), None), 
        ifcfile.createIfcPropertySingleValue("Width", "Width", ifcfile.create_entity("IfcLengthMeasure", feature.getAttribute('LayerThickness')), None), 
        ifcfile.createIfcPropertySingleValue("Wrapping at Ends", "Wrapping at Ends", ifcfile.create_entity("IfcIdentifier", "None"), None),
        ifcfile.createIfcPropertySingleValue("Wrapping at Inserts", "Wrapping at Inserts", ifcfile.create_entity("IfcIdentifier", "Do not wrap"), None)
        ]
        
        pset_construction = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Construction", None, const_values)
        
        # pset Identity Data
        identity_data_values = [
        ifcfile.createIfcPropertySingleValue("Assembly Code", "Assembly Code", ifcfile.create_entity("IfcText", feature.getAttribute('IdentityData.AssemblyCode')), None), 
        ifcfile.createIfcPropertySingleValue("Assembly Description", "Assembly Description", ifcfile.create_entity("IfcText", feature.getAttribute('IdentityData.AssemblyDescription')), None), 
        ifcfile.createIfcPropertySingleValue("Type Name", "Type Name", ifcfile.create_entity("IfcText", feature.getAttribute('FamilyType')), None)
        ]
        
        pset_identity_data = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Identity Data", None, identity_data_values)

        # pset quantity take off
        QTO_values = ifcfile.createIfcPropertySingleValue("Reference", "Reference", ifcfile.create_entity("IfcIdentifier",feature.getAttribute('FamilyType')), None)
        pset_QTO = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Pset_QuantityTakeOff", None, [QTO_values])

        
        #related_objects = [pset_wallcommon, pset_constraints, pset_other, pset_construction, pset_identity_data, pset_QTO]
        ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [wall], pset_wallcommon)
        ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [wall], pset_constraints)
        ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [wall], pset_other)
        ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [wall], pset_construction)
        ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [wall], pset_identity_data)
        ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [wall], pset_QTO)
        
        #ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [wall], pset_wallcommon)

        # Add quantity information
        quantity_values = [
            ifcfile.createIfcQuantityLength("Length", "Length of the wall", None, feature.getAttribute('_length')),
            ifcfile.createIfcQuantityArea("Area", "Area of the front face", None, feature.getAttribute('_area')),
            ifcfile.createIfcQuantityVolume("Volume", "Volume of the wall", None, feature.getAttribute('_volume'))
        ]
        element_quantity = ifcfile.createIfcElementQuantity(create_guid(), owner_history, "BaseQuantities", None, None, quantity_values)
        ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [wall], element_quantity)
               
           

        ifcfile.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, None, None, [wall], storey_level)

        wall_guid = wall.GlobalId
        
        feature.setAttribute('wall_guid', wall_guid)


        # Write the contents of the file to disk
        ifcfile.write(filename)
        
        
        

        self.pyoutput(feature)

    def close(self):

        pass

    def process_group(self):

        pass
