#!/usr/bin/env python3

import logging
from typing import Dict, List
import re
import sys
from bs4 import BeautifulSoup
from bs4.element import Tag


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

    def __init__(self, html_entry: "HtmlEntry"):
        if len(html_entry) != 28:
            raise ValueError("There must be exactly 28 fields, but there were {len(fields)}")
        self._fields = dict(zip(Entry.field_names, list(html_entry)))
        
        self.latin = self.extract(0)
        self.cyrillic = self.extract(-1)
        self.coded_cyrillic = self.extract(1)
        
        self.raw_examples = self.extract(4)
        self.examples = self.raw_examples.strip().replace(' / ', '; ').split("; ") if len(self.raw_examples) > 0 else []
        self.examples = [e.strip() for e in self.examples if len(e.strip()) > 0]

        if len(self.examples) > 0 and self.examples[0] == '<i>particle</i>':
            self.examples = self.examples[1:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0] == '<i>particle':
            self.examples = self.examples[1:]
            self.examples[0] = "<i>" + self.examples[0]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[1] == '<i>particle':
            self.examples = [self.examples[0]] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0] == 'particle':
            self.examples = self.examples[1:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0] == 'particle</i>':
            self.examples = self.examples[1:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[0] == '<i>Chukotkan (R)' and self.examples[1] == 'particle</i>':
            self.examples = [self.examples[0] + "</i>"] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[0] == '<i>Chukotkan (R,V&amp;E)' and self.examples[1] == 'particle</i>':
            self.examples = [self.examples[0] + "</i>"] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[0] == '<i>Chukotkan' and self.examples[1] == 'particle</i>':
            self.examples = [self.examples[0] + "</i>"] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0] == '<i>adverbial particle</i>':
            self.examples = self.examples[1:]
            self.part_of_speech = "adverbial particle"
        elif len(self.examples) > 0 and self.examples[0] == '<i>emotional root</i>':
            self.examples = self.examples[1:]
            self.part_of_speech = "emotional root"
        elif len(self.examples) > 0 and self.examples[0].startswith('<i>emotional root:</i> '):
            self.examples[0] = self.examples[0][len('<i>emotional root:</i> '):]
            self.part_of_speech = "emotional root"
        elif len(self.examples) > 0 and self.examples[0] == '<i>postural root</i>':
            self.examples = self.examples[1:]
            self.part_of_speech = "postural root"
        elif len(self.examples) > 0 and self.examples[0] == 'postural root':
            self.examples = self.examples[1:]
            self.part_of_speech = "postural root"
        elif len(self.examples) > 1 and self.examples[0] == '<i>Chukotkan (R)' and self.examples[1] == 'postural root</i>':
            self.examples = [self.examples[0] + "</i>"] + self.examples[2:]
            self.part_of_speech = "postural root"
        elif len(self.examples) > 0 and self.examples[0].startswith('<i>postural root:</i> '):
            self.examples[0] = self.examples[0][len('<i>postural root:</i> '):]
            self.part_of_speech = "postural root"
        elif len(self.examples) > 0 and self.examples[0] == '<i>dimensional root</i>':
            self.examples = self.examples[1:]
            print(self.latin)
            self.part_of_speech = "dimensional root"
        elif len(self.latin) > 0 and self.latin[0].isalpha() and self.latin[-1].isalpha():
            if self.latin[0].isupper():
                self.part_of_speech = "proper noun"
                print(self.latin)
            else:
                self.part_of_speech = "noun"
        else:
            self.part_of_speech = None

        self.examples = [Example(example) for example in self.examples]
        self.notes = [Note(example.yupik) for example in self.examples if len(example.english) == 0]
        self.examples = [example for example in self.examples if len(example.english) > 0]

        self.combined_english_gloss = self.extract(17).split("; ")

        self.etymology = self.extract(19)
        self.semantic_code = self.extract(20)
        self.source = self.extract(21)

    @staticmethod
    def replace_english_apostrophe(s):
        import re
        modifier_letter_apostrophe = '\u02BC'
        for index in [m.start() for m in re.finditer(r"’|'", s)]:
            if index-1 >= 0 and index+1 < len(s) and s[index-1].isalpha() and s[index+1].isalpha():
                s = s[:index] + modifier_letter_apostrophe + s[index+1:]
        return s

    def extract(self, index: int) -> str:

        result = self._fields[Entry.field_names[index]]
        result = result.strip()
        result = Entry.replace_english_apostrophe(result)
        result = result.replace('\xa0','')
        
        result = re.sub(r'<span class="Apple-converted-space">\s*</span>', ' ', result)
        
        result = result.replace('yu<u>k', 'yu(u)k')
        
        if result.startswith('</i>') or result.startswith('</b>'):
            result = result[4:]
        elif result.startswith('</sup>') or result.startswith('</sub>'):
            result = result[6:]

        for tag in ['sup', 'sub', 'i', 'b']:
            opening_tag = f"<{tag}>"
            closing_tag = f"</{tag}>"
            
            if result.startswith(closing_tag):
                result = result[len(closing_tag):]  # String shouldn't start with a closing tag
        
            count_open = result.count(opening_tag)
            count_close = result.count(closing_tag)
            
            if count_open > count_close:
                # There shouldn't be too many opening tags
                result = result + closing_tag
            
            if count_open < count_close:
                # There shouldn't be too many closing tags
                result = opening_tag + result
            
            if result.find(closing_tag) < result.find(opening_tag):
                # The first closing tag shouldn't be before the first opening tag
                result = opening_tag + result
                
            if result.rfind(opening_tag) > result.rfind(closing_tag):
                # The last opening tag shouldn't be after the last closing tag
                result = result + closing_tag

            while f" {closing_tag}" in result or f";{closing_tag}" in result:
                result = result.replace(f" {closing_tag}", f"{closing_tag} ")
                result = result.replace(f";{closing_tag}", f"{closing_tag};")

        return result

    def __str__(self):
        newline = "\n"
        return f"""\
    <entry part-of-speech="{self.part_of_speech}">
    
        <forms>
            <form script="latin"   >{self.latin}</form>
            <form script="cyrillic">{self.cyrillic}</form>
            <form script="jacobson">{self.coded_cyrillic}</form>
        </forms>
    
        <glosses>
{newline.join(['            <gloss lang="eng">' + gloss + '</gloss>' for gloss in self.combined_english_gloss])}
        </glosses>

        <notes>{(newline + newline.join([str(e) for e in self.notes])) if len(self.notes) > 0 else ""}
        </notes>

        <examples>{(newline + newline + newline.join([str(e) for e in self.examples])) if len(self.examples) > 0 else ""}
        </examples>
        
        <source>{self.source}</source>
        
        <etymology>{self.etymology.replace('<', '&lt;')}</etymology>
        
        <semantic-code>{self.semantic_code}</semantic-code>
        
    </entry>
"""
# {"        " + "<source>" + self.source + "</source>" + newline if len(self.source) > 0 else ""}


