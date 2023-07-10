from aistudio.abstraction.base_types import *
import os
from aistudio.exception.exception_utils import jsonize,Reporter


def get_paint_area(height, sidelengths:tuplargs,exclusiondimensions:dictargs,roomname = None,fullroompathnamewithextension = None):
    """_summary_ calculates the area required to be painted

    area = h/10000 { ∑ wi  - ∑ Ej0 * Ej1}  

    Args:
        height (_type_): in cm height of the room
        sidelengths : in cm length of the sides, must be at least 3
        exlusiondimensions: key:any, value : tuple(x,y)
    """
    area = 0
    factor  = height/10000
    sidelens = 0
    excludearea = 0
    
    for sl in sidelengths:
        sidelens += sl 
    
    for x,y in exclusiondimensions.kwargs.items():
        for i in range(int((len(y) / 2))):
            excludearea += (y[0] * y[1])/10000
    
    total = factor * sidelens
    area = total-excludearea

    if fullroompathnamewithextension:
        path = os.path.join(fullroompathnamewithextension,roomname,f'{roomname}.json')
        rep = Reporter(room = roomname,requiredarea = area, totalarea = total, exlucsionitems = exclusiondimensions.kwargs, excludedarea = excludearea)

        jsonize(rep,fullsavename=path)

    return area
