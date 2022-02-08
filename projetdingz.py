# -*- coding: utf-8 -*-
"""
The goal of this code is to vectorialize a list of event gotten from a DVS128 event-based camera.
The retrieval of the events is made through the dv.py library and the DV software.
All further manipulation are done with the help of matplotlib(especially for it's imshow and imsave methods) and numpy(especially for it's array structure)
This code has been written to use the least space possible, for an integration on a micro-controller.
This code has been written in the mindset that it will be transcribed into C for faster computation.

thus no object based programming has been used.
"""
from dv import *
import matplotlib.pyplot as plt
import numpy as npy
import copy
size = 128
Mattest = npy.zeros((size,size))
polneg=-1
polpos=1
tsh = 1/4

stock = []

def test(port1):
    with NetworkEventInput(address='127.0.0.1', port=port1) as i:
        for event in i:
            print(event.x,event.y)

def SetForExport(): #command to execute before imshow, replaces the pixels by a version that produces more contrast in the resulting pictures
    global polpos
    polpos=255
    global polneg
    polneg=128

def SetForComputation(): #command to execute before computation, sets the polarities to 0 and 1 to run the image manipulation methods 
    global polpos
    polpos=1
    global polneg
    polneg=-1

##############################################################################################################################################
#Aquisition fcnts

def evt_mat(port1): #save a single image from events
    Mat= npy.zeros((size,size))
    evtcnt=0
    pol=0
    global polpos,polneg
    for event in NetworkEventInput(address='127.0.0.1',port=port1):
        if evtcnt<2000:
            if(event.polarity):
                pol=polpos
            else:
                pol=polneg
            Mat[event.y][event.x]=pol
            evtcnt=evtcnt+1
        else: 
            #del(NetworkEventInput)
            ShowMatrix(Mat,'blbl.png')
            return Mat

def evt_mat2(port1): #save images as imageX.png until stopped
    Mat= npy.zeros((size,size))
    evtcnt=0
    imgcnt=0
    pol=0
    global polpos,polneg
    while(1):
        for event in NetworkEventInput(address='127.0.0.1',port=port1):
           if evtcnt<2000:
                if(event.polarity):
                    pol=polpos
                else:
                    pol=polneg
                Mat[event.y][event.x]=pol
                evtcnt=evtcnt+1
           else:
                imgcnt+=1
                name='image' + str(imgcnt) +'.png'
                plt.imsave(name,Mat)
                evtcnt=0
                Mat=npy.zeros((size,size))
        
def evt_mat3(port1): #same as evt_mat2 but keeps the first pixel that was written on the frame, doesn't overwrite any pixel on the image
    Mat= npy.zeros((size,size))
    evtcnt=0
    imgcnt=0
    pol=0
    global polpos,polneg
    while(1):
        for event in NetworkEventInput(address='127.0.0.1',port=port1):
           if evtcnt<2000:
                if(event.polarity):
                    pol=polpos
                else:
                    pol=polneg
                if Mat[event.y][event.x]==0:    
                    Mat[event.y][event.x]=pol
                evtcnt=evtcnt+1
           else:
                imgcnt+=1
                name='image' + str(imgcnt) +'.png'
                plt.imsave(name,Mat)
                evtcnt=0
                Mat=npy.zeros((size,size))
        
def evt_mat4(port1): #same as evt_mat3 except that this code loses no data: whenever an event would replace an existing pixel, the image is saved
    Mat= npy.zeros((size,size))
    imgcnt=0
    pol=0
    global polpos,polneg
    while(1):
        for event in NetworkEventInput(address='127.0.0.1',port=port1):
            if Mat[event.y][event.x]==0:    
                if(event.polarity):
                    pol=polpos
                else:
                    pol=polneg
                Mat[event.y][event.x]=pol
            else:
                name='image' + str(imgcnt) +'.png'
                plt.imsave(name,Mat)
                imgcnt+=1
                Mat=npy.zeros((size,size))     
                if(event.polarity):
                    pol=polpos
                else:
                    pol=polneg
                Mat[event.y][event.x]=pol()
                
def evt_mat5(port1): #creates a "heatmap" of movement , the more events on a pixel, the higher it's value.
    Mat= npy.zeros((size,size))
    evtcnt=0
    pol=0
    global polpos,polneg
    for event in NetworkEventInput(address='127.0.0.1',port=port1):
        if evtcnt<8000: #the event count must be higher than before, as we want to see the ovelapping events.
            if(event.polarity):
                pol=polpos
            else:
                pol=polneg
            Mat[event.y][event.x]+=pol
            evtcnt=evtcnt+1
        else: 
            ShowMatrix(Mat,'blbl.png')
            return Mat
        