class Example:

    def __init__(self, example_string: str):
        if len(example_string) == 0:
            raise ValueError("Examples must be non-zero in length")
        self.raw_string = example_string
        yupik_start = 0
        yupik_end = example_string.find('‘') - 1 if '‘' in example_string else len(example_string)
        english_start = yupik_end + 1 if '‘' in example_string else len(example_string)
        english_end = example_string.find('’')+1 if '’' in example_string else len(example_string)
        citation_start = english_end if '(' in example_string[english_end:] else len(example_string)
        citation_end = len(example_string)
        self.yupik = example_string[yupik_start:yupik_end].strip()
        self.english = example_string[english_start:english_end].strip()
        self.citation = example_string[citation_start:citation_end].strip()

    def __str__(self):

        if len(self.yupik) == 0 and len(self.english) == 0 and len(self.citation) == 0:
            return ""

        result = "            <example>\n"
        if len(self.yupik) > 0:
            result += "                <yupik-example>" + self.yupik + "</yupik-example>\n"
        if len(self.english) > 0:
            result += "                <english-example>" + self.english + "</english-example>\n"
        if len(self.citation) > 0:
            result += "                <citation>" + self.citation + "</citation>\n"
        result += "            </example>\n"
        return result

    def __repr__(self):
        return f"Example({self.raw_string})"


class Note:

    def __init__(self, value: str):
        self.value: str = value

    def __str__(self):

        if len(self.value) == 0:
            return ""
        else:
            return "            <note>" + self.value + "</note>"


class HtmlEntry:

    def __init__(self, fields: List[str]):
        if len(fields) != 28:
            raise ValueError(f"There must be exactly 28 fields, but there were {len(fields)}")
        self._fields: List[str] = fields

    def __getitem__(self, item):
        return self._fields[item]

    def __len__(self):
        return len(self._fields)

    def __iter__(self):
        return iter(self._fields)

    def __str__(self):
        return "\n".join(self._fields)


class HtmlDictionary:

    delimiter = re.compile(r'<span class="Apple-tab-span">\s*</span>')

    def __init__(self, filename: str):
        with open(filename) as html_file:
            html = BeautifulSoup(html_file, "html.parser")
            self._tags: List[Tag] = html.body.find_all("p")
            self._entries = [None] * len(self._tags)

    def __getitem__(self, index) -> List[HtmlEntry]:
        if isinstance(index, int):
            if self._entries[index] is None:
                self._entries[index] = HtmlDictionary.parse_entry(self._tags[index])
            return self._entries[index]
        else:
            raise ValueError

    def __len__(self) -> int:
        return len(self._entries)

    @staticmethod
    def parse_entry(entry: Tag) -> HtmlEntry:
        body = ''.join([str(item) for item in entry.contents])
        parts = HtmlDictionary.delimiter.split(body)
        if len(parts) == 26:  # base
            parts.insert(-3, '')  # Insert empty string for 'postbase head form'
            parts.insert(-3, '')  # Insert empty string for 'postbase alphabetization form'
        elif len(parts) == 27:  # post-base
            parts.insert(-2, '')  # Insert empty string for 'alphabetization field A'
        return HtmlEntry(parts)

    @staticmethod
    def load(*, filename: str) -> BeautifulSoup:
        with open(filename) as html_file:
            logging.info(f"Loading file {filename} using BeautifulSoup")
            html = BeautifulSoup(html_file, "html.parser")
            logging.info(f"File {filename} loaded")
            return html


if __name__ == "__main__":

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print(f"Usage:\t{sys.argv[0]} lexicon.html (output.xml)", file=sys.stderr, flush=True)
        sys.exit(0)
    
    else:
        dictionary = HtmlDictionary(filename=sys.argv[1])
        if len(sys.argv) == 2 or (len(sys.argv) == 3 and sys.argv[2] == '-'):
            for html_entry in dictionary:
                entry = Entry(html_entry)
                if len(entry.latin) > 0:
                    print(entry)
        else:
            with open(sys.argv[2], 'wt') as xml:
                for html_entry in dictionary:
                    entry = Entry(html_entry)
                    if len(entry.latin) > 0:
                        print(entry, file=xml)
