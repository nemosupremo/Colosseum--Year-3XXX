def areaTri(p1,p2,p3):
   x0,y0 = p1[0], p1[1]
   x1,y1 = p2[0], p2[1]
   x2,y2 = p3[0], p3[1]
   return (.5)*(x1*y2 - y1*x2 -x0*y2 + y0*x2 + x0*y1 - y0*x1)

def pointInside(point, poly):
     ini = 0;
     for i in range(len(poly)):
          p1 = poly[i]
          p2 = poly[0] if i == len(poly)-1 else poly[i+1]
          p3 = point
          dt = areaTri(p1,p2,p3)
          if abs(dt) == 0: return False
          negpos = dt / abs(dt)
          if ini == 0:
               ini = negpos
          else:
               if negpos != ini: return False
     return True