def evt_mat6(port1): #Heatmap of the number of events, without considering polarity
    Mat= npy.zeros((size,size))
    evtcnt=0
    pol = 1
    for event in NetworkEventInput(address='127.0.0.1',port=port1):
        if evtcnt<4000: #the event count must be higher than before, as we want to see the ovelapping events.
            Mat[event.y][event.x]+=pol
            evtcnt=evtcnt+1
        else: 
            ShowMatrix(Mat,'blbl.png')
            return Mat
##############################################################################################################################################
# Tying to extrapolate vectors directly from the density of events
#

def Max(M):
    res = 0
    pos = {}
    for i in range(size):
        for j in range(size):
            if abs(M[i][j])>res:
                res = M[i][j]
                pos ={"i" : i,"j" : j}
    return pos

def Vectorize(M,pos): #creates Vectors going out of the pixel on position pos
    VectList = []
    i = pos["i"]
    j = pos["j"]
    pixval = M[i][j]
    s=0
    for op in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,-1),(-1,1)):
        s=abs(pixval-M[i+op[0]][j+op[1]])
        #print('i :' + str(op[0]),'j :' + str(op[1]) ,s)
        VectList.append({"i":op[0],"j":op[1] ,"weight":s})
    return VectList

def SumVect(Vect1,Vect2):
    if(Vect2 == {}):
        return Vect1
    elif(Vect1 == {}):
        return Vect2
    return{"i":Vect1["i"]+Vect2["i"],"j":Vect1["j"]+Vect2["j"],"weight":Vect1["weight"]+Vect2["weight"]}

def MaxVect(VectList):
    maxdist = 0
    Vectmax = []
    for Vect in VectList:
        if Vect["weight"]>maxdist:
            maxdist=Vect["weight"]
            Vectmax = Vect
    return Vectmax

def PixMvt(M,pos,order):
    VectList = []
    VectMax = 0
    Mvt = {}
    for i in range(order):
        VectList = Vectorize(M,pos)
        VectMax = MaxVect(VectList)
        pos={"i":0,"j":0}
        print(VectMax)
        pos["i"]+=int(VectMax["i"])
        pos["j"]+=int(VectMax["j"])
        Mvt = SumVect(VectMax,Mvt)
    return Mvt

def Normalize(M):
    posmax = Max(M)
    valmax = M[posmax["i"]][posmax["j"]]
    for i in range(size):
        for j in range(size):
            M[i][j]/valmax
    return(M)
    

def Print(M):
    for i in range(size):
        for j in range(size):
            M[i][j]=(M[i][j]*255)/Max(M)
    return M

def EvtTreshold(M,tsh): #sets to 0 any pixel that has a value lower than tsh, after this function, the outline fnct can be used.
    for i in range(size):
        for j in range(size):
            if abs(M[i][j])<tsh:
                M[i][j]=0
    return M

def test10(port):
    global Mattest
    global stock
    
    Mattest=evt_mat5(port)
    Normalize(Mattest)
    plt.imsave('Base.png',Mattest)
    
    M = copy.copy(Mattest)

    EvtTreshold(Mattest, 1)
    plt.imsave('Tsh=1.png',Mattest)

    EvtTreshold(Mattest, 2)
    plt.imsave('Tsh=2.png',Mattest)
    
    print(Max(Mattest))
    Mvt = PixMvt(M,Max(M),15)
    print(Mvt)
    
    #outline= GetAllObjects(Mattest)
    
    #m=npy.zeros((127,127))
    #for coo in outline : 
        #m[coo[0]][coo[1]]=1
    #plt.imsave('Step3',m)

##############################################################################################################################################
#Simple image processing treatments

def weakpixels(M): #eliminates all pixels that are 'weak' : pixels that are not close to other pixels where events have happened
    global size
    m=M
    for i in range(size):
        for j in range(size):
            if m[i][j]!=0:
                if IsWeak3x3(m, i, j):
                    print("boo !")
                    M[i][j]=0
                    

def IsWeak3x3(M,i,j): #function for the calculation of the weak pixels
    global tsh
    if i==size-1 or i==0 or j==size-1 or j==0 :
        return True
    if AvgABSNeighbors3x3(M, i, j)<=tsh:
        return True
    else : 
        return False

def holepixels(M): #replaces "holes" in the image, if a pixel is 0 and next to a lot of non-0 values, it is a hole
    global size
    m=M
    for i in range(size):
        for j in range(size):
                if IsHole(m, i, j):
                    M[i][j]=1

def IsHole(M,i,j): #function for the calculation of the holes
    if i==size-1 or i==0 or j==size-1 or j==0 :
        return False
    if AvgABSNeighbors3x3(M, i, j)>=5/8 and M[i][j]==0:
        return True
    else : 
        return False


