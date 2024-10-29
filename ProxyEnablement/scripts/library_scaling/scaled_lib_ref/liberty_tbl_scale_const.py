from liberty.parser import parse_liberty
import numpy as np
import bisect
import sys


def GetScaleLine(lx, ux, x):
  if x <= ux:
    return float(sys.argv[1])
  else:
    return float(sys.argv[1])

def GetUpdatedTables( tbl, maxCap ):
  transArr1 = tbl.get_array('index_1')[0]
  transArr2 = tbl.get_array('index_2')[0]
  valueArr = tbl.get_array('values')

  closeIdx = bisect.bisect_left(transArr2, maxCap)

  newArr = np.copy(valueArr)

  for tranIdx1 in range( len(transArr1) ):
    for tranIdx2 in range( len(transArr2) ):
      scaleDownFact = GetScaleLine( transArr2[0], maxCap, transArr2[tranIdx2] )  
      # Negative delay should have opposite effects
      value = valueArr[tranIdx1][tranIdx2]
      if value < 0:
        scaleDownFact *= -1.0

      newArr[tranIdx1][tranIdx2] = value * (1.0 + scaleDownFact)

  tbl['values'].clear()
  tbl.attributes.pop(2)
  tbl.set_array('values', newArr) 

### Configuration ###
liberty_file = sys.argv[2]

library = parse_liberty(open(liberty_file).read())

cells = library.get_groups('cell')
for cell in cells:
  for pin in cell.get_groups('pin'):
    pinTimings = pin.get_groups('timing')

    for timing in pinTimings:
      riseTbls = timing.get_groups('rise_constraint')
      fallTbls = timing.get_groups('fall_constraint')
      
      if len(riseTbls) == 0 or len(fallTbls) == 0:
          continue

      for riseTbl in riseTbls:
        if 'index_2' not in riseTbl: 
          continue
        GetUpdatedTables( riseTbl, pin['capacitance'] )
      for fallTbl in fallTbls:
        if 'index_2' not in riseTbl: 
          continue
        GetUpdatedTables( fallTbl, pin['capacitance'] )

print( str( library ) )

