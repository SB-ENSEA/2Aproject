# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from dv import *
import matplotlib.pyplot as plt
import numpy as npy

size = 128
Mattest = npy.zeros((size,size))
polneg=-1
polpos=1
tsh = 1/4

def test(port1):
    with NetworkEventInput(address='127.0.0.1', port=port1) as i:
        for event in i:
            print(event.x,event.y)

def SetForExport():
    global polpos
    polpos=255
    global polneg
    polneg=128

def SetForComputation():
    global polpos
    polpos=1
    global polneg
    polneg=-1




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
                Mat[event.y][event.x]=pol
           
            
           
def weakpixels(M): #eliminates all pixels that are 'weak' : pixels that are not close to other pixels where events have happened
    global size
    m=M
    for i in range(size):
        for j in range(size):
            if m[i][j]!=0:
                if IsWeak3x3(m, i, j):
                    print("boo !")
                    M[i][j]=0
                    

def IsWeak3x3(M,i,j):
    global tsh
    if i==size-1 or i==0 or j==size-1 or j==0 :
        return True
    if AvgABSNeighbors3x3(M, i, j)<=tsh:
        return True
    else : 
        return False

def holepixels(M): #replaces "holes" in the image, if a pixel is 0 and next to a lot of non0 values, it is a hole
    global size
    m=M
    for i in range(size):
        for j in range(size):
                if IsHole(m, i, j):
                    print("woo !")
                    M[i][j]=1

def IsHole(M,i,j):
    global tsh
    if i==size-1 or i==0 or j==size-1 or j==0 :
        return False
    if AvgABSNeighbors3x3(M, i, j)>4/8 and M[i][j]==0:
        return True
    else : 
        return False


def AvgABSNeighbors3x3(M,i,j): #computes the average of the pixels around a pixel at index i,j 
    return (abs(M[i-1][j-1])+abs(M[i-1][j])+abs(M[i-1][j+1])+abs(M[i][j-1])+abs(M[i][j+1])+abs(M[i+1][j-1])+abs(M[i+1][j])+abs(M[i+1][j+1]))/8

def AvgNeighbors3x3(M,i,j):
    return ((M[i-1][j-1])+(M[i-1][j])+(M[i-1][j+1])+(M[i][j-1])+(M[i][j+1])+(M[i+1][j-1])+(M[i+1][j])+(M[i+1][j+1]))/8

def ZoomMatrix(M,adress):
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
    
    
    
def ShowMatrix(M,adress):
    m=npy.copy(M)
    for i in range(len(M)):
        for j in range(len(M[0])):
            if m[i][j]==1:
                m[i][j]=255
            else :
                if m[i][j]==-1:
                    m[i][j]=128
    plt.imsave(adress,m)
    
    
    
def Meanfilter(M): #computes the image through a mean filter
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


def Outlining(M,Col,Lig,outline): #recursive ver, currently not working
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
        
        
def ItOutlining(M,Col,Lig,outline):
    for c in [0,-1,1]:
        for l in [0,-1,1]:  
            if (c!=0 or l!=0) and HistOutline1(Col+c,Lig+l,outline) and HistOutline2(Col+c,Lig+l,outline) and HistOutline3(Col+c,Lig+l,outline): #conditions of priority 1 
                print("blbl")
                if M[Col+c][Lig+l]!=0 : #condition of priority 2
                    if IsAdj0(M,Col+c,Lig+l)==True :#condition of priority 3
                        outline.append((Col+c,Lig+l))
                        print(outline)
                        return()
                    
                    

def ItOutlining2(M,ColStart,LigStart):
    outline=[]
    outline.append((ColStart,LigStart))
    while(len(outline)<3 or outline[0]!=outline[-1]):
        Col,Lig = outline[-1]
        for c in [0,-1,1]:
            for l in [0,-1,1]:  
                if (c!=0 or l!=0) and HistOutline1(Col+c, Lig+l, outline) and HistOutline2(Col+c,Lig+l,outline) and HistOutline3(Col+c,Lig+l,outline): #conditions of priority 1 
                    if M[Col+c][Lig+l]!=0 : #condition of priority 2
                        if IsAdj0(M,Col+c,Lig+l)==True :#condition of priority 3
                            outline.append((Col+c,Lig+l))
                            print(outline)
    return outline
            
def ItOutlining3(M,ColStart,LigStart):
    outline=[]
    outline.append((ColStart,LigStart))
    while(len(outline)<3 or outline[0]!=outline[-1]):
         ItOutlining(M,outline[-1][0],outline[-1][1],outline) 
    return outline

def IsAdj0(M,i,j):
    if (M[i-1][j-1])==0 or (M[i-1][j])==0 or (M[i-1][j+1])==0 or (M[i][j-1])==0 or (M[i][j+1])==0 or (M[i+1][j-1])==0 or (M[i+1][j])==0 or (M[i+1][j+1])==0:
        return True
    else:
        return False

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

def Moise(M):
    m1 = npy.zeros((127,127));
    m2 = npy.zeros((127,127));
    for i in range(size):
        for j in range(size):
            if M[i][j]==1:
                m1[i][j]=1
            elif M[i][j]==-1:
                m2[i][j]=1
    return m1,m2

def TestForOutline(Col,Lig,outline):
    for coordinates in outline :
        if (Col,Lig)==coordinates:
            return True
    return False

def TestOutline():
    m=npy.zeros((128,128))
    M=plt.imread("blblblbl.png")
    outline = []
    plt.imsave('blbl.png',M)  
    # outline.append((64,64))
    # while(len(outline)<3 or outline[0]!=outline[-1]):
    #      ItOutlining(Cercle,outline[-1][0],outline[-1][1],outline) 
    #outline=ItOutlining2(Cercle,64,64)   
    outline=ItOutlining3(M,64,64)
    for coo in outline : 
        m[coo[0]][coo[1]]=1
    plt.imsave('blblbl.png',m)
    


def GetFirstNon0(M):
    for i in range(size):
        for j in range(size):
            if M[i][j]==1 and IsAdj0(M,i,j):
                return((i,j))

def GetNextNon0(M,Col,Lig,outline):
    for i in range(size):
        for j in range(size):
            if M[i][j]==1:
                if IsAdj0(M, i, j):
                    if TestForOutline(Col, Lig, outline):
                        return (Col,Lig)
    return (127,127)
                    
def GetNon0(M,Col,Lig,outline):
    if Col==0 and Lig==0:
        return GetFirstNon0
    else : 
        return GetNextNon0(M, Col, Lig, outline)
    
    return ((127,127))
def Get3x3(M,i,j):
    hood = npy.zeros((3,3))
    i=i-1
    j=j-1
    for k in range(3):
        for l in range(3):
                hood[k,l]=(M[i+k][j+l])
    return hood

def main(port):
    global Mattest
    global Tsh
    SetForComputation()
    
    Mattest=evt_mat(port)
    ShowMatrix(Mattest,'et1.png')
    
    Tsh=5/8
    weakpixels(Mattest)
    ShowMatrix(Mattest,'et2.png')
    
    holepixels(Mattest)
    holepixels(Mattest)
    ShowMatrix(Mattest,'et3.png')
    
    (i,j)=GetNon0(Mattest,0,0)
    outline=ItOutlining3(Mattest,i,j)
    
    m=npy.zeros((127,127))
    for coo in outline : 
        m[coo[0]][coo[1]]=1
    plt.imsave('et4',m)
    
    
    
    

                
#while(1): main(44737)
