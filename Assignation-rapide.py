#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ce code prend une liste de prénoms séparés par un retour à la ligne \n dans un fichier .txt et attribue un genre à chacun d'entre eux à partir d'une base de donnée existante (NameKeyOut.txt).
Il retourne le tout dans un fichier output  .txt avec les prénoms suivi d'un tab \t, du genre attribué (M, F, UNI, INI ou UNK), chaque donnée étant séparée par un retour à la ligne \n.
Il retourne également une liste des prénoms séparés par un retour à la ligne \n qui n'ont pas été trouvés dans la base de donnée (et donc attribué UNK par défaut)

Ces nouveaux noms peuvent être ajoutés à la liste input (NameKey.txt) du code Assignation_update.py pour ensuite updater la base de données

Code realise par Nicolas Berube - juin 2017 - Universite de Montreal - groupe de Vincent Lariviere
"""

from os.path import isfile
from unidecode import unidecode
from bisect import bisect_left

#Base de données de correspondance prenom-genre
filepathclef = '/Users/berube/Desktop/postdoc/AssignationGenre/NameKeyOut.txt'
#liste des prenoms a attribuer un genre, séparés par un retour à la ligne
filepathi = '/Users/berube/Desktop/postdoc/Vincent-Genres/NSERC_data_fil.txt'
#Destination du fichier output des prenoms avec le genre attribué
filepatho = '/Users/berube/Desktop/postdoc/Vincent-Genres/NSERC_data_fil_gen.txt'
#ODestination output des prenoms non presents dans la base de donnée de correspondance, pour utilisation future à ajouter au input (NameKey.txt) du code Assignation_update.py
filepathnew = '/Users/berube/Desktop/postdoc/Vincent-Genres/NSERC_data_fil_new.txt'

def index(a, x):
    'Locate the leftmost value exactly equal to x in a list'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return(i)
    else:
        return(-1)

def file_len(fname,encod):
    'Retourne le nombre de ligne dans un fichier'
    with open(fname,encoding=encod) as f:
        for i, l in enumerate(f):
            pass
    return(i+1)

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
    
def namecleanWoSall(prenom):
    'Prend un prenom et retourne une liste des strings a analyser dans l\'ordre pour attribuer le genre avec WiGen. À utiliser pour les noms du WoS.'
    name = prenom
#Met les mots parentheses en derniere priorite et les mots entre guillemets en avant derniere priorite dans le filtre
    while ('(' in name) and (')' in name) or ('"' in name and name.find('"') != name.rfind('"')):
        if name.find('(') < name.rfind(')') and ('(' in name) and (')' in name):
            name = name[:name.find('(')] + ' ' + name[name.rfind(')')+1:] + ' ' + name[name.find('(')+1:name.rfind(')')]
        elif ('"' in name and name.find('"') != name.rfind('"')):
            name = name[:name.find('"')] + ' ' + name[name.rfind('"')+1:] + ' ' + name[name.find('"')+1:name.rfind('"')]
        else:
            break        
#Clean les sequences de la liste: Enleve les string sans lettre, separe les string fusionnees et enleve les points a la fin tout en les depriorisant
    namf = name.replace('-',' ').replace('_',' ').split()
    j = 0
    while j < len(namf):
        if countalpha(namf[j]) == 0:
            del namf[j]
            j -= 1
        j += 1
    j = 0
    while j < len(namf):
        if len(namf[j]) >= 4:
            if namf[j][-1] == '.' and namf[j][-2].isupper() and namf[j][-3].islower():
                namf.insert(j+1,namf[j][-2:])
                namf[j] = namf[j][:-2]
        if namf[j][-1] == '.' and len(namf[j]) > 1:
            namf.append(namf[j][:-1])
            del namf[j]
            j -= 1
        j += 1
#Prend les sequences qui ne sont pas une initiale (si 1 lettre ou aucune voyelle)
    namf2 = []
    for nam in namf:
        if countalpha(nam) > 1 and countvowel(nam) > 0:
            if len(nam) <= 1:
                namf2.append(nam.upper())
            else:
                namf2.append(nam[0].upper()+nam[1:].lower())
    return(namf2)

def nameclean(prenom):
    'Prend un prenom et retourne une liste des strings a analyser dans l\'ordre pour attribuer le genre avec WiGen. À utiliser pour un nom normal.'
    name = prenom
#Met les mots parentheses en derniere priorite et les mots entre guillemets en avant derniere priorite dans le filtre
    while ('(' in name) and (')' in name) or ('"' in name and name.find('"') != name.rfind('"')):
        if name.find('(') < name.rfind(')') and ('(' in name) and (')' in name):
            name = name[:name.find('(')] + ' ' + name[name.rfind(')')+1:] + ' ' + name[name.find('(')+1:name.rfind(')')]
        elif ('"' in name and name.find('"') != name.rfind('"')):
            name = name[:name.find('"')] + ' ' + name[name.rfind('"')+1:] + ' ' + name[name.find('"')+1:name.rfind('"')]
        else:
            break        
#Clean les sequences de la liste: Enleve les string sans lettre, separe les string fusionnees et enleve les points a la fin tout en les depriorisant (AliM. -> Ali M)
    namf = ''
    for i in name:
        if countalpha(i) == 1 or i == '.':
            namf += i
        else:
            namf += ' '       
    namf = namf.split()
    
    j = 0
    while j < len(namf):
        if countalpha(namf[j]) == 0:
            del namf[j]
            j -= 1
        j += 1
        
    j = 0
    while j < len(namf):
        if len(namf[j]) >= 4:
            if namf[j][-1] == '.' and namf[j][-2].isupper() and namf[j][-3].islower():
                namf.insert(j+1,namf[j][-2:])
                namf[j] = namf[j][:-2]
        if namf[j][-1] == '.' and len(namf[j]) > 1:
            namf.append(namf[j][:-1])
            del namf[j]
            j -= 1
        j += 1

#Resplit les points (A.Carl -> A Carl)    
    j = 0
    while j < len(namf):
        namsplit = namf[j].split('.')
        if len(namsplit) > 1:
            del namf[j]
            for k in range(len(namsplit)):
                namf.insert(j+k,namsplit[k])
            j += len(namsplit)-1
        j += 1
        
#Prend les sequences qui ne sont pas une initiale (si 1 lettre ou aucune voyelle)
    namf2 = []
    for nam in namf:
        if countalpha(nam) > 1 and countvowel(nam) > 0:
            if len(nam) <= 1:
                namf2.append(nam.upper())
            else:
                namf2.append(nam[0].upper()+nam[1:].lower())
    return(namf2)

#Lecture de la base de données de correspondance Prenom/Genres. Cette base de données est situee a dans le fichier au path 'filepathclef'
#Cette base de données est sous la forme de deux listes ordonnees: nameswg = liste des prenoms, gendswg = liste des genres associés aux prenoms de nameswg
print('Importation de la table des prenoms')
nameswg = []
gendswg = []
i = 0
ncount = 1
imax = file_len(filepathclef,'utf-8')
print(imax, 'noms dans le fichier',filepathclef)
filewg = open(filepathclef,'r',encoding='utf-8')
for line in filewg.readlines():
    #Progress bar
    i += 1
    if i > ncount*(imax/20):
        print('%i%%'%(ncount*5))
        ncount += 1
    ls = line.replace('\n','').split('\t')
    if i != 0:
        name = ls[0].upper()
        gend = ls[1]
        bind = bisect_left(nameswg,name)
        if bind == len(nameswg):
            nameswg.append(name)
            gendswg.append(gend)
        else:
            if nameswg[bind] != name:
                nameswg.insert(bind,name)
                gendswg.insert(bind,gend)
filewg.close()

#Lecture du fichier input et attribution du genre. Impression des resultats dans outfile et newfile
print('Commencement de l\'attribution')
i = 0
imax = file_len(filepathi,'utf-8')
ncount = 1
print(imax, 'noms dans le fichier',filepathi)
if isfile(filepathi):
    infile = open(filepathi,'r',encoding='utf-8')
    outfile = open(filepatho,'w',encoding='utf-8')
    newfile = open(filepathnew,'w',encoding='utf-8')
    newnames = []
    for line in infile.readlines():
        #Progress bar
        i += 1
        if i > ncount*(imax/100):
            print('%i%%'%ncount)
            ncount += 1
        #Ecriture du output
        prenom = line.replace('\n','')
        namelist = nameclean(prenom)
        gend = 'NULL'
        if len(namelist) == 0:
            gend = 'INI'
        j = 0
        while (gend == 'UNK' or gend == 'NULL') and j < len(namelist):
            ind = index(nameswg,namelist[j].upper())
            if ind == -1:
                ind = index(nameswg,unidecode(namelist[j].upper()))
            if ind == -1:
                newname = namelist[j][0].upper()+namelist[j][1:].lower()
                nind = bisect_left(newnames,newname)
                if nind == len(newnames) or newnames[nind] != newname:
                    newnames.insert(nind,newname)
                if namelist[j].upper() != unidecode(namelist[j].upper()):
                    newname = unidecode(namelist[j].upper())[0]+unidecode(namelist[j].upper())[1:].lower()
                    nind = bisect_left(newnames,newname)
                    if nind == len(newnames) or newnames[nind] != newname:
                        newnames.insert(nind,newname)
            else:
                gend = gendswg[ind]        
            j += 1
        if prenom.upper() == 'NULL' or len(prenom) == 0:
            gend = 'UNK'
        outfile.write(line.replace('\n','')+'\t'+gend+'\n')
    newfile.write('\n'.join(newnames))
    infile.close()
    outfile.close()
    newfile.close()
else:
    print('Fichier introuvable')
