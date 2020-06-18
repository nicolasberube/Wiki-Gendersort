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


def import_wos():
    """Imports dictionary of values with key=raw first name of the Web of
    Science database and value=ppm (sums to 1M) of authorship of that first
    name"""

    print('Importing WOS authorship')
    cwd = Path(__file__).parent.absolute()
    names_ppm = {}
    with open(cwd / 'data_compare' / 'raw' / 'WOS_authors.txt') as file:
        for lin in tqdm(file.read().split('\n')):
            ls = lin.replace('\ufeff', '').split('\t')
            if len(ls) == 3:
                name = ls[0]
                occ = float(ls[-1])
                if name not in names_ppm:
                    names_ppm[name] = 0.
                names_ppm[name] += occ
    return names_ppm


def process_names():
    """Generates Names.txt file with as many first names as possible
    from various raw data sources"""

    names_ppm = import_wos()

    print('Analyzing WOS names')
    all_names = []
    sleep(0.5)
    for name in tqdm(names_ppm):
        all_names += nameclean(name)

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
            all_names += nameclean(name)

    print('Saving names in Names.txt')
    with open(cwd / 'Names.txt', 'w') as file:
        file.write('\n'.join(sorted(list(set(all_names)))))
    print('Done')


def center_string(string, length):
    """Puts space before and after a string so it's centered
    in a specified length"""
    if length < len(string):
        return string[:length]
    n_add = length-len(string)
    return ' '*(n_add//2) + string + ' '*(n_add//2 + n_add % 2)


def table_compare(sort_path):
    """Compare a names sorting dataset to the wiki-gendersort dataset.

    This function prints the comparison results in the console

    Parameters
    ----------
    sort_path: str or Path
        Path to the Out.txt file of the dataset.
        Can also be a list of paths.
    """
    if not isinstance(sort_path, list):
        sort_path = [sort_path]
    sort_path = [Path(s) for s in sort_path]

    names_ppm = import_wos()

    WG = wiki_gendersort()
    compare_GSs = [wiki_gendersort(sp) for sp in sort_path]
    default_names = []
    compare_names = [[] for _ in range(len(compare_GSs))]

    print('Processing comparative data tables')
    gender_dict = {'M': 0,
                   'F': 1,
                   'UNI': 2,
                   'UNK': 3,
                   'INI': 4}
    tables = [[[0. for _ in range(len(gender_dict))]
               for _ in range(len(gender_dict))]
              for _ in range(len(compare_GSs))]
    sleep(0.5)
    for name, ppm in tqdm(names_ppm.items()):
        default_gender = gender_dict[WG.assign(name)]
        default_names.append(WG.matched_name)
        for i, GS in enumerate(compare_GSs):
            compare_gender = gender_dict[GS.assign(name)]
            compare_names[i].append(GS.matched_name)
            tables[i][compare_gender][default_gender] += ppm

    default_n_names = len(set(default_names))
    n_names = [len(set(names)) for names in compare_names]

    # Prints out results
    for i, GS in enumerate(compare_GSs):
        sort_name = sort_path[i].stem
        if sort_name[-3:].upper() == 'OUT':
            sort_name = sort_name[:-3]
        sort_name = sort_name[:13]
        col_ids = [center_string(g, 9)
                   for g, rank in sorted(gender_dict.items(),
                                         key=lambda x:x[1])]

        # Print cross-results table
        ini_ppm = tables[i][-1][-1]
        default_totals = [sum(tables[i][j][k]
                              for j in range(len(tables[i])-1))
                          for k in range(len(tables[i])-1)]
        compare_totals = [sum(tables[i][j][:-1])
                          for j in range(len(tables[i])-1)]
        print(' '*15 + '|' + center_string('Wiki-GenderSort',
                                           len(col_ids[:-1])*10-1) + '|')
        print(center_string(sort_name, 15) + '|' +
              '|'.join(col_ids[:-1]) + '|' +
              center_string('Total', 9) + '|')
        for j, col_id in enumerate(col_ids[:-1]):
            print(' '*6 + col_id + '|' +
                  '|'.join(' %5.2f %% ' % (100*ppm/(10**6-ini_ppm))
                           for ppm in tables[i][j][:-1]) + '|' +
                  ' %5.2f %% ' % (100*compare_totals[j]/(10**6-ini_ppm)) + '|')
        print(' '*6 + center_string('Total', 9) + '|' +
              '|'.join(' %5.2f %% ' % (100*ppm/(10**6-ini_ppm))
                       for ppm in default_totals) + '|' +
              '%6.2f %% ' % 100 + '|')
        print('Proportion of initials: %.2f %%' % (ini_ppm/10000))
        print()

        # Prints global data
        print('Wiki-GenderSort')
        print(' '*4 +
              'Identified authors : %.2f %%' %
              (100*sum(default_totals[:2])/sum(default_totals)))
        print(' '*4 +
              'Name tokens used for identification: %i (out of %i)' %
              (default_n_names, len([v for v in WG.names_key.values()
                                     if v not in {'INI', 'UNK'}])))
        print()
        print(center_string(sort_name, 15))
        print(' '*4 +
              'Identified authors : %.2f %%' %
              (100*sum(compare_totals[:2])/sum(compare_totals)))
        print(' '*4 +
              'Name tokens used for identification: %i (out of %i)' %
              (n_names[i], len([v for v in GS.names_key.values()
                                if v not in {'INI', 'UNK'}])))
        print()
        print()


def true_compare():
    """Compare the wiki-gendersort dataset with the true label
    dataset of "Comparison and benchmark of name-to-gender inference services"
    (https://peerj.com/articles/cs-156/)

    This function prints the results in the console
    """
    cwd = Path().parent.absolute()
    path = cwd / 'data_compare' / 'all.csv'
    namdata = []
    with open(path) as file:
        lin = file.readline()
        for lin in file.read().split('\n'):
            ls = lin[1:-1].split('","')
            if lin == '':
                continue
            nam = ls[0]
            gen = ls[4].upper()
            if gen in {'M', 'F'}:
                namdata.append([nam, gen])

    WG = wiki_gendersort()
    table = [[0, 0, 0], [0, 0, 0]]
    gender_dict = {'M': 0,
                   'F': 1,
                   'UNI': 2,
                   'UNK': 2,
                   'INI': 2}
    for name, gender in namdata:
        true_gender = gender_dict[gender]
        pred_gender = gender_dict[WG.assign(name)]
        table[true_gender][pred_gender] += 1

    col_ids = [center_string(g, 8) for g in [' M', ' F', ' UNK']]
    print(' '*15 + '|' + center_string('Wiki-GenderSort',
                                       len(col_ids)*9-1) + '|')
    print(center_string('True Label', 15) + '|' +
          '|'.join(col_ids) + '|')
    for j, col_id in enumerate(col_ids[:-1]):
        print(' '*7 + col_id + '|' +
              '|'.join('  %4i  ' % val
                       for val in table[j]) + '|')

    [[mm, mf, mu], [fm, ff, fu]] = table
    print()
    print('errorCoded = %.3f' % ((fm+mf+mu+fu)/(mm+fm+mf+ff+mu+fu)))
    print('errorCodedWithoutNA = %.3f' % ((fm+mf)/(mm+fm+mf+ff)))
    print('naCoded = %.3f' % ((mu+fu)/(mm+fm+mf+ff+mu+fu)))
    print('errorGenderBias = %.3f' % ((mf-fm)/(mm+fm+mf+ff)))
    print()
    print()


if __name__ == '__main__':
    pass
    # process_genderc()
    # process_uscensus()
    # process_genderchecker()
    # process_namsor()
    # process_names()

    cwd = Path(__file__).parent.absolute()
    sort_paths = [cwd / 'data_compare' / 'USCensusOut.txt',
                  cwd / 'data_compare' / 'GenderCheckerOut.txt',
                  cwd / 'data_compare' / 'NamsorOut.txt',
                  cwd / 'data_compare' / 'GendercOut.txt']
    table_compare(sort_paths)

    true_compare()
