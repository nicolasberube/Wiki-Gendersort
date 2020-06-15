# Wiki-Gendersort

This is the code and database behind the paper [Wiki-Gendersort: Automatic gender detection using first names in Wikipedia](https://osf.io/preprints/socarxiv/ezw7p/)

The gender association to the 586 132 names is available in the file [NamesOut.txt](https://github.com/nicolasberube/Wiki-Gendersort/blob/master/NamesOut.txt) as a tab separated flat file. The categories are M (male), F (female), UNI (unisex), UNK (unknown) and INI (initials).

You can use the ```wiki_gendersort``` class to assign a gender based on the built dataset:
```
WG = wiki_gendersort()
WG.assign('Nicolas')
WG.file_assign('test_file.txt')
```

You can also build your own database of names with ```build_dataset()```
