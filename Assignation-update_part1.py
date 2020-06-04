#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Nicolas Berube

Ce code doit être utilisé conjointement avec Assignation-update_part2.py

Ce code prend une liste de prénoms séparés par un retour à la ligne \n dans un fichier .txt (NameKey.txt) et update la base de donnée existante (NameKeyOut.txt) avec les nouveaux noms qui n'y sont pas présents en leur attribuant un genre.
L'attribution du genre (M, F, UNI, INI ou UNK) se fait selon l'occurence de prenoms sur des pages Wikipedia les concernant.
Les noms déjà présents dans la base de données existante (NameKeyOut.txt) ne sont pas analysés.
Les informations sur l'attribution du genre sont présentes dans le fichier log (NameKeyLog.txt). C'est ce fichier qui est utilisé pour les calculs.

Si un fichier NameKeyLog.txt existe, il sera copié dans NameKeyLog_buX.txt ou X est un numéro.
Les résultats seront dans un ou plusieurs fichiers NameKeyLogX.txt ou X est un numéro.
Le code Assignation-update_part2.py doit ensuite être utilisé pour fusionner tous les fichier NameKeyLogX.txt dans un nouveau fichier NameKeyLog.txt
Si le code est terminé, ou s'il a planté, il faut utiliser Assignation-update_part2.py, puis repartir le code Assignation-update_part1.py

Code realise par Nicolas Berube - aout 2016 - Universite de Montreal - groupe de Vincent Lariviere
"""

from os.path import isfile
from wikipedia import search, summary
from math import floor
import wikipedia
import sys
from bisect import bisect_left
from unidecode import unidecode

inputnames = '/Users/berube/Desktop/postdoc/AssignationGenre/NameKey.txt'
#(la derniere linge doit etre vierge!)

def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return(i)
    else:
        return(-1)
    
def countalpha(name):
    'Retourne le nombre de caracteres alphabetique, avec ou sans accents'
    i = 0
    for c in name:
        if unidecode(c) in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            i += 1
    return(i)

def countvowel(name):
    'Retourne le nombre de voyelles, avec ou sans accents'
    i = 0
    for c in name:
        if unidecode(c) in 'aeiouyAEIOUY':
            i += 1
    return(i)

def lectdatalog(filelog):
    'Lecture des fichiers log pour mise en mémoire'
    datalogtemp=''
    filelog = open(filelog,'r',encoding='utf-8')
    datalogtemp = filelog.read()
    filelog.close()
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
    datalog = sorted(datalog, key=lambda x: x[0])
    datanames = list(map(list, zip(*datalog)))[0]
    return(datalog,datanames)

#Vieux code pour reboot
"""
if len(sys.argv) == 4:
#liste des prenoms separes par \n et doit avoir une ligne vierge a la fin
  inputnames=sys.argv[1]
#tn = nombre total de calculs simultanes
#cn = code actuel. cn <= tn
  tn = int(sys.argv[2])
  cn = int(sys.argv[3])
else:
  print('Ce code necessite 3 arguments: fichier input, nombre total de calculs lances et numero du calcul actuel. Utiliser le script bash pour lancer un calcul avec WiGen.')
  exit()
