import fme
import fmeobjects
from fmeobjects import FMEGeometry
from fmeobjects import FMEBox
from fmeobjects import FMEFeature, FMEPoint, FMEGeometryTools

class FeatureProcessor(object):


    #def __init__(self):
        #pass

    def input(self, feature):

        #Box_Traits = FMEBox.
        
        #feature = FMEFeature()
        height = feature.getGeometry().getLocalHeight()

        
        
        feature.setAttribute("Glass_Height",height)

        self.pyoutput(feature)
        
 
        
        
        

    def close(self):

        pass

    def process_group(self):

        pass

