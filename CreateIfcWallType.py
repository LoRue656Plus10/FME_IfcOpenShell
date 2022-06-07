import fme
import fmeobjects
import uuid
import tempfile
import ifcopenshell
import ifcopenshell.util
import ifcopenshell.guid


class FeatureProcessor(object):

    def input(self, feature):

        create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)
        

        filename = feature.getAttribute('path_rootname')+"_FME.ifc"
        

        # Open ifc file
        ifcfile = ifcopenshell.open(filename)
   
        # Obtain references to instances defined in ifc file
        owner_history = ifcfile.by_type("IfcOwnerHistory")[0]     
        
  
        
        #pset_analytical_properties
        list_pset_analytical = [
        (ifcfile.createIfcPropertySingleValue("Absorptance", "Absorptance", ifcfile.create_entity("IfcReal", 0.7), None)),
        (ifcfile.createIfcPropertySingleValue("Roughness", "Roughness",  ifcfile.create_entity("IfcInteger", 3), None))
        ]
        
        pset_analytical_props = ifcfile.createIfcPropertySet(ifcopenshell.guid.new(), owner_history, 'Analytical Properties', None, list_pset_analytical)
        
        #pset_Construction
        list_pset_const = [
        ifcfile.createIfcPropertySingleValue("Function", "Function", ifcfile.create_entity("IfcIdentifier", 'Exterior'), None), 
        ifcfile.createIfcPropertySingleValue("Width", "Width", ifcfile.create_entity("IfcLengthMeasure", feature.getAttribute('LayerThickness')), None), 
        ifcfile.createIfcPropertySingleValue("Wrapping at Ends", "Wrapping at Ends", ifcfile.create_entity("IfcIdentifier", "None"), None),
        ifcfile.createIfcPropertySingleValue('Wrapping at Inserts', 'Wrapping at Inserts', ifcfile.create_entity("IfcIdentifier", 'Do not wrap'), None)
        ]
        
        pset_construction = ifcfile.createIfcPropertySet(ifcopenshell.guid.new(), owner_history, "Construction", None, list_pset_const)

        
        # pset_graphics
        list_csfc = [
        ifcfile.createIfcPropertySingleValue('Coarse Scale Fill Color', 'Coarse Scale Fill Color', ifcfile.create_entity("IfcInteger", 0),None)
        ]
        
        pset_graphics = ifcfile.createIfcPropertySet(ifcopenshell.guid.new(), owner_history, 'Graphics', None, list_csfc)

        
        # pset_assembly code
        list_assembly_code = [
        ifcfile.createIfcPropertySingleValue('Assembly Code', 'Assembly Code', ifcfile.create_entity("IfcText", feature.getAttribute('IdentityData.AssemblyCode')), None),
        ifcfile.createIfcPropertySingleValue('Assembly Description', 'Assembly Description', ifcfile.create_entity("IfcText", feature.getAttribute('IdentityData.AssemblyDescription')), None),
        ifcfile.createIfcPropertySingleValue('Type Name', 'Type Name', ifcfile.create_entity("IfcText", feature.getAttribute('FamilyType')), None)
        ]

        pset_identity_data = ifcfile.createIfcPropertySet(ifcopenshell.guid.new(), owner_history, 'Identity Data', None, list_assembly_code)
        
  
        # pset_Other
        list_pset_Other = [
        ifcfile.createIfcPropertySingleValue('Category', 'Category', ifcfile.create_entity("IfcLabel", feature.getAttribute('Category')), None),
        ifcfile.createIfcPropertySingleValue('Family Name', 'Family Name', ifcfile.create_entity("IfcText", feature.getAttribute('Family')), None)
        ]
        
        pset_other = ifcfile.createIfcPropertySet(ifcopenshell.guid.new(), owner_history, "Other", None, list_pset_Other)
        
        
        # pset_element_shading
        list_pset_elem_shading = [
        ifcfile.createIfcPropertySingleValue('Roughness', 'Roughness', ifcfile.create_entity("IfcPositiveLengthMeasure", 36.0), None)
        ]
        
        pset_element_shading = ifcfile.createIfcPropertySet(ifcopenshell.guid.new(), owner_history, 'Pset_ElementShading', None, list_pset_elem_shading)


        # aggregate all psets
        psets = [pset_analytical_props, pset_construction, pset_graphics, pset_identity_data, pset_other, pset_element_shading]
        
        
        # Create IfcWall types
        wall_type = ifcfile.createIfcWalltype(ifcopenshell.guid.new(), owner_history, feature.getAttribute('FamilyType'), None, None, psets, None, None, None, "STANDARD")



        # Write the contents of the file to disk
        ifcfile.write(filename)

        self.pyoutput(feature)



    def close(self):

        pass

    def process_group(self):

        pass
