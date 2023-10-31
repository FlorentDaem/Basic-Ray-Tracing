## Sim lum


## A faire

# Prendre en compte le fait que l'image est flip pour les y... : ptet redéfinir le repère

#pouvoir tourner la tête plus que ça : ptet mettre le curseur en permanence au milieu











## Imports

import math
import numpy as np
import matplotlib.pyplot as plt
import pygame as pg
from pygame.locals import *
from PIL import Image
import pylab as pyl


pg.init() #Initialise pygame


## Fonctions de base


def point(x,y,z):
    return np.array([x,y,z])

def coul(r,g,b):
    return np.array([r,g,b])


## Fonctions mathématiques


def sym(u,proj):
    '''symétrie associé au proj'''
    w=2*proj(u)-u
    return w



## Classes


class sphere:
    def __init__(self,cara,kd,kr):
        self.type="sphere"
        self.cara=cara
        self.kd=kd
        self.kr=kr
    def intersection(self,r):
        (A,u)=r
        (C,R)=self.cara
        CA=vec(C,A)
        a=1
        b=2*np.dot(u,CA)
        c=norme(CA)**2-R**2
        D=b**2-4*a*c
        if D>=0:
            t1=(-b+math.sqrt(D))/(2*a)
            t2=(-b-math.sqrt(D))/(2*a)
            t=min((t1,t2))
            if t<=0:
                t=max((t1,t2))
            if t>0:
                return (pt(r,t),t)



class plan:
    def __init__(self,cara,kd,kr):
        self.type='plan'
        self.cara=cara
        self.kd=kd
        self.kr=kr
    def intersection(self,r):
        (A,u)=r
        (P,N)=self.cara
        if np.dot(u,N)<0:
            t=(-np.dot(N,A)+np.dot(N,P))/np.dot(u,N)
            if t!=0:
                return (pt(r,t),t)


## Variables


Run=True


#Base absolue
e1=point(1,0,0)
e2=point(0,1,0)
e3=point(0,0,1)


#Base relative
omega=point(0.,0.,-4.)
u1=e1
u2=e2
u3=e3
#u3 est la direction et u1 u2 u3 forment une base orthonormée directe


#Résolution et fov
N=2 #HD : 120
Nx=N*16
Ny=N*9
D=0.8
Dx=D*16
Dy=D*9

alpha=np.pi/1.75

d=Dx/(2*np.tan(alpha/2))


#Couleurs
noir=coul(10,10,10)
blanc=coul(255,255,255)



#Scène

Objet=[
sphere([point(0,0,2),1],(0.75,0.75,0.75),0.5),
sphere([point(-3,1,1),1],(0.75,0,0.75),0.5),
plan([point(5,0,0),-e1],(0.75,0   ,0   ),0.5),
plan([point(0,-5,0),e2],(0   ,0.75,0   ),0.5),
plan([point(-5,0,0),e1],(0   ,0   ,0.75),0.5),
plan([point(0,5,0),-e2],(0.75,0.75,0   ),0.5),
plan([point(0,0,-5),e3],(0.75,0   ,0.75),0.5),
plan([point(0,0,5),-e3],(0   ,0.75,0.75),0.5)
]



no=len(Objet)


Source=[
point(0,0,0)
]

ColSrc=[
blanc*0.75
]

ns=len(Source)




## I - Géométrie


def vec(A,B):
    '''renvoie le vecteur AB '''
    return B-A


def ps(v1,v2):
    '''produit scalaire'''
    return v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]


def norme(v):
    return math.sqrt(ps(v,v))


def unitaire(v):
    return 1/norme(v)*v


def pt(r, t):
    '''renvoie le point à une distance t sur le rayon r'''
    # assert t >= 0
    (S, u) = r
    return S + t * u


def dir(A, B):
    '''direction du vecteur AB'''
    return unitaire(vec(A, B))


def ra(A, B):
    '''définit un rayon partant de A et de direction AB'''
    return (A, dir(A, B))

