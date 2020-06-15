#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Nicolas Berube, 2016-2020
for Vincent Larivière, EBSI, University of Montreal

Library to build the Wiki-Gendersort dataset, and to use it.
This code is associated to the paper
Wiki-Gendersort: Automatic gender detection using first names in Wikipedia
https://osf.io/preprints/socarxiv/ezw7p/

Use build_dataset() to build the dataset from scratch with Wikiedia searches.
This should already been done on our own first name database and available
in NamesOut.txt

Use wiki_gendersort() class to assign a gender based on the built dataset.
    WG = wiki_gendersort()
    WG.assign('Nicolas')
    WG.file_assign('test_file.txt')
"""

from os.path import isfile
from os import remove
from shutil import copyfile
from wikipedia import search, summary
from datetime import datetime
# from math import floor
import wikipedia
import json
# import sys
import string
from bisect import bisect_left
from unidecode import unidecode
from pathlib import Path
from multiprocessing import Pool
from tqdm import tqdm


def index(a, x):
    """Locate the leftmost value exactly equal to x in an ordered list

    Parameters
    ----------
    a: list
    Ordered list of elements

    x: element
    The element to find in the list a

    Returns
    -------
    int
    The index of the element in the ordered list. Returns -1 if the element
    is not found.
    """
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return(i)
    else:
        return(-1)


def file_len(fname, encod):
    "Returns the number of lines in a files"
    with open(fname, encoding=encod) as f:
        for i, l in enumerate(f):
            pass
    return(i+1)


def countalpha(name):
    "Counts the number of alphabetical characters in a string"
    i = 0
    chars = string.ascii_lowercase + string.ascii_uppercase
    for c in name:
        if unidecode(c) in chars:
            i += 1
    return(i)


def countvowel(name):
    "Counts the number of vowels in a string"
    i = 0
    for c in name:
        if unidecode(c) in 'aeiouyAEIOUY':
            i += 1
    return(i)


def lectdatalog(cwd, backup=True):
    "Cleans and imports data from log file"
    # Cleans log
    datalog = []
    datanames = []

    log_path = cwd / 'NamesLog.txt'
    if isfile(log_path):
        # Back-up of current log file
        nbulog = 1
        bu_name = log_path.stem + '_bu%i' % nbulog + log_path.suffix
        while isfile(cwd / bu_name):
            nbulog += 1
            bu_name = log_path.stem + '_bu%i' % nbulog + log_path.suffix
        copyfile(log_path, cwd / bu_name)
        if backup:
            print('Copying ' + log_path.name + ' into ' + bu_name)

        print('Importing ' + log_path.stem)
        with open(log_path) as f:
            datalogtemp = f.read()
        datalogtemp = datalogtemp.split('\n\n')
        for d in datalogtemp:
            if len(d) != 0:
                ds = d.split('\n')
                if len(ds) >= 2:
                    name = ds[0]
                    gend = ds[-1].replace(' ', '').split('=')[-1]
                    try:
                        time = datetime.strptime(ds[-2],
                                                 '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        time = datetime.strptime(ds[-2],
                                                 '%Y-%m-%d %H:%M:%S')
                    name_idx = bisect_left(datanames, name)
                    if (name_idx != len(datanames) and
                            datanames[name_idx] == name):
                        if datalog[name_idx][2] < time:
                            datalog[name_idx] = [name, gend, time, d]
                    else:
                        datanames.insert(name_idx, name)
                        datalog.insert(name_idx, [name, gend, time, d])
        if not backup:
            remove(bu_name)

    return datalog, datanames


def name_to_gender(name):
    "Assigns gender to a first name based on a wikipedia search"

    log_data = name
    gender = 'UNK'
    if len(name) == 0 or len(name.split()) == 0 or name.upper() == 'NULL':
        gender = 'INI'
        log_data += '\nname is empty\n'
        log_data += str(datetime.now()) + '\n'
        log_data += name + ' = ' + gender
        return gender, log_data

    elif countalpha(name) <= 1 or countvowel(name) == 0:
        gender = 'INI'
        log_data += '\nname is initials\n'
        log_data += str(datetime.now()) + '\n'
        log_data += name + ' = ' + gender
        return gender, log_data

    # genh: # of pages refering to a man. genf: woman.
    genh = 0
    genf = 0
    # Only the first part of the name and puts proper uppercase/lowercase
    namesplit = name.replace('-', ' ').split()
    if len(namesplit[0]) == 1:
        nam = namesplit[0].upper()
    else:
        nam = namesplit[0][0].upper() + namesplit[0][1:].lower()
    # Search parameters if previous search was inconclusive
    # 0: Presenc of a page FIRST_NAME (given name)
    # 1: FIRST_NAME LAST_NAME
    # 2: Analysis of page listing (not their content)
    # 3: LAST_NAME FIRST_NAME
    ntry = 0
    while ntry <= 1 and gender == 'UNK':
        ntry += 1
    # filtered pages, which are the ones kept from the wikipedia search.
    # The second list contains added disambiguations, if needed
        fpag = []
        fpag2 = []
        log_data += '\n'+str(ntry)+'\n'
        try:
            if ntry == 1:
                for pag in search(nam, results=1000):
                    if (pag[:len(nam)+1] == nam+' ' and
                            pag[len(nam)+1].isupper()):
                        fpag.append(pag)
            if ntry == 2:
                fpag.append(''.join(search(nam, results=1000)))
        except wikipedia.exceptions.WikipediaException:
            pass
        except json.decoder.JSONDecodeError:
            pass
    # Pages analysis
        for pag in fpag:
            tpag = ''
            heocc = 0
            hisocc = 0
            sheocc = 0
            herocc = 0
            if ntry == 1:
                log_data += pag
                # If page does not exist of is a disambiguation
                try:
                    # The following line if the true code bottleneck
                    tpag = summary(pag).lower()
                    log_data += '\n'
                except wikipedia.exceptions.DisambiguationError as e:
                    log_data += ' - DISAMBIGUATION\n'
                    fpag2.append([])
                    for dpag in e.options:
                        if (((dpag[:len(nam)+1] == nam+' ' and
                              dpag[len(nam)+1].isupper() and
                              ntry == 1) or
                             (dpag[-len(nam)-1:] == ' '+nam or
                              ' '+nam+' (' in dpag)) and
                                dpag not in fpag and
                                len(fpag2[-1]) < 20):
                            fpag2[-1].append(dpag)
                    if len(fpag2[-1]) == 0:
                        fpag2.pop()
                    elif fpag2[-1][0] not in fpag:
                        fpag.insert(fpag.index(pag)+1, fpag2[-1].pop(0))
                except wikipedia.exceptions.PageError:
                    pass
                except wikipedia.exceptions.WikipediaException:
                    pass
                except json.decoder.JSONDecodeError:
                    pass
            elif ntry == 2:
                tpag = pag.lower()
            # Counts the number of 'he', 'his', 'she' and 'her'
            # (and variants) to identify the gender
            if len(tpag) != 0:
                tpag = tpag.replace('\n', ' ')
                tpag = tpag.replace('(', ' ')
                tpag = tpag.replace(')', ' ')
                tpag = tpag.replace(",", ' ')
                tpag = tpag.replace(".", ' ')
                tpag = tpag.replace("'", ' ')
                if ntry == 1:
                    heocc = tpag.count(' he ')
                    sheocc = tpag.count(' she ')
                    hisocc = tpag.count(' his ')
                    herocc = tpag.count(' her ')
                    log_data += ('he='+str(heocc) +
                                 ' his='+str(hisocc) +
                                 ' she='+str(sheocc) +
                                 ' her='+str(herocc) +
                                 '\n')
                elif ntry == 2:
                    heocc = tpag.count(' men ')
                    hisocc = tpag.count(' male ')
                    sheocc = tpag.count(' women ')
                    herocc = tpag.count(' female ')
                    log_data += ('men='+str(heocc) +
                                 ' male='+str(hisocc) +
                                 ' women='+str(sheocc) +
                                 ' female='+str(herocc) +
                                 '\n')
                if heocc+hisocc >= 3*(sheocc+herocc) and heocc+hisocc > 0:
                    genh += 1
                elif (sheocc+herocc >= 3*(heocc+hisocc) and
                      sheocc+herocc > 0):
                    genf += 1
            # Adding an element of fpag2 if we don't have enough data
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
            # Unisex if less than 3/4 of occurences are of the same gender
        if genh >= 3*genf and genh > 0:
            gender = 'M'
        if genf >= 3*genh and genf > 0:
            gender = 'F'
        if (gender == 'UNK' and (genh != 0 or genf != 0)):
            gender = 'UNI'
        if ntry <= 2:
            log_data += name + ' = %iH %iF\n' % (genh, genf)
        log_data += str(datetime.now()) + '\n'
        log_data += name + ' = ' + gender

    return gender, log_data


def build_dataset(reboot=False):
    """Builds the database of gender based on Wikipedia search.

    This code takes a list of first names separated by a line break \n
    in file Names.txt and constructs a database in NamesOut.txt by assigning
    them a gender.

    NamesOut.txt will contain the same names, but followed by the
    assigned gender (both of them being seprated by a tab \t).

    The gender attribution (M, F, UNI, INI or UNK) is done according to the
    occurrence of first names on Wikipedia pages concerning them.
    M: male
    F: female
    UNI: unisex
    INI: initials
    UNK: unknown

    If NamesOut.txt already exists, it will be ignored and overwritten.
    Information on gender assignment is present in the log file (NamesLog.txt).
    The log file is automatically detected to launch the code back where it was
    in the case it got interrupted.

    Set reboot=True if you want to disregard log files and start from scratch
    """

    cwd = Path(__file__).parent.absolute()
    inputnames = cwd / 'Names.txt'

    # namestot: List of str names to attribute a gender to
    namestot_raw = []
    with open(inputnames, 'r') as namefile:
        for n in namefile.readlines():
            name = n[:-1]
            if name:
                namestot_raw.append(name)

    print('Names sorting')
    namestot = sorted(namestot_raw)
    print('Log reading')
    datalog, datanames = lectdatalog(cwd)
    if not datanames or reboot:
        datanames = ['']
        datalog = [['',
                    'UNK',
                    datetime.now(),
                    '\nname is empty\n' + str(datetime.now()) + '\n = UNK']]

    print('Names treatment')
    # Keeping only names that are not in log file in namesfil
    namesfil = []

    for name in namestot:
        if index(datanames, name) == -1:
            namesfil.append(name)
    print('Fetching names data from Wikipedia')
    # tn = cpu_count()
    # Since the bottleneck is waiting for the wikipedia server to ping back,
    # n_pool should be as high as possible
    n_pool = 25
    with open(cwd / 'NamesLog.txt', 'w', encoding='utf-8') as filelog:
        filelog.write('\n\n'.join([d[3] for d in datalog]))
        with Pool(n_pool) as pool:
            with tqdm(total=len(namesfil)) as pbar:
                for gender, log_data in pool.imap_unordered(name_to_gender,
                                                            namesfil):
                    pbar.update()
                    print(gender)
                    print(log_data)
                    filelog.write('\n\n'+log_data)
                    print('DONE')

    print('Saving out file in NamesOut.txt')
    datalog, datanames = lectdatalog(cwd, backup=False)
    gender_data = {k[0]: k[1] for k in datalog}
    with open(cwd / 'NamesOut.txt', 'w', encoding='utf-8') as fileout:
        fileout.write('\n'.join([name + '\t' + gender_data[name]
                                 for name in namestot_raw]))
    print('Done')


def namecleanWoSall(prenom):
    """Cleans a first name string and separates it into a list of strings,
    ordered by priority, to analyze for Wiki-Gendersort.

    This is a special modification to use on specific names format in the
    Web of Science database. Normal names should use nameclean().
    """

    name = prenom
    # Takes words in quotations and parenthesis as a penultimate priority
    while (('(' in name) and (')' in name) or
           ('"' in name and name.find('"') != name.rfind('"'))):
        if (name.find('(') < name.rfind(')') and
                ('(' in name) and (')' in name)):
            name = (name[:name.find('(')] + ' ' +
                    name[name.rfind(')')+1:] + ' ' +
                    name[name.find('(')+1:name.rfind(')')])
        elif ('"' in name and name.find('"') != name.rfind('"')):
            name = (name[:name.find('"')] + ' ' +
                    name[name.rfind('"')+1:] + ' ' +
                    name[name.find('"')+1:name.rfind('"')])
        else:
            break
    # Cleans strings of the list: Gets rid of strings without letters,
    # separates fused strings and gets rid of periods at the end of strings
    # while making the latter last in priority
    namf = name.replace('-', ' ').replace('_', ' ').split()
    j = 0
    while j < len(namf):
        if countalpha(namf[j]) == 0:
            del namf[j]
            j -= 1
        j += 1
    j = 0
    while j < len(namf):
        if len(namf[j]) >= 4:
            if (namf[j][-1] == '.' and namf[j][-2].isupper() and
                    namf[j][-3].islower()):
                namf.insert(j+1, namf[j][-2:])
                namf[j] = namf[j][:-2]
        if namf[j][-1] == '.' and len(namf[j]) > 1:
            namf.append(namf[j][:-1])
            del namf[j]
            j -= 1
        j += 1

    # Takes the strings that are not initials (if 1 letter or no vowels)
    namf2 = []
    for nam in namf:
        if countalpha(nam) > 1 and countvowel(nam) > 0:
            if len(nam) <= 1:
                namf2.append(nam.upper())
            else:
                namf2.append(nam[0].upper()+nam[1:].lower())
    return(namf2)


def nameclean(prenom):
    """Cleans a first name string and separates it into a list of strings,
    ordered by priority, to analyze for Wiki-Gendersort.
    """

    name = prenom
    # Takes words in quotations and parenthesis as a penultimate priority
    while (('(' in name) and (')' in name) or
           ('"' in name and name.find('"') != name.rfind('"'))):
        if (name.find('(') < name.rfind(')') and
                ('(' in name) and (')' in name)):
            name = (name[:name.find('(')] + ' ' +
                    name[name.rfind(')')+1:] + ' ' +
                    name[name.find('(')+1:name.rfind(')')])
        elif ('"' in name and name.find('"') != name.rfind('"')):
            name = (name[:name.find('"')] + ' ' +
                    name[name.rfind('"')+1:] + ' ' +
                    name[name.find('"')+1:name.rfind('"')])
        else:
            break

    # Cleans strings of the list: Gets rid of strings without letters,
    # separates fused strings and gets rid of periods at the end of strings
    # while making the latter last in priority (AliM. -> Ali M)
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
            if (namf[j][-1] == '.' and namf[j][-2].isupper() and
                    namf[j][-3].islower()):
                namf.insert(j+1, namf[j][-2:])
                namf[j] = namf[j][:-2]
        if namf[j][-1] == '.' and len(namf[j]) > 1:
            namf.append(namf[j][:-1])
            del namf[j]
            j -= 1
        j += 1

    # Resplit the periods (A.Carl -> A Carl)
    j = 0
    while j < len(namf):
        namsplit = namf[j].split('.')
        if len(namsplit) > 1:
            del namf[j]
            for k in range(len(namsplit)):
                namf.insert(j+k, namsplit[k])
            j += len(namsplit)-1
        j += 1

    # Takes the strings that are not initials (if 1 letter or no vowels)
    namf2 = []
    for nam in namf:
        if countalpha(nam) > 1 and countvowel(nam) > 0:
            if len(nam) <= 1:
                namf2.append(nam.upper())
            else:
                namf2.append(nam[0].upper()+nam[1:].lower())
    return(namf2)


class wiki_gendersort():
    def __init__(self,
                 input_path=None):
        if input_path is None:
            cwd = Path(__file__).parent.absolute()
            self.input_path = cwd / 'NamesOut.txt'
        else:
            self.input_path = Path(input_path)

        print('Importing names database from ' + self.input_path.name)
        self.names_key = {}
        with open(self.input_path, 'r', encoding='utf-8') as filewg:
            for line in filewg.readlines():
                ls = line.replace('\n', '').split('\t')
                name = '\t'.join(ls[0:-1]).upper()
                gend = ls[-1]
                self.names_key[name] = gend

    def assign(self,
               name):
        "Assign a gender to a first name (string)"
        self.unknown_set = []
        namelist = nameclean(name)
        gend = 'NULL'
        if len(namelist) == 0:
            gend = 'INI'
        j = 0
        while (gend == 'UNK' or gend == 'NULL') and j < len(namelist):
            if namelist[j].upper() in self.names_key:
                gend = self.names_key[namelist[j].upper()]
            elif unidecode(namelist[j].upper()) in self.names_key:
                gend = self.names_key[unidecode(namelist[j].upper())]
            else:
                newname = namelist[j][0].upper() + namelist[j][1:].lower()
                self.unknown_set.append(newname)
                if namelist[j].upper() != unidecode(namelist[j].upper()):
                    newname = (unidecode(namelist[j].upper())[0] +
                               unidecode(namelist[j].upper())[1:].lower())
                    self.unknown_set.append(newname)
            j += 1
        if name.upper() == 'NULL' or len(name) == 0:
            gend = 'UNK'

        return gend

    def file_assign(self,
                    input_path,
                    output_path=None,
                    unknown_path=None):
        """Assigns a gender to a list of first names in a file.

        Parameters
        ----------
        input_path: str
            path to the file containing names to assign a gender.
            The names should be separated by a line break in a .txt file
            encoded in utf-8.

        output_path: str, optional
            path to the file containing the genders of the names.
            Each entry will be separated by a line break \n, and the gender
            will be separated from the name by a tab \t, encoded in utf-8.

            If None, the path will be input_path+'_genders.txt'.
            Default is None.

        unknown_path: str, optional
            path to the file containing names that were not in the database
            and were attributed 'UNK' by default.
            Each entry will be separated by a line break \n. Those names
            could be added to Names.txt, and then the database can be updated
            by running build_dataset(), assuming you still have the log files.
            Alternatively, the unknown names could be manually assigned to a
            gender with name_to_gender().

            If None, the path will be input_path+'_unknown.txt'.
            Default is None.
        """
        input_path = Path(input_path).absolute()
        print('Assigning gender to the names in file ' + input_path.name)
        if output_path is None:
            output_path = input_path.parent / (input_path.stem+'_output.txt')
        if unknown_path is None:
            unknown_path = input_path.parent / (input_path.stem+'_unknown.txt')
        infile = open(input_path, 'r', encoding='utf-8')
        outfile = open(output_path, 'w', encoding='utf-8')
        newnames = []
        for line in infile.readlines():
            name = line.replace('\n', '')
            gend = self.assign(name)
            for newname in self.unknown_set:
                nind = bisect_left(newnames, newname)
                if nind == len(newnames) or newnames[nind] != newname:
                    newnames.insert(nind, newname)
            outfile.write(line.replace('\n', '') + '\t' + gend + '\n')
        infile.close()
        outfile.close()
        print('Genders assigned in file ' + output_path.name)
        if len(newnames) != 0:
            with open(unknown_path, 'w', encoding='utf-8') as newfile:
                newfile.write('\n'.join(newnames))
            print('%i unknown names identified in file ' % len(newnames) +
                  unknown_path.name)
            print('Consider adding those names to Names.txt and ' +
                  'running build_dataset()')


if __name__ == '__main__':
    # build_dataset()

    # WG = wiki_gendersort()
    # WG.assign('Nicolas')
    # WG.file_assign('test_file.txt')
    pass
