#!/usr/bin/env python3

from typing import List
import re
import sys
from bs4 import BeautifulSoup

class Entry:

    field_names = [
        'CSY word (Lat. orth.)',
        'CSY word (Cyr. orth.)',
        'Eng. gloss 1',
        'Russ. gloss 1',
        "ex'ples, etym, etc.",
        'Eng. gloss 2',
        'Eng. gloss 3',
        'Russ. gloss 2',
        'Russ. gloss 3',
        'CSY word (Cyr.) num. eq.',
        'Russ. gloss 1 num. eq.',
        'Russ. gloss 2 num. eq.',
        'Russ. gloss 3 num. eq.',
        'queries, etc.',
        'Eng. gloss 4',
        'Russ. gloss 4',
        'Russ. gloss 4 num. eq.',
        'combined English gloss',
        'combined Russian gloss',
        'PE (PY) source',
        'symantic code',
        'Sib. source code',
        'derived forms',
        'postbase head form',             # Only occurs in postbases
        'postbase alphabetization form',  # Only occurs in postbases
        'alphabetization field A',        # Only occurs in     bases
        'alphabetization field B',
        'CSY word (Cyrillic)'
    ]


    def __init__(self, *, fields: List[str]):
        if len(fields) != 28:
            raise ValueError("There must be exactly 28 fields, but there were {len(fields)}")
        self._fields = dict(zip(Entry.field_names, fields))
        
        self.latin = self.extract(0)
        self.cyrillic = self.extract(-1)
        self.coded_cyrillic = self.extract(1)
        
        self.examples = self.extract(4)
        
        self.combined_english_gloss = self.extract(17)

    def extract(self, index: int) -> str:
        result = self._fields[Entry.field_names[index]]
        
        result = result.replace('\xa0','')
        
        result = re.sub(r'<span class="Apple-converted-space">\s*</span>', ' ', result)
        
        result = result.replace('yu<u>k', 'yu(u)k')
        
        if result.startswith('</i>') or result.startswith('</b>'):
            result = result[4:]
        elif result.startswith('</sup>') or result.startswith('</sub>'):
            result = result[6:]
        
        open_i = result.count('<i>')
        close_i = result.count('</i>')
        
        open_b = result.count('<b>')
        close_b = result.count('</b>')

        open_sup = result.count('<sup>')
        close_sup = result.count('</sup>')
        
        open_sub = result.count('<sub>')
        close_sub = result.count('</sub>')

        for tag in ['sup', 'sub', 'i', 'b']:
            opening_tag = f"<{tag}>"
            closing_tag = f"</{tag}>"
            
            if result.startswith(closing_tag):
                result = result[len(closing_tag):]  # String shouldn't start with a closing tag
        
            count_open = result.count(opening_tag)
            count_close = result.count(closing_tag)
            
            if count_open > count_close:
                #print(f"Too many {opening_tag}:\t{count_open} > {count_close}\t{result}")
                result = result + closing_tag
            
            if count_open < count_close:
                #print(f"Too many {closing_tag}:\t{count_open} < {count_close}\t{result}")
                result = opening_tag + result
            
            if result.find(closing_tag) < result.find(opening_tag):
                result = opening_tag + result
                
            if result.rfind(opening_tag) > result.find(closing_tag):
                result = result + closing_tag

            while f" {closing_tag}" in result or f";{closing_tag}" in result:
                result = result.replace(f" {closing_tag}", f"{closing_tag} ")
                result = result.replace(f";{closing_tag}", f"{closing_tag};")

        return result

    def __str__(self):
        return f"""\
    <entry>
        <orthography type="latin">{self.latin}</orthography>
        <orthography type="cyrillic" code="{self.coded_cyrillic}">{self.cyrillic}</orthography>
    
        <glosses lang="eng">{self.combined_english_gloss}</glosses>
    
        <examples>{self.examples}</examples>
    </entry>
"""

def load(*, filename: str) -> BeautifulSoup:
    with open(filename) as html_file:
        print(f"Loading file {filename} ... ", end="", flush=True, file=sys.stderr)
        html = BeautifulSoup(html_file, "html.parser")
        print("done.", end="\n", flush=True, file=sys.stderr)
        return html

def parse(*, filename: str):
    html = load(filename=sys.argv[1])

    entries = html.body.find_all("p")
    print(f"Identified {len(entries)} entries in {filename}.", flush=True, file=sys.stderr)
    
    pattern = re.compile(r'<span class="Apple-tab-span">\s*</span>')
    
    for num, entry in enumerate(entries):
        body = ''.join([str(item) for item in entry.contents])
        parts = pattern.split(body)
        if len(parts) == 26:  # base
            parts.insert(-3, '') # Insert empty string for 'postbase head form'
            parts.insert(-3, '') # Insert empty string for 'postbase alphabetization form'
        elif len(parts) == 27:  # post-base
            parts.insert(-2, '') # Insert empty string for 'alphabetization field A'
        
        entry = Entry(fields=parts)
        print(entry)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(f"Usage:\t{sys.argv[0]} lexicon.html", file=sys.stderr, flush=True)
        sys.exit(0)
    
    else:
        parse(filename=sys.argv[1])