def AvgABSNeighbors3x3(M,i,j): #computes the average of the absolute value of the pixels around the current pixel
    return (abs(M[i-1][j-1])+abs(M[i-1][j])+abs(M[i-1][j+1])+abs(M[i][j-1])+abs(M[i][j+1])+abs(M[i+1][j-1])+abs(M[i+1][j])+abs(M[i+1][j+1]))/8

def AvgNeighbors3x3(M,i,j): #computes the average of the pixels around the current pixel
    return ((M[i-1][j-1])+(M[i-1][j])+(M[i-1][j+1])+(M[i][j-1])+(M[i][j+1])+(M[i+1][j-1])+(M[i+1][j])+(M[i+1][j+1]))/8

def ZoomMatrix(M,adress): #zooms a 128x128 image to a 256x256 image by extrapolating 2x2 pixels from 1x1 pixels
    m=npy.zeros((2*size,2*size))
    for i in range(size,2):
        for j in range(size,2):
            if M[i][j]==1:
                m[i][j]=255
                m[i+1][j+1]=255
                m[i+1][j]=255
                m[i][j+1]=255
            else :
                if M[i][j]==-1:
                    m[i][j]=128
                    m[i+1][j+1]=128
                    m[i+1][j]=128
                    m[i][j+1]=128
    plt.imsave(adress,m)
    
    
    
def ShowMatrix(M,adress): #changes the polarity +/- 1 to 1 and 255 in order to export the image 
    m=npy.copy(M)
    for i in range(len(M)):
        for j in range(len(M[0])):
            if m[i][j]==1:
                m[i][j]=255
            else :
                if m[i][j]==-1:
                    m[i][j]=128
    plt.imsave(adress,m)
    
    
    
def Meanfilter(M): #Filters the image by checking a threshold on the avg value around the current pixel
    global size
    global pospol
    global negpol
    global Tsh
    m=npy.copy(M)
    avg= 0
    for i in range(size):
        for j in range(size):
            avg=AvgABSNeighbors3x3(m, i, j)
            if avg>=1-Tsh:
                m[i][j]=pospol
            else:
                if avg<Tsh:
                    m[i][j]= negpol
    return m

##############################################################################################################################################

# Functions for the computation of the outline of objects.
#
# To compute our outline we have 3 levels of conditions we must satisfy
# priority 1 => The pixel mustn't be already on the outline
# priority 2 => The pixel mustn't be 0, else it is not part of the outline 
# priority 3 => the chosen pixel must be next to blank pixel, so it is at the limit between the object and the background
#
#The outline is finished when is comes back to the beginning pixel



def Outlining(M,Col,Lig,outline): #recursive ver, not optimized in python :(
    outline.append((Col,Lig))  
    print(outline)
    if len(outline)>1 :
        if outline[0]==outline[-1]:
            print("Success !")
            return outline
    else :
        for c in [0,-1,1]:
            for l in [0,-1,1]:  
                print(c,l)
                if (c!=0 or l!=0) and  HistOutline1(Col+c, Lig+l, outline) and HistOutline2(Col+c,Lig+l,outline) : #conditions of priority 1 
                    if M[Col+c][Lig+l]!=0 : #condition of priority 2
                        if IsAdj0(M,Col+c,Lig+l)==True :#condition of priority 3
                            Outlining(M, Col+c, Lig+l, outline)
        print("oof !")
        
        
def ItOutlining(M,Col,Lig,outline): #iterative version that gets the next point in an outline
    for c in [0,-1,1]:
        for l in [0,-1,1]:  
            if (c!=0 or l!=0) and HistOutline1(Col+c,Lig+l,outline) and HistOutline2(Col+c,Lig+l,outline) and HistOutline3(Col+c,Lig+l,outline): #conditions of priority 1 
                if M[Col+c][Lig+l]!=0 : #condition of priority 2
                    if IsAdj0(M,Col+c,Lig+l)==True :#condition of priority 3
                        outline.append((Col+c,Lig+l))
                        return()
                    
                    
#FINAL outlining code
def ItOutlining3(M,ColStart,LigStart): #iterative version of outlining that gives the full outline around an object from which (i,j) is a pixel
    outline=[]
    outline.append((ColStart,LigStart))
    while(len(outline)<3 or outline[0]!=outline[-1]):
         ItOutlining(M,outline[-1][0],outline[-1][1],outline) 
    return outline

def IsAdj0(M,i,j):  #function to check if the pixel is next to a blank pixel
    if (M[i-1][j-1])==0 or (M[i-1][j])==0 or (M[i-1][j+1])==0 or (M[i][j-1])==0 or (M[i][j+1])==0 or (M[i+1][j-1])==0 or (M[i+1][j])==0 or (M[i+1][j+1])==0:
        return True
    else:
        return False

#HistOutlineN checks for the Nth position before the last and compares it to the given position of the current pixel.
#if our list of points is smaller than N, we default to True.

def HistOutline1(i,j,outline):
    N=len(outline)
    if N<1:
        return True
    elif (i == outline[N-1][0] and j == outline[N-1][1]):
        return False
    else:
        return True 
          
def HistOutline2(i,j,outline):
    N=len(outline)
    if N<2:
        return True
    elif (i == outline[N-2][0] and j == outline[N-2][1]):
        return False
    else :
        return True 

def HistOutline3(i,j,outline):
    N=len(outline)
    if N<3:
        return True
    elif (i == outline[N-3][0] and j == outline[N-3][1]):
        return False
    else :
        return True
    
#Using HistOutline we limit ourselves to 3 steps before in the outline, TestForOutline is a function that tests for all positions of the outline :
#safer but much slower.
#For most non-noisy real shapes,going back 3 steps is enough to draw the outline. 
    
def TestForOutline(Col,Lig,outline): 
    for coordinates in outline :
        if (Col,Lig)==coordinates:
            return True
    return False
    

##############################################################################################################################################
#Using the outline we now want to extrapolate vectors 
#to this use we split the outlines between polarity 1 and -1 into two images
#If the object is an actual real moving object, the outline will be divided in a mostly positive part and a mostly negative part
#We split the outline into two images, then we fill both outline and compares them afterward
#

def DrawObject(M,Object):
    m = npy.zeros(size,size)
    for coordinates in Object:
        m[coordinates[0]][coordinates[1]]=M[coordinates[0]][coordinates[1]]
    return m



def Moise(M):  #splits the input matrix into two matrixes mpos and mneg depending on polarity
    mpos = npy.zeros((size,size));
    mneg = npy.zeros((size,size));
    for i in range(size):
        for j in range(size):
            if M[i][j]==1:
                mpos[i][j]=1
            elif M[i][j]==-1:
                mneg[i][j]=1
    return mpos,mneg


##############################################################################################################################################
#The goal here is to list all objects in the image
#for this we first search a non0 pixel on the image
#Each pixel in an outline is associated with an object
#the last pixel is (127,127); it is returned when all objects have been identified
#

def GetAllObjects(M):
    Objects = []
    outline = []
    Col = 0
    Lig = 0
    while Col<size:
        while Lig<size: #we go through all pixels of the image
            if abs(M[Col][Lig])>1:
                if IsAdj0(M, Col, Lig):
                    if TestForOutline(Col,Lig,outline):
                        (Col,Lig)=SkipObject(Col,Lig,outline)
                    else:
                        ItOutlining3(M,Col,Lig,outline)
                        Objects.append(outline)
                        (Col,Lig)=SkipObject(Col,Lig,outline)
        Col+=1
        Lig+=1
    return Objects
            

def SkipObject(Col,Lig,outline): # skips all pixels from a given object (in the form of outline) in the current column
    for coordinates in outline:
        if coordinates[0]==Col and coordinates[1]!=Lig:
            return coordinates
    #if the object is not fully on the screen, this function may not find the target pixel to go to
    #this happens only when the top/bottom half of an object is off the screen.In which case we can go to the next column.
    #We supposed that our objects of interest were all well framed, so this case shouldn't happen.
    print("Object is not well framed :|")
    return (126,126)
   


# def GetNon0(M,Col,Lig,outline):
#     if Col==0 and Lig==0:
#         return GetFirstNon0
#     else : 
#         return GetNextNon0(M, Col, Lig, outline)
#     return ((127,127))


def Get3x3(M,i,j):
    hood = npy.zeros((3,3))
    i=i-1
    j=j-1
    for k in range(3):
        for l in range(3):
                hood[k,l]=(M[i+k][j+l])
    return hood


#Testing fncts
#
#the main function show the full procedure that is applied to our events to become vectors, each step is saved to a new image
#

def TestOutline(M):
    m=npy.zeros((128,128))
    outline = []
    ShowMatrix(M,'blbl.png')  
    outline=ItOutlining3(M,64,64)
    for coo in outline : 
        m[coo[0]][coo[1]]=1
    plt.imsave('blblbl.png',m)

def main(port):
    global Mattest
    global Tsh
    SetForComputation()
    
    Mattest=evt_mat5(port)
    ShowMatrix(Mattest,'Base.png')
    
    Tsh=5/8
    weakpixels(Mattest)
    ShowMatrix(Mattest,'Step1.png')
    
    holepixels(Mattest)
    ShowMatrix(Mattest,'Step2.png')
    
    (i,j)=GetNon0(Mattest,0,0)
    outline=ItOutlining3(Mattest,i,j)
    
    m=npy.zeros((127,127))
    for coo in outline : 
        m[coo[0]][coo[1]]=1
    plt.imsave('Step3',m)


#while(1): main(44737)
