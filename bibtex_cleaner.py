
# coding: utf-8

# In[285]:

import bibtexparser
import difflib 
import re
import os
from sets import Set
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import codecs


# # Load the .bib files and .tex files

# In[286]:

bibfileNames = ['energyLandscape.bib','bibfile_original.bib', 'bibfile.bib','dynamical_trajectories.bib']
texFileNames = ["NATCOMM_si_revision_v3.tex"]


# # Define the similarity between strings

# In[287]:

def similar(seq1, seq2, simValue=0.9):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > simValue


# # Compare two entries

# In[288]:

def compareTwoEntry(bib_1, bib_2):
    '''
    compare whether two entries are the same, may need to add try-catch 
    '''
    if bib_1['ID']==bib_2['ID']:
        return True
    else:
        try:
            a1 = similar(bib_1['title'], bib_2['title'], 0.8)
        except KeyError:
            return False
        #try:
        #    a2 = similar(bib_1['journal'], bib_2['journal'])
        #except KeyError:
        a2 = True
        try:    
            a3 = similar(bib_1['volume'], bib_2['volume'])
        except KeyError:
            a3 = True
        try:
            a4 = similar(bib_1['year'], bib_2['year'])
        except KeyError:
            a4 = True
        try:    
            a5 = similar(bib_1['pages'], bib_2['pages'])
        except KeyError:
            a5 = True
        #try:
        #    a6 = similar(bib_1['author'], bib_2['author'], 0.8)
        #except KeyError:
        a6 = True
        if similar(bib_1['title'], bib_2['title'], 0.95) and a4:
            return True
        else:
            return (a1 and a2 and a3 and a4 and a5 and a6)


# # Save unique entries only but mutiple keys

# In[289]:

def uniqueBibTexItem(bib_entries):
    '''
    kill the duplicated items and save the key names
    '''
    currIdx = 0
    while currIdx < len(bib_entries):
        if currIdx == 0:
            bib_entries[currIdx]['ID_SETS'] = Set([bib_entries[currIdx]['ID']])
            currIdx = currIdx + 1
        else:
            flag = False
            for i in range(currIdx):
                if bib_entries[currIdx]['ID'] in bib_entries[i]['ID_SETS']:
                    #print bib_entries[currIdx]['ID'],'\t',bib_entries[currIdx]['title'], '\n', \
                    #    bib_entries[currIdx]['ID'], '\t', bib_entries[i]['title'],'\n','\n'
                    del bib_entries[currIdx]
                    flag = True
                    break
                elif compareTwoEntry(bib_entries[currIdx], bib_entries[i]):
                    bib_entries[i]['ID_SETS'].add(bib_entries[currIdx]['ID'])
                    #print bib_entries[currIdx]['ID'],'\t',bib_entries[currIdx]['title'], '\n', \
                    #    bib_entries[currIdx]['ID'], '\t', bib_entries[i]['title'],'\n','\n'
                    del bib_entries[currIdx]
                    flag = True
                    break
            if not flag:
                bib_entries[currIdx]['ID_SETS'] = Set([bib_entries[currIdx]['ID']])
                currIdx = currIdx + 1
    return bib_entries


# # Merge the duplicated items

# In[290]:

# Read the .bib files into the bibtex_subjects
parser = BibTexParser()
parser.customization = convert_to_unicode
bib_database = bibtexparser.loads("") 
for bibfile in bibfileNames:    
    with open(bibfile) as tmp_bibFile:
        tmp_bibtex_str = tmp_bibFile.read()
        tmp = bibtexparser.loads(tmp_bibtex_str, parser=parser) 
        bib_database.entries = bib_database.entries + tmp.entries[:]
uniqBibEntries = uniqueBibTexItem(bib_database.entries)


# # Replace in the .tex files

# In[291]:

if not os.path.exists("output"):
    os.makedirs("output")
for texfile in texFileNames:
    with open(texfile) as texFile:
        texString = texFile.read()
        for i in range(len(bib_database.entries)):
            curr_bib_item = bib_database.entries[i]
            for id_name in curr_bib_item['ID_SETS']:
                if id_name != curr_bib_item['ID']:
                    texString = re.sub(id_name, curr_bib_item['ID'],texString)
    with open("output/clean_"+texfile, "a+") as save_tex_file:
        save_tex_file.write(texString)


# In[295]:

for bibitem in bib_database.entries:
    try:
        del bibitem['ID_SETS']
    except KeyError:
        continue

writer = BibTexWriter()
with codecs.open("output/clean_bibuniq_combo.bib","w+",encoding='utf-8') as save_bib_file:
    save_bib_file.write(writer.write(bib_database))


# In[294]:

len(bib_database.entries)


# In[ ]:



