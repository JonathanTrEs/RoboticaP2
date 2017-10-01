#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Rob�tica Computacional - Curso 2014/2015
# Grado en Ingenier�a Inform�tica (Cuarto)
# Pr�ctica: Resoluci�n de la cinem�tica inversa mediante CCD
#           (Cyclic Coordinate Descent).

import sys
from math import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import colorsys as cs

# ******************************************************************************
# Declaraci�n de funciones

def muestra_origenes(O,final=0):
  # Muestra los or�genes de coordenadas para cada articulaci�n
  print('Origenes de coordenadas:')
  for i in range(len(O)):
    print('(O'+str(i)+')0\t= '+str([round(j,3) for j in O[i]]))
  if final:
    print('E.Final = '+str([round(j,3) for j in final]))

def muestra_robot(O,obj):
  # Muestra el robot graficamente
  plt.figure(1)
  plt.xlim(-L,L)
  plt.ylim(-L,L)
  T = [np.array(o).T.tolist() for o in O]
  for i in range(len(T)):
    plt.plot(T[i][0], T[i][1], '-o', color=cs.hsv_to_rgb(i/float(len(T)),1,1))
  plt.plot(obj[0], obj[1], '*')
  plt.show()
  raw_input()
  plt.clf()

def matriz_T(d,th,a,al):
  # Calcula la matriz T (�ngulos de entrada en grados)
  return [[cos(th), -sin(th)*cos(al),  sin(th)*sin(al), a*cos(th)]
         ,[sin(th),  cos(th)*cos(al), -sin(al)*cos(th), a*sin(th)]
         ,[      0,          sin(al),          cos(al),         d]
         ,[      0,                0,                0,         1]
         ]

def cin_dir(th,a):
  #Sea 'th' el vector de thetas
  #Sea 'a'  el vector de longitudes
  T = np.identity(4)
  o = [[0,0]]
  for i in range(len(th)):
    T = np.dot(T,matriz_T(0,th[i],a[i],0))
    tmp=np.dot(T,[0,0,0,1])
    o.append([tmp[0],tmp[1]])
  return o

# ******************************************************************************
# C�lculo de la cinem�tica inversa de forma iterativa por el m�todo CCD

# valores articulares arbitrarios para la cinem�tica directa inicial
th=[ 0.,0.,0.]
a =[5.,5.,5.]
lmin=[-pi*.75,  0, -pi*.75] # l�mite m�nimo de cada articulaci�n
lmax=[ pi*.75, 10,  pi*.75] # l�mite m�ximo de cada articulaci�n
p =[0,1,0] # 0:rotaci�n, 1:prism�tica
L = sum(a) # variable para representaci�n gr�fica
EPSILON = .01

plt.ion() # modo interactivo

# introducci�n del punto para la cinem�tica inversa
if len(sys.argv) != 3:
  sys.exit("python " + sys.argv[0] + " x y")
objetivo=[float(i) for i in sys.argv[1:]]

O=range(len(th)+1) # Reservamos estructura en memoria
O[0]=cin_dir(th,a) # Calculamos la posicion inicial
print "- Posicion inicial:"
muestra_origenes(O[0])

dist = float("inf")
prev = 0.
iteracion = 1
while (dist > EPSILON and abs(prev-dist) > EPSILON/100.):
  prev = dist
  # Para cada combinaci�n de articulaciones:
  for i in range(len(th)):
    # c�lculo de la cinem�tica inversa:
    actual = len(th)-i-1
    if not p[actual]: # si no es prism�tica:
      v1=np.subtract(objetivo,O[i][actual])
      v2=np.subtract(O[i][-1],O[i][actual])
      c1=atan2(v1[1],v1[0])
      c2=atan2(v2[1],v2[0])
      th[actual] += c1 - c2
      
      # convertir el valor del �ngulo al intervalo [-pi,pi]
      while th[actual] > pi:
        th[actual] = th[actual] - 2*pi

      while th[actual] < -pi:
        th[actual] = th[actual] + 2*pi
      # limitar con el valor m�nimo que puede tomar la articulaci�n
      if th[actual] < lmin[actual]:
        th[actual] = lmin[actual]
      # limitar con el valor m�ximo que puede tomar la articulaci�n
      if th[actual] > lmax[actual]:
        th[actual] = lmax[actual]

    else:
      w = sum(th[:actual+1])                 # Sumatorio de 'th' de 0 hasta 'actual' (incluido)
      v = np.subtract(objetivo,O[i][-1])     # Calcular vector que va de 'O[i][-1]' a 'objetivo'
      a[actual] += np.dot([cos(w),sin(w)],v) # Proyecci�n escalar, mediante 'np.dot', del vector unitario
                                             # orientado con el �ngulo 'w', y 'v' (ver apuntes).



      # limitar con el valor m�nimo que puede tomar la articulaci�n
      if th[actual] < lmin[actual]:
        th[actual] = lmin[actual]
      # limitar con el valor m�ximo que puede tomar la articulaci�n
      if th[actual] > lmax[actual]:
        th[actual] = lmax[actual]

    O[i+1] = cin_dir(th,a)

  dist = np.linalg.norm(np.subtract(objetivo,O[-1][-1]))
  print "\n- Iteracion " + str(iteracion) + ':'
  muestra_origenes(O[-1])
  muestra_robot(O,objetivo)
  print "Distancia al objetivo = " + str(round(dist,5))
  iteracion+=1
  O[0]=O[-1]

if dist <= EPSILON:
  print "\n" + str(iteracion) + " iteraciones para converger."
else:
  print "\nNo hay convergencia tras " + str(iteracion) + " iteraciones."
print "- Umbral de convergencia epsilon: " + str(EPSILON)
print "- Distancia al objetivo:          " + str(round(dist,5))
print "- Valores finales de las articulaciones:"
for i in range(len(th)):
  print "  theta" + str(i+1) + " = " + str(round(th[i],3))
for i in range(len(th)):
  print "  L" + str(i+1) + "     = " + str(round(a[i],3))
