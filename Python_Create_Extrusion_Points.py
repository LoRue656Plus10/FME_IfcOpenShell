import fme
import fmeobjects
from fmeobjects import FMEPoint


class FeatureProcessor(object):


    def __init__(self):
        

        pass

    def input(self, feature):
        
        
        
        x0 = feature.getAttribute('_indices{0}.x')
        y0 = feature.getAttribute('_indices{0}.y')
        z0 = feature.getAttribute('_indices{0}.z')
  
        x1 = feature.getAttribute('_indices{1}.x')
        y1 = feature.getAttribute('_indices{1}.y')
        z1 = feature.getAttribute('_indices{1}.z')
        
        x2 = feature.getAttribute('_indices{2}.x')
        y2 = feature.getAttribute('_indices{2}.y')
        z2 = feature.getAttribute('_indices{2}.z')
   
        x3 = feature.getAttribute('_indices{3}.x')
        y3 = feature.getAttribute('_indices{3}.y')
        z3 = feature.getAttribute('_indices{3}.z')
 
        x4 = feature.getAttribute('_indices{4}.x')
        y4 = feature.getAttribute('_indices{4}.y')
        z4 = feature.getAttribute('_indices{4}.z')
                
        point0 = [x0,y0,z0]
        point1 = [x1,y1,z1]
        point2 = [x2,y2,z2]
        point3 = [x3,y3,z3]
        point4 = [x4,y4,z4]
  
        point0
        point1
        point2
        point3
        point4

        feature.setAttribute('p0', list(point0))
        feature.setAttribute('p1', list(point1))
        feature.setAttribute('p2', list(point2))
        feature.setAttribute('p3', list(point3))
        feature.setAttribute('p4', list(point4))
     
        self.pyoutput(feature)
      
    def close(self):

        pass

    def process_group(self):

        pass
