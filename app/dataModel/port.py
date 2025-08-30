from typing import List,Set,Dict,Tuple
from OCC.Core.TopAbs import (TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX,
                             TopAbs_SHELL, TopAbs_SOLID)
class Port():
    classTitle="Ports"
    
    titlePrefix="Port"
    nodeName="Ports"
    objIndex=256+1
    currentIndex:int=1
    def __init__(self) -> None:
        self.name:str=""
        self.title:str=""
        self.index:int=None
        self.modelName:str=None

        self.startX:float=None
        self.startY:float=None
        self.startZ:float=None
        self.endX:float=None
        self.endY:float=None
        self.endZ:float=None
        self.edgePoint:Tuple[Tuple[float,float,float],Tuple[float,float,float]]=None
        self.edgeId:int=-1
        self.vIndexList:list[tuple[int,int]]=None #顶点1编号
        
        pass