def sp(A,B):
    '''définit une sphère de centre A et de rayon AB'''
    r=norme(vec(A,B))
    return (A,r)





## II - Optique


#Visibilité

def au_dessus(s,P,src):
    (C,r)=s.cara
    CP=vec(C,P)
    CS=vec(C,src)
    return np.dot(CP,CS)>=r**2




def visible(obj,j,P,src):
    "Détermine si la source est visible du point P appartenant à la sphere j (si rien ne la bloque)"
    if 1!=0:
        r=ra(src,P)
        s=obj[j]
        (C,R)=s.cara
        if s.type=='sphere':
            if au_dessus(s,P,src):
                (I,t1)=s.intersection(r)
                for i in range(no):
                    if i!=j:
                        inters=obj[i].intersection(r)
                        if inters!=None:
                            (I,t2)=inters
                            if t2<=t1:
                                return False
                return True #Si aucune intersection n'a lieu avant celle avec l'objet, alors la source est visible de P
            else:
                return False
        else:
            inters=s.intersection(r)
            if inters!=None:
                (I,t1)=inters
                for i in range(no):
                    if i!=j:
                        inters=obj[i].intersection(r)
                        if inters!=None:
                            (I,t2)=inters
                            if t2<=t1:
                                return False
                return True #Si aucune intersection n'a lieu avant celle avec l'objet, alors la source est visible de P
            else:
                return False
    else:
        return False



#Diffusion


def couleur_diffusee(r,Cs,N,kd):
    (S,u)=r
    (Rs,Vs,Bs)=Cs
    (kdr,kdv,kdb)=kd
    cost=np.dot(N,-u)
    Rd=Rs*kdr*cost
    Vd=Vs*kdv*cost
    Bd=Bs*kdb*cost
    return np.array([Rd,Vd,Bd])


#Reflexion


def rayon_reflechi(s,P,src):
    (C,R)=s
    N=dir(C,P)
    v=vec(P,src)
    w=sym(v,lambda x: np.dot(x,N)*N)
    return (P,w)


## IV - Lancer de rayons


#Ecran


def grille(i,j):
    #coordonnées relatives à omega
    xr=-((j+1/2)*Dx/Nx-Dx/(2))*u1
    yr=-((i+1/2)*Dy/Ny-Dy/(2))*u2
    zr=d*u3
    vr=xr+yr+zr
    #coordonnées absolues
    xa=omega[0]+np.dot(vr,e1)
    ya=omega[1]+np.dot(vr,e2)
    za=omega[2]+np.dot(vr,e3)
    return (xa,ya,za)


def rayon_ecran(omega,i,j):
    E=grille(i,j)
    return ra(omega,E)


#Couleur d'un pixel


def interception(r):
    "Prend en paramètre un rayon r et renvoie le premier point matériel de la scène atteint par ce rayon ainsi que l’indice de la sphère concernée dans la liste Objet. Si le rayon n’intercepte aucune sphère, la fonction renvoie None"
    for i in range(no):
        si=Objet[i]
        inters=si.intersection(r)
        if inters!=None:
            (P,t)=inters
            if visible(Objet,i,P,r[0]):
                return (P,i)


def couleur_diffusion(P,j):
    Cd=noir
    for k in range(ns):
        if visible(Objet,j,P,Source[k]):
            r=ra(Source[k],P)
            Cs=ColSrc[k]
            kd=Objet[j].kd
            if Objet[j].type=='sphere':
                (C,R)=Objet[j].cara
                N=dir(C,P)
            else:
                N=Objet[j].cara[1]
            Cd=Cd + couleur_diffusee(r,Cs,N,kd)
    return Cd


#Constitution de l'image




