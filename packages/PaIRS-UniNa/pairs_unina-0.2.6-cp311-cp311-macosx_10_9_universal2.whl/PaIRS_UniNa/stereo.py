''' helper class for Stereo'''
# pylint: disable=pointless-string-statement, too-many-instance-attributes, no-name-in-module, multiple-imports
# pylint: disable= import-error 
# pylint: disable=multiple-statements


import sys #, traceback
from typing import Tuple#,Callable
from enum import Enum
from time import sleep 
#import faulthandler # per capire da dove vengono gli errori c
import platform

from PIL import Image
import numpy as np

from .tAVarie import pri, PrintTA ,PrintTAPriority
from .readcfg import readNumCfg, readCfgTag,readNumVecCfg

if __package__ or "." in __name__:
  import PaIRS_UniNa.PaIRS_PIV as PaIRS_lib
  from PaIRS_UniNa.PaIRS_PIV import Punto
  
else:
  if platform.system() == "Darwin":
    sys.path.append('../lib/mac')
    #sys.path.append('../lib')
  else:
    #sys.path.append('PaIRS_PIV')
    sys.path.append('../lib')
    sys.path.append('TpivPython/lib')
  import PaIRS_PIV as PaIRS_lib # type: ignore
  from PaIRS_PIV import Punto # type: ignore
  

# to be deleted
#import debugpy #nel caso mettere nel thread debugpy.debug_this_thread()
#from PaIRS_pypacks import Flag_DEBUG_PARPOOL
Flag_DEBUG_PARPOOL=1 # pylint: disable=invalid-name
if Flag_DEBUG_PARPOOL: import debugpy #nel casso mettere nel thread debugpy.debug_this_thread()

FlagReadCfg=True
PrintTA.flagPriority=PrintTAPriority.veryLow 
# errror codes 
TYPE_ERR_REPEAT=-101 # pylint: disable=invalid-name
TYPE_ERR_STOP=0 # pylint: disable=invalid-name

#for multithreading and other stuff 
SleepTime_Workers=0.1 # pylint: disable=invalid-name

class StereoTasks(Enum):
  ''' when <=0 no button is created'''
  #stop should be zero so that is is possible to check immediately is no task are running
  stop = 0            # pylint: disable=invalid-name
  findAllPlanes= 1    # pylint: disable=invalid-name
  '''****
  findCurrentPlane= 2 # pylint: disable=invalid-name
  calibrate=3         # pylint: disable=invalid-name
  savePoints=4         # pylint: disable=invalid-name
  findPlanesFromOrigin=-1         # pylint: disable=invalid-name
  ***'''
stereoTasksText=[
  # the index is relative to the value of CalibTask
   'Stop',           
   'Find all' ,  
   '''***
   'Find curr.',
   'Calibrate' ,   
   'Save coord.' ,   
   '...'
   ***''' 

]
''' when not calibrated all the voices are disabled'''
class StereoFunctions(Enum):
  ''' when <=0 only the context menu is added but the button isn't created (negative voices are not disabled)'''
  #***removeMaxErrPoint= 1    # pylint: disable=invalid-name
  #***findMaxErrPoint=2    # pylint: disable=invalid-name
  #***RemovePoint=-3    # pylint: disable=invalid-name
  #findMaxErrPoint1=[3, 4]    # pylint: disable=invalid-name
  
stereoFunctionsText=[
  # hte index is relative to the value of CalibTask
   'Stop',           #not used but needed
   #***'Delete max.',           
   #***'Focus max.',           
   #***'Apply to all',
]

def loopFun(fun):
  ''' loop a function 
    if the fun raises exception:
      ValueError as err: if err.args[1]==TYPE_ERR_REPEAT'''
  def wrapper(*args,**kwargs):
    ''' wrapper'''
    while True:  
      try:
        res=fun(*args,**kwargs)
      except ValueError as err:
        if err.args[1]!=TYPE_ERR_REPEAT:
          raise err
        continue
      break
    return res
  return wrapper  

