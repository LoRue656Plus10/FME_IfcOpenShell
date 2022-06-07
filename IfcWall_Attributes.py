import fme
import fmeobjects
from fmeobjects import FMELogFile
import ifcopenshell
import sys


class FeatureProcessor(object):


    def input(self, feature):
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")
        ifc_class = schema.declaration_by_name(feature.getAttribute('Classification')) 
        classAtts = ifc_class.all_attributes()
        classAttsLength = ifc_class.attribute_count()
        enumIndex = ifc_class.attribute_index("PredefinedType")
        predefined_type = ifc_class.attribute_by_index(enumIndex)
        enum = predefined_type.type_of_attribute()
        enumName = predefined_type.type_of_attribute().declared_type().name()
        
        #enumList = enum.get(enumName)

        

        
        newAtts = []
        for att in classAtts:
            attName = att.name()
            newAtts.append(attName)
            newAtts
        
        feature.setAttribute("EnumList", str(enum))
        feature.setAttribute("PredefinedType", str(enumName))
        feature.setAttribute("ClassAttributes", str(classAtts))
        
        feature.setAttribute("EntityAttribute", newAtts)
        feature.setAttribute("AttNumber", classAttsLength)
        feature.setAttribute("IfcSchema", "IFC4")

        self.pyoutput(feature)

    def close(self):

        pass

    def process_group(self):
        pass
