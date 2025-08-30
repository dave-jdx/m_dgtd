from typing import List,Set,Dict,Tuple
from ngsolve import Mesh
from app.api import api_mesh
import os
import pickle
class t():
    t1:str="12"
    t2:Tuple[int,float]=(1,0.2)
    t3:List[int]=[1,2,3]
    meshObj:Mesh=None
    fileName:str=None

def save(tObj:t):
    f=open("test.pyx","wb")
    pickle.dump(tObj,f)
    f.close()
    pass
def load():
    f = open('test.pyx', 'rb')
    data:t = pickle.load(f)
    print(data.t1,data.t2,data.t3)
    f.close()
    pass
print(os.getcwd())
code,message,data=api_mesh.mesh_generate("temp/array.stp")
t.fileName=data[0]
t.meshObj=data[1]
tObj=t()
# tObj.fileName=data[0]
# tObj.meshObj=data[1]
save(tObj)
load()
