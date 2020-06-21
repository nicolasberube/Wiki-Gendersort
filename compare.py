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

    Also print out basic stats for the wiki-gendersort dataset.

    This function prints the comparison results in the console.

    Parameters
    ----------
    sort_path: str or Path
        Path to the Out.txt file of the dataset.
        Can also be a list of paths.
    """
    if not isinstance(sort_path, list):
        sort_path = [sort_path]
    sort_path = [Path(s) for s in sort_path]

    WG = wiki_gendersort(verbose=True)
    compare_GSs = [wiki_gendersort(input_path=sp, verbose=True)
                   for sp in sort_path]

    print('Importing WOS authorship')
    cwd = Path(__file__).parent.absolute()
    names_ppm = {}
    wos_n_names = 0
    ppm_test = 0
    t1m = []
    with open(cwd / 'data_compare' / 'raw' / 'WOS_authors.txt') as file:
        for lin in tqdm(file.read().split('\n')):
            ls = lin.replace('\ufeff', '').split('\t')
            if len(ls) == 3:
                wos_n_names += 1
                name = ls[0]
                occ = float(ls[-1])
                if len(t1m) <= 10**6 and WG.assign(name) != 'INI':
                    ppm_test += occ
                    t1m.append([ls[0], ls[1]])
                if name not in names_ppm:
                    names_ppm[name] = 0.
                names_ppm[name] += occ

    # Imports log file data for gender assignation method
    log_path = cwd / 'NamesLog.txt'
    name_method = {}
    with open(log_path) as f:
        datalogtemp = f.read()
    datalogtemp = datalogtemp.split('\n\n')
    for d in datalogtemp:
        if len(d) != 0:
            ds = d.split('\n')
            if len(ds) >= 2:
                name = ds[0]
                gend = ds[-1].replace(' ', '').split('=')[-1]
                method = 1
                if '2' in ds:
                    method = 2
                if gend == 'UNK':
                    method = 0
                name_method[name] = method

    print('Processing comparative data tables')
    default_names = []
    compare_names = [[] for _ in range(len(compare_GSs))]
    gender_dict = {'M': 0,
                   'F': 1,
                   'UNI': 2,
                   'UNK': 3,
                   'INI': 4}
    tables = [[[0. for _ in range(len(gender_dict))]
               for _ in range(len(gender_dict))]
              for _ in range(len(compare_GSs))]
    gender_tokens = [[] for _ in range(len(gender_dict))]
    gender_ppm = [0 for _ in range(len(gender_dict))]
    method_tokens = [[] for _ in range(len(set(name_method.values())))]
    method_ppm = [0 for _ in range(len(set(name_method.values())))]

    sleep(0.5)
    all_tokens = []
    for name, ppm in tqdm(names_ppm.items()):
        current_tokens = nameclean(name)
        all_tokens += current_tokens
        default_gender = WG.assign(name)
        if default_gender in {'M', 'F', 'UNI'} and WG.matched_name:
            default_gender = gender_dict[default_gender]
            method = name_method[WG.matched_name]
            default_names.append(WG.matched_name)
            gender_tokens[default_gender].append(WG.matched_name)
            method_tokens[method].append(WG.matched_name)
            method_ppm[method] += ppm
        elif default_gender == 'UNK':
            default_gender = gender_dict[default_gender]
            method = 0
            gender_tokens[default_gender] += current_tokens
            method_tokens[method] += current_tokens
            method_ppm[method] += ppm
        else:
            default_gender = gender_dict[default_gender]
        gender_ppm[default_gender] += ppm
        for i, GS in enumerate(compare_GSs):
            compare_gender = GS.assign(name)
            if compare_gender in {'M', 'F', 'UNI'} and GS.matched_name:
                compare_names[i].append(GS.matched_name)
            compare_gender = gender_dict[compare_gender]
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
        mm = tables[i][gender_dict['M']][gender_dict['M']]
        ff = tables[i][gender_dict['F']][gender_dict['F']]
        mf = tables[i][gender_dict['M']][gender_dict['F']]
        fm = tables[i][gender_dict['F']][gender_dict['M']]
        print('errorCodedWithoutNA: %.2f %%' % (100*(fm+mf)/(mm+fm+mf+ff)))
        print('1-errorCodedWithoutNA: %.2f %%' %
              (100-100*(fm+mf)/(mm+fm+mf+ff)))
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
        print(sort_name)
        print(' '*4 +
              'Identified authors : %.2f %%' %
              (100*sum(compare_totals[:2])/sum(compare_totals)))
        print(' '*4 +
              'Name tokens used for identification: %i (out of %i)' %
              (n_names[i], len([v for v in GS.names_key.values()
                                if v not in {'INI', 'UNK'}])))
        print()
        print()

    print(center_string('METHOD', 15) + '|' +
          center_string('#TOKENS', 9) + '|' +
          center_string('OCC (%)', 9) + '|')
    print(center_string('Initials', 15) + '|' +
          center_string('N\\A', 9) + '|' +
          ' %5.2f %% ' % (ini_ppm/10000) + '|')
    print(center_string('1st method', 15) + '|' +
          center_string('%i' % (len(set(method_tokens[1]))), 9) + '|' +
          ' %5.2f %% ' % (method_ppm[1]/10000) + '|')
    print(center_string('2nd method', 15) + '|' +
          center_string('%i' % (len(set(method_tokens[2]))), 9) + '|' +
          ' %5.2f %% ' % (method_ppm[2]/10000) + '|')
    print(center_string('gender unknown', 15) + '|' +
          center_string('%i' % (len(set(method_tokens[0]))), 9) + '|' +
          ' %5.2f %% ' % (method_ppm[0]/10000) + '|')
    print()
    print(center_string('GENDER', 15) + '|' +
          center_string('#TOKENS', 9) + '|' +
          center_string('OCC (%)', 9) + '|')
    for gender, gi in gender_dict.items():
        print(center_string(gender, 15) + '|' +
              center_string('%i' % (len(set(gender_tokens[gi]))), 9) + '|' +
              ' %5.2f %% ' % (gender_ppm[gi]/10000) + '|')
    print()
    print('Total unique full names in WoS: %i' % wos_n_names)
    print('Total unique first name in WoS: %i' % len(names_ppm))
    print('Total unique first name tokens in WoS: %i' % len(set(all_tokens)))
    print()
    print()


def namsor_compare():
    """Compare a NamSor dataset to the wiki-gendersort dataset.

    This function prints the comparison results in the console.
    """

    WG = wiki_gendersort(verbose=True)

    print('Processing comparative data tables')
    cwd = Path(__file__).parent.absolute()
    namsor_path = cwd / 'data_compare' / 'raw' / 'Namsor_1M.txt'

    default_names = []
    gender_dict = {'M': 0,
                   'F': 1,
                   'UNI': 2,
                   'UNK': 3,
                   'INI': 4}
    table = [[0. for _ in range(len(gender_dict))]
             for _ in range(len(gender_dict))]
    ppm = 0
    cumul_ppm = 0
    sleep(0.5)
    with open(namsor_path, 'r') as raw_file:
        raw_file.readline()
        for lin in tqdm(raw_file.readlines(), total=1000000):
            ls = lin.replace('\n', '').split('\t')
            name = ls[0]
            ppm = float(ls[2]) - cumul_ppm
            cumul_ppm = float(ls[2])
            default_gender = WG.assign(name)
            compare_gender = ls[-1]
            if compare_gender == 'male':
                compare_gender = 'M'
            elif compare_gender == 'female':
                compare_gender = 'F'
            elif compare_gender == 'unknown':
                compare_gender = 'UNK'
            else:
                print('genre introuvable: '+compare_gender)
            if default_gender in {'M', 'F', 'UNI'} and WG.matched_name:
                default_gender = gender_dict[default_gender]
                default_names.append(WG.matched_name)
            else:
                default_gender = gender_dict[default_gender]
            compare_gender = gender_dict[compare_gender]
            table[compare_gender][default_gender] += ppm

    default_n_names = len(set(default_names))

    # Prints out results
    col_ids = [center_string(g, 9)
               for g, rank in sorted(gender_dict.items(),
                                     key=lambda x:x[1])]

    # Print cross-results table
    default_totals = [sum(table[j][k]
                          for j in range(len(table)))
                      for k in range(len(table))]
    compare_totals = [sum(table[j])
                      for j in range(len(table))]
    total = (sum(default_totals) + sum(compare_totals))/2
    print(' '*15 + '|' + center_string('Wiki-GenderSort',
                                       len(col_ids)*10-1) + '|')
    print(center_string('NamSor', 15) + '|' +
          '|'.join(col_ids) + '|' +
          center_string('Total', 9) + '|')
    for j, col_id in enumerate(col_ids):
        print(' '*6 + col_id + '|' +
              '|'.join(' %5.2f %% ' % (100*percent/total)
                       for percent in table[j]) + '|' +
              ' %5.2f %% ' % (100*compare_totals[j]/total) + '|')
    print(' '*6 + center_string('Total', 9) + '|' +
          '|'.join(' %5.2f %% ' % (100*percent/total)
                   for percent in default_totals) + '|' +
          '%6.2f %% ' % 100 + '|')
    mm = table[gender_dict['M']][gender_dict['M']]
    ff = table[gender_dict['F']][gender_dict['F']]
    mf = table[gender_dict['M']][gender_dict['F']]
    fm = table[gender_dict['F']][gender_dict['M']]
    print('Proportion of authorship: %.2f %%' % sum(default_totals))
    print('errorCodedWithoutNA: %.2f %%' % (100*(fm+mf)/(mm+fm+mf+ff)))
    print('1-errorCodedWithoutNA: %.2f %%' % (100-100*(fm+mf)/(mm+fm+mf+ff)))
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
    print('NamSor')
    print(' '*4 +
          'Identified authors : %.2f %%' %
          (100*sum(compare_totals[:2])/sum(compare_totals)))
    print()
    print()


def true_compare():
    """Generate default stats for the wiki-gendersort dataset

    Compare the wiki-gendersort dataset with the true label
    dataset of "Comparison and benchmark of name-to-gender inference services"
    (https://peerj.com/articles/cs-156/)

    This function prints the results in the console
    """
    cwd = Path(__file__).parent.absolute()
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
                  cwd / 'data_compare' / 'GendercOut.txt']
    namsor_compare()
    table_compare(sort_paths)
    true_compare()
