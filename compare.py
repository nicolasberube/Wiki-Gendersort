# -*- coding: utf-8 -*-
"""
@author: Nicolas Berube, 2016-2020
for Vincent Larivière, EBSI, University of Montreal

Library to compare the Wiki-Gendersort dataset to other datasets
This code is associated to the paper
Wiki-Gendersort: Automatic gender detection using first names in Wikipedia
https://osf.io/preprints/socarxiv/ezw7p/

The 4 process_ functions create the outfile for the gendersort class
based on the specific datasets raw files.

"""

from pathlib import Path
from Wiki_Gendersort import wiki_gendersort, nameclean
from tqdm import tqdm
from time import sleep
# from collections import Counter


def process_genderc():
    print('Processing GenderC')
    cwd = Path(__file__).parent.absolute()
    raw_file_path = cwd / 'data_compare' / 'raw' / 'nam_dict.txt'
    out_path = cwd / 'data_compare' / 'GendercOut.txt'
    print('Importing file ' + raw_file_path.name)
    namdata = {}
    with open(raw_file_path, 'r', encoding='iso-8859-1') as raw_file:
        rec = 0
        for lin in raw_file.readlines():
            if rec > 0 and rec < 3:
                rec += 1
            if 'begin of name list' in lin:
                rec = 1
            if rec == 3:
                dat = lin[:lin.index('    ')]
                gend = dat[:3]
                nam = dat[3:]
                if ('M' in gend) and not ('F' in gend):
                    gen = 'M'
                elif ('F' in gend) and not ('M' in gend):
                    gen = 'F'
                elif ('=' in gend):
                    gen = 'UNI'
                else:
                    gen = 'UNK'
                if nam in namdata:
                    gs = namdata[nam]
                    if ((gs == 'M' and gen == 'F') or
                            (gs == 'F' and gen == 'M') or
                            (gen == 'UNI')):
                        namdata[nam] = 'UNI'
                    if (gs == 'UNK' and gen == 'M'):
                        namdata[nam] = 'M'
                    if (gs == 'UNK' and gen == 'F'):
                        namdata[nam] = 'F'
                else:
                    namdata[nam] = gen

    print('Saving out file in ' + out_path.name)
    with open(out_path, 'w', encoding='utf-8') as fileout:
        fileout.write('\n'.join([k + '\t' + v
                                 for k, v in namdata.items()]))
    print('Done')


def process_uscensus():
    print('Processing US Census')
    cwd = Path(__file__).parent.absolute()
    M_raw_file_path = cwd / 'data_compare' / 'raw' / 'Census Male names.txt'
    F_raw_file_path = cwd / 'data_compare' / 'raw' / 'Census Female names.txt'
    out_path = cwd / 'data_compare' / 'USCensusOut.txt'
    print('Importing file ' + M_raw_file_path.name)
    M_occdata = {}
    namdata = {}
    with open(M_raw_file_path, 'r') as raw_file:
        for lin in raw_file.readlines():
            ls = lin.split()
            nam = ls[0]
            occ = float(ls[1])
            if nam in M_occdata:
                M_occdata[nam] += occ
            M_occdata[nam] = occ
            namdata[nam] = 'M'

    print('Importing file ' + F_raw_file_path.name)
    with open(F_raw_file_path, 'r') as raw_file:
        for lin in raw_file.readlines():
            ls = lin.split()
            nam = ls[0]
            occ = float(ls[1])
            if occ > 0.01:
                if nam in M_occdata:
                    if occ >= 3*M_occdata[nam]:
                        namdata[nam] = 'F'
                    elif occ >= 3*M_occdata[nam]:
                        namdata[nam] = 'UNI'
                else:
                    namdata[nam] = 'F'

    print('Saving out file in ' + out_path.name)
    with open(out_path, 'w', encoding='utf-8') as fileout:
        fileout.write('\n'.join([k + '\t' + v
                                 for k, v in namdata.items()]))
    print('Done')


def process_genderchecker():
    print('Processing GenderChecker')
    cwd = Path(__file__).parent.absolute()
    raw_file_path = (cwd / 'data_compare' / 'raw' /
                     'GenderChecker Database Feb2020.csv')
    out_path = cwd / 'data_compare' / 'GenderCheckerOut.txt'
    print('Importing file ' + raw_file_path.name)
    namdata = {}
    with open(raw_file_path, 'r', encoding='iso-8859-1') as raw_file:
        raw_file.readline()
        for lin in raw_file.readlines():
            ls = lin.split(',')
            nam = ','.join(ls[0:-1])
            gender = ls[-1]
            gen = 'UNK'
            if 'female' in gender.lower():
                gen = 'F'
            elif 'male' in gender.lower():
                gen = 'M'
            elif 'unisex' in gender.lower():
                gen = 'UNI'
            if nam in namdata:
                gs = namdata[nam]
                if ((gs == 'M' and gen == 'F') or
                        (gs == 'F' and gen == 'M') or
                        (gen == 'UNI')):
                    namdata[nam] = 'UNI'
                if (gs == 'UNK' and gen == 'M'):
                    namdata[nam] = 'M'
                if (gs == 'UNK' and gen == 'F'):
                    namdata[nam] = 'F'
            else:
                namdata[nam] = gen

    print('Saving out file in ' + out_path.name)
    with open(out_path, 'w', encoding='utf-8') as fileout:
        fileout.write('\n'.join([k + '\t' + v
                                 for k, v in namdata.items()]))
    print('Done')


