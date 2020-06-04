#!/bin/bash
#Ce code lance $2 calculs WiGen.py $1 dans des screens (voir commande screen)
#/Users/berube/Desktop/postdoc/AssignationGenre/Assignation-reboot_part1.sh NameKey.txt 25

if [ -z "$1" ]
then
 echo Indiquez le fichier input ~[]. Exemple: input.txt
 read INPUT
else
 INPUT=$1
fi
if [ -z "$2" ]
then
 echo Entrez le nombre de calculs paralleles a accomplir. Exemple: 5
 read TN
else
 TN=$2
fi

CN=1
while (($CN <= $TN)); do
 screen -S WiGen$CN -d -m python /Users/berube/Desktop/postdoc/AssignationGenre/Assignation-reboot_part1.py $INPUT $TN $CN
 let CN=CN+1
done

