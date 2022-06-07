import fme
import fmeobjects
from fmeobjects import FMELogFile
import ifcopenshell
import ifcopenshell.util.pset
from ifcopenshell import util


class FeatureProcessor(object):


    def input(self, feature):
        ifc = ifcopenshell.open(r'C:\Users\LorenERouth\Documents\CADtoBIM\IFC\Pset_IFC4_ADD2.ifc')
        
        #simple_prop_template = ifc.by_type("IfcSimplePropertyTemplate")
        
        #prop_template_list = []
        #for n in simple_prop_template:
            #prop_name = n[2]
            #prop_template_list.append(prop_name)
            #prop_template_list
        
        #feature.setAttribute("PropertyTemplatenames", str(simple_prop_template))
        
        
        

         
        pset_qto = util.pset.PsetQto("IFC4")
        all_properties = pset_qto.get_applicable_names("IfcWall")        
        pset_wallcommon = pset_qto.get_by_name("Pset_WallCommon")
        simple_props = pset_wallcommon[6]

        
        prop_template_names = []
        for n in simple_props:
            prop_name = n[2]
            prop_template_names.append(prop_name)
            prop_template_names
        
        feature.setAttribute("AllProperties", all_properties)
        feature.setAttribute("PropertySetName", "Pset_WallCommon")
        feature.setAttribute("IfcSimplePropertyTemplateList", str(prop_template_names))
        feature.setAttribute("IfcSimpleProperties", str(simple_props))
        #feature.setAttribute("AttNumber", classAttsLength)   6
        feature.setAttribute("IfcSchema", "IFC4")

        self.pyoutput(feature)

    def close(self):

        pass

    def process_group(self):
        pass