def process_namsor():
    print('Processing NamSor')
    cwd = Path(__file__).parent.absolute()
    raw_file_path = cwd / 'data_compare' / 'raw' / 'Namsor_1M.txt'
    out_path = cwd / 'data_compare' / 'NamsorOut.txt'
    print('Importing file ' + raw_file_path.name)
    namcount = {}
    with open(raw_file_path, 'r') as raw_file:
        raw_file.readline()
        for lin in tqdm(raw_file.readlines(), total=1000000):
            ls = lin.replace('\n', '').split('\t')
            nam = nameclean(nameclean(ls[0], wos_flag=True)[0])[0]
            gender = ls[-1]
            if gender == 'male':
                gend = 0
            elif gender == 'female':
                gend = 1
            elif gender == 'unknown':
                gend = 2
            else:
                print('genre introuvable: '+gend)
            if nam not in namcount:
                namcount[nam] = [0, 0, 0]
            namcount[nam][gend] += 1

    namdata = {}
    for nam, count in namcount.items():
        if count[0] > 3*count[1]:
            gen = 'M'
        elif count[1] > 3*count[0]:
            gen = 'F'
        elif count[0] == 0 and count[1] == 0:
            gen = 'UNK'
        else:
            gen = 'UNI'
        namdata[nam] = gen

    print('Saving out file in ' + out_path.name)
    with open(out_path, 'w', encoding='utf-8') as fileout:
        fileout.write('\n'.join([k + '\t' + v
                                 for k, v in namdata.items()]))
    print('Done')


def table_compare(sort_path,
                  names_path=None):
    """Compare a names sorting dataset to the wiki-gendersort dataset.

    This function prints the comparison results in the console

    Parameters
    ----------
    sort_path: str or Path
        Path to the Out.txt file of the dataset

    names_path: str or Path, optional
        Path to the list of names to compare to.
        Default is "./Names.txt"
    """
    if names_path is None:
        cwd = Path(__file__).parent.absolute()
        names_path = cwd / 'Names.txt'

    sort_path = cwd / 'data_compare' / 'USCensusOut.txt'
    sort_path = Path(sort_path)
    WG = wiki_gendersort()
    CS = wiki_gendersort(sort_path)
    with open(cwd / 'Names.txt') as name_file:
        names = name_file.read().split('\n')

    gender_dict = {'M': 0,
                   'F': 1,
                   'UNI': 2,
                   'UNK': 3,
                   'INI': 4}
    table = [[0]*5 for _ in range(5)]
    for name in tqdm(names):
        table[gender_dict[WG.assign(name)]][gender_dict[CS.assign(name)]] += 1


#Processing WOS authorship and Names lists
#Need to incorporate first name authorship proportions


print('Importing WOS authorship')
cwd = Path().parent.absolute()
raw_names_ppm = {}
with open(cwd / 'data_compare' / 'raw' / 'WOS_authors.txt') as file:
    for lin in tqdm(file.read().split('\n')):
        ls = lin.replace('\ufeff', '').split('\t')
        if len(ls) == 3:
            name = ls[0]
            occ = float(ls[-1])
            if name not in raw_names_ppm:
                raw_names_ppm[name] = 0.
            raw_names_ppm[name] += occ

print('Cleaning and saving WOS names')
sleep(0.5)
names_ppm = {}
for name, ppm in tqdm(raw_names_ppm.items()):
    for n in nameclean(name):
        if n not in names_ppm:
            names_ppm[n] = 0.
        names_ppm[n] += ppm

names = sorted(list(names_ppm))
with open(cwd / 'WOS_Names.txt', 'w') as file:
    file.write('\n'.join(names))

print('Analyzing names not in WOS')
raw_new_names = []
all_paths = [cwd / 'data_compare' / 'raw' / 'NamesOut_2017.txt',
             cwd / 'data_compare' / 'GendercOut.txt',
             cwd / 'data_compare' / 'GenderCheckerOut.txt',
             cwd / 'data_compare' / 'NamsorOut.txt',
             cwd / 'data_compare' / 'USCensusOut.txt']
for path in all_paths:
    print(f'Importing names from {path.name}')
    sleep(0.5)
    with open(path) as file:
        data = file.read().split('\n')
    for d in tqdm(data):
        name = '\t'.join(d.split('\t')[:-1])
        raw_new_names += nameclean(name)

print('Saving names not in WOS')
sleep(0.5)
new_names = []
for name in tqdm(set(raw_new_names)):
    if name not in names_ppm:
        new_names.append(name)
with open(cwd / 'New_Names.txt', 'w') as file:
    file.write('\n'.join(sorted(list(new_names))))
with open(cwd / 'Names.txt', 'w') as file:
    file.write('\n'.join(sorted(list(new_names)+list(names))))
print('Done')


if __name__ == '__main__':
    # process_genderc()
    # process_uscensus()
    # process_genderchecker()
    # process_namsor()

    cwd = Path(__file__).parent.absolute()
    #table_compare(cwd / 'data_compare' / 'GendercOut.txt')
    #GC = wiki_gendersort(cwd / 'data_compare' / 'GenderCheckerOut.txt')
    #US = wiki_gendersort(cwd / 'data_compare' / 'USCensusOut.txt')
    #NS = wiki_gendersort(cwd / 'data_compare' / 'NamsorOut.txt')
    # table_compare(cwd / 'data_compare' / 'USCensusOut.txt')