def printPIVLog(PD):
    stampa="It    IW      #IW        #Vect/#Tot      %       CC       CC(avg)   DC%\n"#  NR% Cap%\n"
    for j in range(len(PD.It)):
        riga="%3d %3dx%-3d %4dx%-4d %7d/%-7d %5.1f  %8.7f  %8.7f  %4.1f\n" %\
            (PD.It[j], PD.WCella[j], PD.HCella[j], PD.W[j], PD.H[j], PD.NVect[j],\
            PD.W[j]*PD.H[j], 100.0*PD.NVect[j]/(PD.W[j]*PD.H[j]), PD.Fc[j],\
                PD.FcMedia[j], 100.0*PD.ContErorreDc[j]/(PD.W[j]*PD.H[j]))#,\
                    #100.0*PIV.PD.ContRemNoise[j]/(PIV.Inp.ImgW*PIV.Inp.ImgH),\
                    #100.0*PIV.PD.ContCap[j]/(PIV.Inp.ImgW*PIV.Inp.ImgH))
        stampa=stampa+riga
    return stampa

class Stereo(PaIRS_lib.PyFunOutCalib):
  def __init__(self):
    #super().__init__(mainFun=self.findAllPlanes)
    PaIRS_lib.PyFunOutCalib.__init__(self)
    # self.funCalib =PaIRS_lib.getPyFunCalib(self) 
    # self.pointDesc=['origin ', 'right (along x)','upper (along y)']
    # self.inputPoints=[Punto(0,0)]*3  #input points when looking for origin
    # self.foundPoints=[Punto(0,0)]*3  #found point near the input points when looking for origin
    # self.flagFoundPoints=[False]*3  #flag to be sure that point have been found
    #self.cal=PaIRS_lib.Cal()
    
    
    #self.disp=PaIRS_lib.StereoDisp()
    self.stereo=PaIRS_lib.Stereo()
    
    
    self.imgs =[]                     # Images imgs[i][c][0/1]  i img number c cam last first or second image
    # self.ccMask =[]                   # correlation mask 
    # self.flagRicerca=0  # 0 stand by 1-3 searching first, second or third point 4 the three point have been found

  


    
    # self.tipoCal=0                # Calibration type see calibra.h
    # comunication with the view
    self.signals:SignalsStereoWorker=None
    self.ans=0                    # Answer from view
    self.pu=Punto(0,0)            # Point From view
    self.flagAnsReady=False       #True  if answer is ready to be read
    self.flagPointReady=False     #True  if point  is ready to be read
    self.flagExitFromView=False   #True  if exit from View signal
    self.flagFindAllPlanes=False  #True  if point  searching all the planes
    self.rectZonaCom:Tuple=None
    #self.cal.flagCalibrated=False      # True if the calibration has ended successfully
    # various
    self.cfgName=''               # Name of the cfg file comprehensive of path but without extension
    self.cfgNameStereo=''               # Name of the cfg file comprehensive of path but without extension
    pri.Time.cyan(0,'Init Stereo')
    self.nImgs=0
    self.img=0  # Img in use 
    self.nCams=2                  # number of cameras
    self.cam=0                  # camera in use
    
    self.cams=[]                  # list of the camera identifiers
    self.pair=0                 # 0 img a 1 img b
    # flags
    # self.flagShowMask=True       # True to plot the mask #todo maybe in a different window
    #self.flagPlotMask=False
    #self.strOut=''
  
    self.LLim=1
    self.LMax=1
    self.LMin=0



  
  def waitAnsFromView(self)-> int:
    ''' used to wait an answer from the view return an int  '''
    while not self.flagAnsReady:
      sleep(SleepTime_Workers) 
    self.flagAnsReady=False

    return self.ans

  def checkExitFromView(self):
    ''' control if an exit signal has been emitted by the view and in case raises an error signal'''
    if self.flagExitFromView:
      self.flagExitFromView=False
      self.signals.textFromStereo.emit( 'stopped by user')
      raise ValueError('Exit from view ',TYPE_ERR_STOP) 
      
  def waitPointFromView(self)-> int:
    ''' used to wait a point from the view return an int  '''
    while not self.flagPointReady and not self.flagExitFromView:
      sleep(SleepTime_Workers) 
    self.flagPointReady=False
    self.checkExitFromView()
    return self.pu

  
  
  def askToRetry(self, funName:str):
    ''' used to avoid repeating code'''
    self.signals.textFromStereo.emit('Press Yes to continue No to repeat' )
    if not self.waitAnsFromView():
      raise ValueError(f'Repeat in {funName}',TYPE_ERR_REPEAT) 
  
  def exceptAskRetry(self, exc:Exception, question: str,funName:str):
    ''' used to avoid repeating code'''
    if len(exc.args) >1:# if not most probably from c Lib
      if exc.args[1]==TYPE_ERR_STOP:# just exit
        raise exc
    self.signals.textFromStereo.emit(question)
    if self.waitAnsFromView():
      raise ValueError(f'Repeat in {funName}',TYPE_ERR_REPEAT) from exc 
    raise ValueError(f'Search stopped in {funName}',TYPE_ERR_STOP) from exc
  
  @loopFun
  def findPoint(self)->Punto:  
    ''' look for a single point '''
    self.signals.flagGetPointFromStereo.emit(1) #enables the search for points in the view
    pu=self.waitPointFromView()
    self.signals.flagGetPointFromStereo.emit(0) #disables the search for points in the view
    sleep(0)
    try:
      pu=self.cal.findPoint(pu)
    except ValueError as exc:
      self.exceptAskRetry( exc, 'Point not found Yes to repeat No to stop','findPoint')
    #pri.Info.white(f'findPoint ({pu.x}, {pu.y})')
    self.signals.drawSingleCircleFromStereo.emit(pu,0,self.flagRicerca-1) # draws a circle on the detected points
    return pu
  def getZonaCom(self,c:int):
    return (min (self.disp.vect.Xinf[c],self.disp.vect.Xsup[c]),
                               min (self.disp.vect.Yinf[c],self.disp.vect.Ysup[c]),
                               max (self.disp.vect.Xinf[c],self.disp.vect.Xsup[c]),
                               max (self.disp.vect.Yinf[c],self.disp.vect.Ysup[c]))      
  def getZonaComStereo(self,c:int):
    return (min (self.stereo.vect.Xinf[c],self.stereo.vect.Xsup[c]),
                               min (self.stereo.vect.Yinf[c],self.stereo.vect.Ysup[c]),
                               max (self.stereo.vect.Xinf[c],self.stereo.vect.Xsup[c]),
                               max (self.stereo.vect.Yinf[c],self.stereo.vect.Ysup[c]))   
  def taskFindAllPlanes(self):  
    ''' finds all the planes '''

    pri.Callback.cyan('taskFindAllPlanes')

  def prettyPrintErrCalib(self)-> str:
    ''' generate a string with a "pretty" version of the calibration error '''
    data=self.cal.data
    strAppo=f'#Points = { data.Npti}\n'
    strAppo+=f'ErrRms={data.Errrms:.3f} ErrMax={data.ErrMax:.3f} \nImg ({data.XMax:.2f}, {data.YMax:.2f}) Space({data.xMax:.2f}, {data.yMax:.2f}, {data.zMax:.2f})'
    return strAppo
  
  def prettyPrintCalib(self)-> str:
    ''' generate a string with a "pretty" version of the calibration parameters '''
    data=self.cal.data
    cost=self.cal.vect.cost
    convGradi=180/np.pi
    tipoCal = (data.TipoCal >> CalFlags.SHIFT) &CalFlags.MASK
    flagPinHole =not (not( data.TipoCal & CalFlags.Flag_PIANI))  # pylint: disable=unneeded-not,superfluous-parens
    #F_Sa = not (not(data.TipoCal & CalFlags.Flag_LIN_VI))
    s=''
    if (data.FlagCal == 1 or data.FlagCal == 2 or data.FlagCal == 3):
      c = 0
      for i in range (4, data.NumCostCalib):
         s+=f'{cost[c][i]:+.4g}  '
    else:         # TSAI di qualche forma!!!!!!!!
      if (tipoCal> 0 or ( (data.FlagCal >= 10 and  data.FlagCal <= 43)and  flagPinHole)):#la seconda dovrebbe comprendere la prima 
        cPlanes=self.cal.vect.costPlanes
        s+='Planes ******************\r\n'
        for i in range ( data.Numpiani_PerCam):
          s+=f'Plane {i}: Ang(°)=[{cPlanes[i,0]:+.2f},{cPlanes[i,1]:+.2f},{cPlanes[i,2]:+.2f}] T=[{cPlanes[i,3]:+.2f},{cPlanes[i,4]:+.2f},{cPlanes[i,5]:+.2f}]\r\n'
      if data.FlagCal >= 30:#cal cilindrica
        c = 0
        s+='Cylinder ****************\r\n'
        s+=f'Distortion s1={cost[c][24]:.2e} s2={cost[c][25]:.2e}\r\n' 
        s+=f'T(Cyl)=[{cost[c][17]:+.2f},{cost[c][18]:+.2f}] Ang(°)=[{cost[c][19]:+.2f},{cost[c][20]:+.2f}]\r\n' 
        s+=f'r(Cyl) [{cost[c][21]:+.2f},{cost[c][21]+cost[c][23]:+.2f}] rho=%g  \r\n'
      s+='Cameras  ***************\r\n'
      for c in range(data.NCam):
        if cost[c][1] < 0:
          s+='\r\n \r\n *******  The coordinate system is not right-handed ******* \r\n \r\n'
        #Flag Rot Rot Rot Tx Ty Tz   f   u0  v0    b1    b2    k1    k2    p1    p2   sx   S   

        s+=f'** c={c} Ang(°)=[{cost[c][2] * convGradi:+.2f},{cost[c][3] * convGradi:+.2f},{cost[c][4] * convGradi:+.2f}] '
        s+=f'T=[{cost[c][5]:+.2f},{cost[c][6]:+.2f},{cost[c][7]:+.2f}] \r\n'
        s+=f'   f={cost[c][8]:+.2f} T(Img) [{cost[c][9]:+6.4g},{cost[c][10]:+6.4g}] b=[{ cost[c][11]:.2e},{ cost[c][12]:.2e}]  \r\n'
        s+=f'   k=[{cost[c][13]:.2e},{cost[c][14]:.2e}]  p=[{cost[c][15]:.2e},{cost[c][16]:.2e}]\r\n'
        if data.FlagCal >= 30:
          s+=f'   Pixel Ratio={cost[c][26]:+.4g} xdim pixel={cost[c][27]:+.4g}  \r\n'
        else:
          s+=f'   Pixel Ratio={cost[c][17]:+.4g} xdim pixel={cost[c][18]:+.4g}  \r\n'
    return s
  
  def waitForEver(self):
    ''' simply waits for ever'''
    self.signals.flagGetPointFromStereo.emit(1)
    #sleep(SleepTime_Workers) 
    self.taskFindAllPlanes()
    i=0
    while True:# and not self.isKilled:
      sleep(SleepTime_Workers*5) 
      i+=1
      #pri.Info.white(f'dummy called->{i}')    
  
  def setLMinMax(self,img=0,cam=0,pair=0):
    self.LLim,self.LMax,self.LMin=self.calcLMinMax(img=img,cam=cam,pair=pair)
    return
  # TODO GP forse è meglio fissare un LLim positivo ed uno negativo come:
  # perc= 0.2 ad esempio
  # LLMin=LMin-abs((LMax-LMin)*perc) 
  # LLMax=LMax+abs((LMax-LMin)*perc) 
  # questo potrebbe essere fatto direttamente in fase di plot
  # fra l'altro potremmo calcolare queste cose solo in fase di lettura (o calcolo nel caso della maschera) e non modificarle più
  def calcLMinMax(self,img=0,cam=0,pair=0):
    LLim=2**16-1
    if len(self.imgs):
        a=self.imgs[img][cam][pair]
        LLim=np.iinfo(a.dtype).max
        flagArray=True
    else:
        flagArray=False
    if flagArray:
      try:
        LMax=int(a.max())
      except:
        LMax=LLim
      try:
        LMin=int(a.min())
      except:
        LMin=-LLim
    else:
      LMax=LLim
      LMin=-LLim
    return LLim,LMax,LMin
        
  def readCalFile(self,buffer:str)->Tuple[int,int ,list[float]]:
    ''' reads the calibration constants from a file
      buffer is the name of the file
      if numCostCalib is different from none it is used regardless of the value in  the file
      In output returns flagCal,numCostCalib,cost 
    '''
    try:
      with open(buffer,'r') as f:
        tag=readCfgTag(f)
        
        if tag != "%SP00015":
          raise RuntimeError(f'Wrong tag in file: {buffer}') 
        ind=1
        ind,flagCal=readNumCfg(f,ind,int)
        ind,numCostCalib=readNumCfg(f,ind,int)
        
        cost=[0]*numCostCalib
        for i in range(numCostCalib):# dati->NumCostCalib; i++):
          ind,cost[i]=readNumCfg(f,ind,float)
      return flagCal,numCostCalib,cost
        #if "%SP00015"
        #for index, line in enumerate(f):              pri.Info.white("Line {}: {}".format(index, line.strip()))
    #except Exception as exc: 
    except IOError as exc: 
      raise RuntimeError(f'Error opening the calibration constants file: {buffer}') from exc
    except ValueError as exc: 
      raise RuntimeError(f'Error reading line:{ind+1} of file: {buffer}') from exc
    except IndexError as exc: 
      raise RuntimeError(f'Error reading array in line:{ind+1} of file: {buffer}') from exc  
  
  def readImgsStereo(self ):
    ''' reads the images'''
    formato=f'0{self.stereo.SPIVIn.Digit}d'
    spivIn=self.stereo.SPIVIn
    dP=self.stereo.dataProc
    ind=np.ix_(np.arange(spivIn.RigaPart,spivIn.RigaPart+dP.ImgH),np.arange(spivIn.ColPart,spivIn.ColPart+dP.ImgW))
    for p in range(spivIn.FirstImg, spivIn.LastImg+1):
      ic=[]
      for cam in range(self.nCams):
      #numero='' if self.cal.data.FlagCam else f'_cam{self.cams[cam]}'
        nomeImg=spivIn.InDir+spivIn.ImgRoot+f'{self.cams[cam]}_a{p:{formato}}'+spivIn.InExt
        da=np.array(Image.open(nomeImg),dtype=float)
        nomeImg=spivIn.InDir+spivIn.ImgRoot+f'{self.cams[cam]}_b{p:{formato}}'+spivIn.InExt
        db=np.array(Image.open(nomeImg),dtype=float)
        #pri.Info.white (f'{nomeImg}')
        #ic.append
        
        ic.append([np.ascontiguousarray(da[ind],dtype= np.uint16),np.ascontiguousarray(db[ind],dtype= np.uint16)])
      self.imgs.append(ic)
      #self.imgs.append(np.ascontiguousarray(da[spivIn.RigaPart:spivIn.RigaPart+dP.ImgH,spivIn.ColPart:spivIn.ColPart+dP.ImgW],dtype= np.uint16))

    self.setLMinMax()
    self.stereo.initAlloc(None)
    for i in range( spivIn.LastImg+1-spivIn.FirstImg):
        self.stereo.run(self.imgs[i])
        sOut=printPIVLog(self.stereo.PD0)
        sOut+=printPIVLog(self.stereo.PD1)
        print (sOut)
    

      
    #[Image2PIV_Float(I) for I in iProc]
    
    
    
  def readImgs(self ):
    ''' reads the images'''
    formato=f'0{self.disp.SPIVIn.Digit}d'
    spivIn=self.disp.SPIVIn
    dP=self.disp.dataProc
    ind=np.ix_(np.arange(spivIn.RigaPart,spivIn.RigaPart+dP.ImgH),np.arange(spivIn.ColPart,spivIn.ColPart+dP.ImgW))
    for p in range(spivIn.FirstImg, spivIn.LastImg+1):
      ic=[]
      for cam in range(self.nCams):
      #numero='' if self.cal.data.FlagCam else f'_cam{self.cams[cam]}'
        nomeImg=spivIn.InDir+spivIn.ImgRoot+f'{self.cams[cam]}_a{p:{formato}}'+spivIn.InExt
        da=np.array(Image.open(nomeImg),dtype=float)
        nomeImg=spivIn.InDir+spivIn.ImgRoot+f'{self.cams[cam]}_b{p:{formato}}'+spivIn.InExt
        db=np.array(Image.open(nomeImg),dtype=float)
        #pri.Info.white (f'{nomeImg}')
        #ic.append
        
        ic.append([np.ascontiguousarray(da[ind],dtype= np.uint16),np.ascontiguousarray(db[ind],dtype= np.uint16)])
      self.imgs.append(ic)
      #self.imgs.append(np.ascontiguousarray(da[spivIn.RigaPart:spivIn.RigaPart+dP.ImgH,spivIn.ColPart:spivIn.ColPart+dP.ImgW],dtype= np.uint16))

    self.setLMinMax()
    
    
    
    
    
    
    self.disp.initAllocDisp()
    dAC=self.disp.dispAvCo
    ve=self.disp.vect
    
    for it in range(5):
      self.disp.evaldXdY()  
      for i in range( spivIn.LastImg+1-spivIn.FirstImg):
        self.disp.deWarpAndCalcCC(self.imgs[i])
      self.disp.calcDisparity()
      print(f"Laser plane eq {ve.PianoLaser[0]:4g}, {ve.PianoLaser[1]:4g}, {ve.PianoLaser[2]:4g} Res error cal {dAC.dOrtMean:4g} Corr Width {dAC.DeltaZ:4g} (approx {dAC.DeltaZ * dP.RisxRadd / abs(dAC.ta0Mean - dAC.ta1Mean):4g}mm)")
      '''ve.PianoLaser[0]=0
      ve.PianoLaser[1]=0
      ve.PianoLaser[2]=0'''
      #sprintf(OutErr, "Laser plane eq %g %g %g Res error cal %g Corr Width %g (approx %gmm)", datiproc->PianoLaser[0], datiproc->PianoLaser[1], datiproc->PianoLaser[2], DiAvCo->dOrtMean, DiAvCo->DeltaZ, DiAvCo->DeltaZ * datiproc->RisxRadd / ABS(DiAvCo->ta0Mean - DiAvCo->ta1Mean));
    #self.cal.FlagPos=-5

    '''aaaa=np.array([[[1, 2, 3, 4],[11, 12, 13, 14],[21, 22, 23,24]]             ,[[10, 2, 3, 4],[1, 12, 13, 14],[1, 22, 23,24]]             ])
    aaaa=np.array([[[[1, 2, 3, 4],[11, 12, 13, 14],[21, 22, 23,24]]             ,[[10, 2, 3, 4],[1, 12, 13, 14],[1, 22, 23,24]]             ],[[[100, 2, 3, 4],[11, 12, 13, 14],[21, 22, 23,24]]             ,[[1000, 2, 3, 4],[1, 12, 13, 14],[1, 22, 23,24]]             ]])
    bb=np.ascontiguousarray(aaaa,dtype= np.uint16)
    self.cal.SetImg( [ bb])
    bb
    da[284,202]
    '''
    #self.cal.setImgs(self.imgs)
    #self.ccMask=self.cal.getMask()

  def readCfgStereo(self):
    #self.stereo.readAllCfgs(self.cfgNameStereo)
    self.initDataStereo()
    '''
    try:
      if FlagReadCfg:
        self.disp.readAllCfgs(self.cfgName)
      else:
        self.initData()
  
    except Exception as exc:
      #traceback.print_exc()
      #pri.Info.white(str(exc.__cause__).split('\n')[3])
      #pri.Info.white(str(exc.args[0]).split('\n')[3])
      raise exc
    '''
    self.nCams=2
    self.cams=[0, 1]
    self.nImgs=self.stereo.SPIVIn.LastImg+1-self.stereo.SPIVIn.FirstImg
    # the common zone can be changed by using the following variables 
    # self.disp.dataProc.xinfZC, self.disp.dataProc.xsupZC ,self.disp.dataProc.yinfZC, self.disp.dataProc.ysupZC
    #eg
    #self.disp.dataProc.xinfZC=-30
    try:
      self.stereo.evalCommonZone()
      
    except ValueError as exc:
      pri.Info.white(f"{exc=}, {type(exc)=}")
      #self.signals.textFromStereo.emit(f'{exc}') # todo come comunico con la view
    self.cam=0
    
    self.rectZonaCom=self.getZonaComStereo(self.cam)
    
  def readCfg(self):
    #self.stereo.readAllCfgs(self.cfgNameStereo)
    try:
      if FlagReadCfg:
        self.disp.readAllCfgs(self.cfgName)
      else:
        self.initData()
  
    except Exception as exc:
      #traceback.print_exc()
      #pri.Info.white(str(exc.__cause__).split('\n')[3])
      #pri.Info.white(str(exc.args[0]).split('\n')[3])
      raise exc
    
    self.nCams=2
    self.cams=[0, 1]
    self.nImgs=self.disp.SPIVIn.LastImg+1-self.disp.SPIVIn.FirstImg
    # the common zone can be changed by using the following variables 
    # self.disp.dataProc.xinfZC, self.disp.dataProc.xsupZC ,self.disp.dataProc.yinfZC, self.disp.dataProc.ysupZC
    #eg
    #self.disp.dataProc.xinfZC=-30
    try:
      #self.stereo.evalCommonZone()
      self.disp.evalCommonZone()
    except ValueError as exc:
      pri.Info.white(f"{exc=}, {type(exc)=}")
      #self.signals.textFromStereo.emit(f'{exc}') # todo come comunico con la view
    self.cam=0
    
    self.rectZonaCom=self.getZonaCom(self.cam)
    
    

  

    
  
    
  
  def initData(self):
    spiv=self.disp.SPIVIn
    dP=self.disp.dataProc
    dAC=self.disp.dispAvCo
    spiv.nomecal='cal'    # 		Root of calibration constants				
    spiv.percorsocal='../Cal/'     #Path of calibration constants
    spiv.ImgRoot='disp_cam'   #		Root input	Images
    spiv.InExt='.png'   #			Extension of the images
    spiv.InDir='../img/'     #Path of the images
    spiv.FirstImg=1 # # of first img to be processed
    spiv.LastImg=3   # # of first last to be processed
    spiv.Digit=3     # number  of figures i.e. zeros (MAX 10)		
    spiv.RigaPart=0 		# Starting row 
    spiv.ColPart=0			# Starting column
    dP.ImgH=1024 -spiv.RigaPart   # Ending row
    dP.ImgW=1280 -spiv.ColPart	  # Starting row
    spiv.Sfas=3    #	Sfasamento sub-immagini (righe a partire dall'origine):			0 per singola img: 1=a,b (finali); 2=_1,_2 (finali); 3=a,b (prima del numero sequenziale			
    spiv.FlagImgTau=1   #	Img da processare: 0-entrambe; 1-solo la prima; 2-solo la seconda;PARAMETRO IGNORATO SE SFAS=0					
    
    #Output
    spiv.OutRoot ='disp'      #	        Root of output Files
    spiv.OutDir ='../Cal/'      #                 Output path 
    # Process parameters **********************
    dP.FlagInt=57     #			Metodo di raddrizzamento: 0=veloce (simp.), 1=quad…….				
    dP.FlagZonaCom=0   # 			Flag per la zona comune: 0=coordinate nel piano oggetto; 1=coord. nel piano img
    spiv.Niter=-5   #		Numero di iterazioni
    if (spiv.Niter < 0) :
      spiv.WrtFlag = 1
      spiv.Niter = -spiv.Niter
    else:
      spiv.WrtFlag = 0

    dAC.HCella=256      #     Correlation window Height 
    dAC.WCella=256      #     Correlation window Width
    dAC.HGrid=128      #     Grid distance vertical
    dAC.WGrid=128      #     Grid distance horizontal
    dAC.N_NormEpi=40      #      Semiwidth in the direction normal to the epipolar line
    dAC.RaggioFiltro=9      #       Semiwidth of the filter for the detection of the maximum in the displacement map
    dAC.SogliaCor = 0.6   #     Threshold for the determination of point used in the baricentric search of the maximum in the disp map
    #%% Volume ********************************
    dP.xinfZC = -28    #		Coordinata x inferiore
    dP.yinfZC = -30    #		Coordinata y inferiore
    dP.xsupZC = 20#28    #		Coordinata x superiore	
    dP.ysupZC = 0#15    #		Coordinata y superiore
    # ******************************
    flagReadCalConst=0# if true internal reading
    if flagReadCalConst:
      self.disp.readCalConst()
    else:
      c=0
      cost=[]
      for c in range(2):
        fileName=f'{spiv.percorsocal}{spiv.nomecal}{c}.cal'
        flagCal,numCostCalib,costDum=self.readCalFile(fileName)
        if c==0:
          dP.FlagCal=flagCal
          dP.NumCostCalib=numCostCalib
        else:
          if (dP.FlagCal!=flagCal):
            raise('error the two calibration file are not compatible')
        cost.append(costDum)
      self.disp.setCalConst( flagCal, numCostCalib,cost)
      
    flagReadPlaneConst=0# if true internal reading
    if flagReadPlaneConst:
      if self.disp.readPlaneConst()==0:
        pri.Callback.green('readPlaneConst ok')
    else:
      self.disp.vect.PianoLaser[0]=0
      self.disp.vect.PianoLaser[1]=0
      self.disp.vect.PianoLaser[2]=0

  def initDataStereo(self):
    spiv=self.stereo.SPIVIn
    dP=self.stereo.dataProc
    inPiv=self.stereo.Inp
    
    

    # STEREO CFG file
    # A €£ indicate that the feature is not enabled in the python wrapper
    spiv.nomecal='Cal'    # 		Root of calibration constants
    spiv.NomeCostPiano='disp_1_0.5_0.1_T_1'     # Root of disparity plane constants
    spiv.percorsocal='../cal1/'     # Path of calibration constants
    spiv.FlagParallel=0          # Type of parallel process 0 horizontal 1 vertical (faster but with less information and mor RAM occupied)
    dP.FlagInt=57     #			IS for image reconstruction (only used  when FlagRad==0)
    inPiv.FlagRad=1     #			1 internal (in piv) or 0 external de-warping of the images (the latter €£)
    dP.FlagCoordRad=0     #			when equal to 0 the de-warping is carried on with the larger resolution (pix/mm)
                          #     when equal to 1 (2) the x (y) axis resolution is used 
    spiv.salvarad=0			#    if true and FlagRad is equal to 0 then the dewarped images are saved (€£)


    #                               %  ********************* Input/Output
    spiv.FirstImg=1 # # of first img to be processed (€£)
    spiv.LastImg=1   # # of first last to be processed (€£)
    spiv.Digit=3     # number  of figures i.e. zeros (MAX 10)		 (€£)
    
    
    spiv.ImgRoot='disp_1_0.5_0.1_T_1_cam'   #		Root of the input Images (€£)
    spiv.InDir='../img/'     # Path of the images (€£)
    spiv.InExt='.png'   #			Extension of the images (€£)
    spiv.OutRoot ='disp_1_0.5_0.1_T_1'      #	        Root of the output Files (€£)
    spiv.OutDir ='../out1/'      #                 Output path (€£)
    spiv.OutExt ='.plt'      #                 Output extension (€£)
    spiv.OutFlag = 0        # type of output file : 0 binary Tecplot 1 ascii tecplot (€£)
    spiv.WrtFlag = 1        # 0 only mean values are saved 1 all the instantaneous images are written  (€£)
    spiv.RigaPart=0 		# Starting row (€£)
    spiv.ColPart=0			# Starting Col (€£)
    dP.ImgH=1024 -spiv.RigaPart   # Ending row 
    dP.ImgW=1280 -spiv.ColPart	  # Starting Col
    #                     % *********************** Process parameters
    dP.FlagZonaCom=0   # 			Flag for common zone should be equal to 0
    #           Volume ********************************
    dP.xinfZC = -24     #		  minimum x world coordinates
    dP.yinfZC = -10     #		  minimum y world coordinates
    dP.xsupZC = 24      #		  maximum x world coordinates
    dP.ysupZC = 5       #		  maximum y world coordinates
    spiv.FlagRis=0      #	    0 displacements in m/s 1 in pixels 
    spiv.dt=1000        #	    time separation. If the displacements in mm are needed use 1000 (and 0 for the previous parameter)
    spiv.Sfas=3         #	    in case of images in a single file the distance between images. Normally define the name (€£)
                        #			1=a,b (after number); 2=_1,_2 (after number); 3=a,b (before number)
    #                    % Output
    spiv.FlagRotImg=0         #	    Rotation of the  img 0=no rot 1=90°, 2=180° 3= 270° clockwise	 (£€)
    inPiv.FlagLog=9            #	    0=no 1=video 2=log 3=video e log 4=Log short  5=video e log short (£€)
    spiv.StatFlag =0          #	    stat on: 1 all the vectors 0 only the good ones
    spiv.nomecfgPiv ='StereoProcess.cfg'          #	    name of the cfg file for PIV
  
    # ******************************
    flagReadCalConst=0# if true internal reading
    if flagReadCalConst:
      self.stereo.readCalConst()
    else:
      c=0
      cost=[]
      for c in range(2):
        fileName=f'{spiv.percorsocal}{spiv.nomecal}{c}.cal'
        flagCal,numCostCalib,costDum=self.readCalFile(fileName)
        if c==0:
          dP.FlagCal=flagCal
          dP.NumCostCalib=numCostCalib
        else:
          if (dP.FlagCal!=flagCal):
            raise('error the two calibration file are not compatible')
        cost.append(costDum)
      self.stereo.setCalConst( flagCal, numCostCalib,cost)
      
    flagReadPlaneConst=1# if true internal reading
    if flagReadPlaneConst:
      if self.stereo.readPlaneConst()==0:
        pri.Callback.green('readPlaneConst ok')
    else:
      self.stereo.vect.PianoLaser[0]=0
      self.stereo.vect.PianoLaser[1]=0
      self.stereo.vect.PianoLaser[2]=0
    #piv *******************************************************************************
    
    self.stereo.readCfgProc(spiv.nomecfgPiv)
    