"""
tn = 1
cn = 1

#names: liste de noms a trouver le genre
namestot=[]
namefile = open(inputnames,'r',encoding='utf-8')
for n in namefile.readlines():
  namestot.append(n[:-1])
namefile.close()

print('Sorting du input')
namestot = sorted(namestot)

print('Lecture du log')
otempsn = ['']
otemps = [['','UNK','\nname is empty\n = UNK']]
if isfile(inputnames[:-4]+'Log.txt'):
    otemps,otempsn = lectdatalog(inputnames[:-4]+'Log.txt')


#Prend la sous-section necessaire aux names
namesfil = []
#ntrack: pour progress bar
ntrack = 0
ntrack2 = 0
i = 0
for n in namestot:
  ntrack += 1
  if ntrack > len(namestot)/20:
    ntrack2 += 1
    ntrack = 0
    print('Traitement des noms: %i%%'%(ntrack2*5))
  if n == otemps[i][0] and i+1 != len(otemps):
    i += 1
  else:
    namesfil.append(n)

names=[]
c = 1
i = 0
deb = 0
for n in namestot:
  if c == cn:
    names.append(n)
  if namesfil[i] == n and i+1 < len(namesfil):
    i += 1
    deb = 0
  if i%int(floor(len(namesfil)/float(tn))) == 0 and i != 0 and c != tn and deb == 0:
    c += 1
    deb = 1

#ntrack: pour progress bar
ntrack = 0
filelog = open(inputnames[:-4]+'Log%i.txt'%cn,'w',encoding='utf-8')
for name in names:
  ntrack += 1
#si le nom est deja dans le .out
  ind = index(otempsn,name)
  if ind != -1:
    filelog.write(otemps[ind][2])
  elif len(name) == 0 or len(name.split()) == 0 or name.upper() == 'NULL':
    filelog.write(name+'\nname is empty\n'+name+' = INI')
  elif countalpha(name) <= 1 or countvowel(name) == 0:
    filelog.write(name+'\nname is initials\n'+name+' = INI')
  else:
    filelog.write(name)
    gender = 'UNK'
#genh: nombre de pages retournant un homme. genf: femme
    genh = 0
    genf = 0
#Considere seulement la premiere partie du nom si nom compose et corrige la casse
    namesplit = name.replace('-',' ').split()
    if len(namesplit[0]) == 1:
      nam = namesplit[0].upper()
    else:
      nam = namesplit[0][0].upper()+namesplit[0][1:].lower()
#Choisis les parametres de recherche si la recherche precedente n'a pas retourne de resultats. 0: existence d'une page PRENOM (given name), 1: PRENOM NOM, 2: analyse de la liste des pages et non de leur contenu, 3: NOM PRENOM
    ntry = 0
    while ntry <= 1 and gender == 'UNK':
      ntry += 1
#filtered pages, pages retenues parmis un wikipedia search. La 2e liste contient les disambiguations supplementaires, au besoin
      fpag = []
      fpag2 = []
      filelog.write('\n'+str(ntry)+'\n')
      if ntry == 1:
        for pag in search(nam,results=1000):
          if pag[:len(nam)+1] == nam+' ' and pag[len(nam)+1].isupper():
            fpag.append(pag)
      if ntry == 2:
        fpag.append(''.join(search(nam,results=1000)))
#Analyse des pages retenues
      for pag in fpag:
        tpag = ''
        heocc = 0
        hisocc = 0
        sheocc = 0
        herocc = 0
        if ntry == 1:
          filelog.write(pag)
#Evite les erreurs si la page n'existe pas ou en est une de dismabiguation
          try:
#La ligne ci-dessous est le bottleneck du code car elle depend de ta connexion internet
            tpag = summary(pag).lower()
            filelog.write('\n')
          except wikipedia.exceptions.DisambiguationError as e:
            filelog.write(' - DISAMBIGUATION\n')
            fpag2.append([])
            for dpag in e.options:
              if ((dpag[:len(nam)+1] == nam+' ' and dpag[len(nam)+1].isupper() and ntry == 1) or (dpag[-len(nam)-1:] == ' '+nam or ' '+nam+' (' in dpag)) and not dpag in fpag and len(fpag2[-1])<20:
                fpag2[-1].append(dpag)
            if len(fpag2[-1]) == 0:
              fpag2.pop()
            elif fpag2[-1][0] not in fpag:
              fpag.insert(fpag.index(pag)+1,fpag2[-1].pop(0))
          except wikipedia.exceptions.PageError as p:
            pass
          except wikipedia.exceptions.WikipediaException as w:
            pass
        elif ntry == 2:
          tpag = pag.lower()
#Compte les occurence de 'he', 'his', 'she' et 'her' (ou variantes) pour identifier le genre de la page
        if len(tpag) != 0:
          tpag = tpag.replace('\n',' ')
          tpag = tpag.replace('(',' ')
          tpag = tpag.replace(')',' ')
          tpag = tpag.replace(",",' ')
          tpag = tpag.replace(".",' ')
          tpag = tpag.replace("'",' ')
          if ntry == 1:
            heocc = tpag.count(' he ')
            sheocc = tpag.count(' she ')
            hisocc = tpag.count(' his ')
            herocc = tpag.count(' her ')
            filelog.write('he='+str(heocc)+' his='+str(hisocc)+' she='+str(sheocc)+' her='+str(herocc)+'\n')
          elif ntry == 2:
            heocc = tpag.count(' men ')
            hisocc = tpag.count(' male ')
            sheocc = tpag.count(' women ')
            herocc = tpag.count(' female ')
            filelog.write('men='+str(heocc)+' male='+str(hisocc)+' women='+str(sheocc)+' female='+str(herocc)+'\n')
          if heocc+hisocc >= 3*(sheocc+herocc) and heocc+hisocc > 0:
            genh += 1
          elif sheocc+herocc >= 3*(heocc+hisocc) and sheocc+herocc > 0:
            genf += 1
#Debug: Pour voir la progression d'une entree
#        print(genh, genf, fpag.index(pag), len(fpag)-1)
#Rajout d'un element de fpag2 si on a pas assez de donnees
        if (fpag.index(pag) == len(fpag)-1) and (len(fpag2) > 0):
          if len(fpag2[0]) > 0:
            if fpag2[0][0] not in fpag:
              fpag.append(fpag2[0].pop(0))
          if len(fpag2[0]) > 0:
            fpag2.append(fpag2[0])
          if len(fpag2) == 1 and len(fpag2[0]) == 0:
            fpag2 = []
          else:
            fpag2 = fpag2[1:]
        if genh + genf >= 20:
          break
#Unisexe si moins du 2/3 des occurences sont identifiees au meme genre
      if genh >= 3*genf and genh > 0:
        gender = 'M'
      if genf >= 3*genh and genf > 0:
        gender = 'F'
      if (gender == 'UNK' and (genh != 0 or genf != 0)):
        gender = 'UNI'
      if ntry <= 2:
        filelog.write(name+' = %iH %iF\n'%(genh,genf))
      filelog.write(name+' = '+gender)
  filelog.write('\n\n')
  print(ntrack,'sur',len(names))
