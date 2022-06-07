#PythonCaller__PropertySets

import fme
import fmeobjects
from fmeobjects import FMELogFile
import ifcopenshell
import ifcopenshell.util.pset
from ifcopenshell import util



class FeatureProcessor(object):


    def input(self, feature):
        
        
        pset_qto = util.pset.PsetQto("IFC4")
        
        pset_list = pset_qto.get_applicable_names("IfcWall")
        
        pset_template_gen = pset_qto.get_applicable("IfcWall")
        
        pset_info_list = []
        
        for pset in pset_template_gen:
            pset_info = pset.get_info()
            pset_info_list.append(pset_info)
            pset_info_list
            
            psetinfo1 = pset_info_list[0]        

        
        pset_wall_common = pset_qto.get_by_name("Pset_WallCommon").get_info()
        
        
        feature.setAttribute("Pset_Names", str(pset_list))
        feature.setAttribute("Pset_Info", str(pset_info_list))
        feature.setAttribute("Pset_Info", str(pset_wall_common))
        feature.setAttribute("IfcSchema", "IFC4")

        self.pyoutput(feature)

    def close(self):
        pass

    def process_group(self):
        pass
