# -*- coding: utf-8 -*-
"""
@author: Nicolas Berube

Ce code doit être lancé seulement après l'utilisation de Assignation-reboot_part1.py
La complétion des calculs doit être vérifiée via la commande 'screen -ls'. Si des screens sont encore actifs, il faut attendre ou terminer les processus en cours avant de lancer le code actuel
Le code présent doit être lancé via la ligne de commande suivante

    python /Users/berube/Desktop/postdoc/AssignationGenre/Assignation-reboot_part2.py NameKey.txt

Ce code prend une liste de fichier NameKeyLogX.txt et les fusionner dans un nouveau fichier NameKeyLogX.txt

Ce code doit être utilisé seulement après l'utilisation de Assignation-reboot_part1.py. Voyez les commentaires de ce code pour plus d'information.
Si le code Assignation-reboot_part1.py a été interrompue, il faut utiliser le code présent Assignation-reboot_part2.py avant de relancer Assignation-reboot_part1.py

Code realise par Nicolas Berube - aout 2016 - Universite de Montreal - groupe de Vincent Lariviere
"""

from os.path import isfile
from shutil import copyfile
import sys
from bisect import bisect_left

def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return(i)
    else:
        return(-1)    

if len(sys.argv) == 2:
#liste des prenoms separes par \n et doit avoir une ligne vierge a la fin
  inputnames=sys.argv[1]
  output = inputnames[:-4]
else:
  print('Ce code necessite 2 arguments: fichier input, fichier log')
  exit()

#Names: liste de noms a obtenir les genre pour
print('Lecture du input')
names=[]
namefile = open(inputnames,'r',encoding='utf-8')
for n in namefile.readlines():
  names.append(n[:-1])
namefile.close()

#Sauvgarde un back-up du fichier output et log s'il existe deja
print('Sauvegarde des back-ups')
#nombre de fichiers back up log
nbulog = 0
if isfile(output+'Log.txt'):
  nbulog = 1
  while isfile(output+'Log_bu%i.txt'%nbulog):
    nbulog += 1
  copyfile(output+'Log.txt',output+'Log_bu%i.txt'%nbulog)

#nombre de fichiers log
nlog = 1
while isfile(output+'Log%i.txt'%nlog):
  nlog += 1
nlog -= 1

#Lecture des fichiers log et du back-up
datalogtemp=''
if nbulog != 0:
  otemp=''
  filelog = open(output+'Log_bu%i.txt'%nbulog,'r',encoding='utf-8')
  otemp = filelog.read()
  filelog.close()
  datalogtemp += otemp
for i in range(1,nlog+1):
  otemp=''
  filelog = open(output+'Log%i.txt'%i,'r',encoding='utf-8')
  otemp = filelog.read()
  filelog.close()
  datalogtemp += otemp

datalogtemp = datalogtemp.split('\n\n')
if datalogtemp[-1] != '':
    datalogtemp = datalogtemp[:-1]
datalog = []
for d in datalogtemp:
  if len(d) != 0:
    ds = d.split('\n')
    if len(ds) >= 2:
      name = ds[0]
      gend = ds[-1].replace(' ','').split('=')[-1]
      datalog.append([name,gend,d])
      
print('Sorting du fichier log')
datalog = sorted(datalog, key=lambda x: x[0])
datanames = list(map(list, zip(*datalog)))[0]

#Ecriture du fichier log et out
print('Ecriture du fichier log et out')
filelog = open(output+'Log.txt','w',encoding='utf-8')
fileout = open(output+'Out.txt','w',encoding='utf-8')
for name in names:
  ind = index(datanames,name)
  if ind == -1:
    print('!!!! '+name+'\tn\'est pas dans le log')
  else:
    filelog.write(datalog[ind][2]+'\n\n')
    fileout.write(name+'\t'+datalog[ind][1]+'\n')
filelog.close()
fileout.close()

print('Merged %i fichiers log dans '%nlog+output+'Log.txt')
print('Creation du fichier out: '+output+'Out.txt')
if nbulog != 0:
  print('Back-up du log cree dans '+output+'Log_bu%i.txt'%nbulog)