def lancer(omega,fond):
    im=np.zeros((Ny,Nx,3))
    for j in range(Nx):
        for i in range(Ny):
            r=rayon_ecran(omega,i,j)
            interc=interception(r)
            if interc==None:
                im[i,j]=fond
            else:
                (P,q)=interc
                (R,G,B)=couleur_diffusion(P,q)
                im[i,j]=[R,G,B]
    return im


## Améliorations


#Prise en compte de la réflexion


def reflexions(r,rmax):
    L=[]
    nbr=0
    while nbr<=rmax:
        if interception(r)!=None:
            (P,j)=interception(r)
            L.append((P,j))
            src=r[0]
            r=rayon_reflechi(Objet[j],P,src)
        nbr+=1
    return L


def couleur_percue(r,rmax,fond):
    Lref=reflexions(r,rmax)
    C=fond
    if len(Lref)<1:
        return C
    else:
        (P,j)=Lref[0]
        src=r[0]
        r=rayon_reflechi(Objet[j],P,src)
        C=couleur_diffusion(P,j)
        C=C+KrObjet[j]*couleur_percue(r,rmax-1,fond)
    # C=normeCoul(C)
    return C


#Prise en compte de la saturation


def normeCoul(C):
    (R,G,B)=C
    if R>=1:
        R=1
    if G>=1:
        G=1
    if B>=1:
        B=1
    return coul(R,G,B)


def lancer_reflexion(omega,fond,rmax):
    im=np.empty((Ny,Nx,3))
    for i in range(Ny):
        for j in range(Nx):
            r=rayon_ecran(omega,i,j)
            im[i,j]=couleur_percue(r,rmax,fond)
    return im




## Conclusion Raytracing



def GenereImg(omega,fond,rmax):
    if rmax==0:
        return lancer(omega,fond)
    else:
        return lancer_reflexion(omega,fond,rmax)




# plt.imshow(lancer(omega,noir))
# # plt.imshow(lancer_complet(omega,noir,2))
# plt.axis('off')
# plt.show()





## Variables animation


du3=0.1
du1=0.1
du2=0.1






## annimations







k=0

def Update():
    global k
    global Source
    k+=10**-1
    Source[0][1]=Source[0][1]+4*np.sin(k)


def Affiche():
    im=GenereImg(omega,noir,0)
    im=np.swapaxes(im, 0, 1) #Seule façon que j'ai trouvé de corriger l'affichage avec pygame (transposée)
    surf = pg.surfarray.make_surface(im)
    canvas.blit(pg.transform.scale(surf,canvas.get_rect().size),(0, 0)) # Adapte l'image à l'écran
    canvas.blit(surf,(0, 0)) # Affiche l'image en taille réelle
    pg.display.update()



canvas=pg.display.set_mode()


pg.mouse.set_visible(False)



while Run:

    Update()
    Affiche()

    #Evènements
    for event in pg.event.get():

        #Appuyer sur la croix
        if event.type == QUIT:
            Run = 0

        #Touches
        if event.type == KEYDOWN:
            #Quitter (echap)
            if event.key == K_ESCAPE:
                Run = 0

            #gauche/droite
            if event.key == K_d:
                omega-=du1*u1
            if event.key == K_q:
                omega+=du1*u1
            #devant/derriere
            if event.key == K_z:
                omega+=du3*u3
            if event.key == K_s:
                omega-=du3*u3
            #haut/bas
            if event.key == K_SPACE:
                omega+=du2*u2
            if event.key == K_LCTRL:
                omega-=du2*u2
        #Souris
        if event.type == MOUSEMOTION:
            (sx,sy)=pg.mouse.get_rel() #prend les variations x y de la souris
            dpi=10**-3
            sx*=-dpi
            sy*=dpi
            #pour gauche/droite
            u3new=u3+sx*u1
            u1new=u1-sx*u3
            u3=unitaire(u3new)
            u1=unitaire(u1new)
            #pour haut/bas
            u2new=u2+sy*u3
            u3new=u3-sy*u2
            u3=unitaire(u3new)
            u2=unitaire(u2new)



pg.quit()


