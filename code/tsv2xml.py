#!/usr/bin/env python3

import logging
from typing import Dict, List
import re
import sys
from bs4 import BeautifulSoup
from bs4.element import Tag

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


class YupikBase:

    def __init__(self, parts: List[str], id: int):
        self.id = id
        self.part_of_speech = ""
        self.latin = [l.strip() for l in parts[0].replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").strip().replace(' / ', ', ').replace('; ', ', ').split(',')]
        #if self.latin.endswith(','):
        #    self.latin = self.latin[:-1]
        self.cyrillic = [c.strip() for c in parts[1].replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").strip().replace('; ', ', ').replace(' -- ', ', ').replace('- ', '-, ').replace('. ', ', ').split(',')]
        for i in range(len(self.latin)):
            if self.latin[i].endswith("ae"):
                self.latin[i] = self.latin[i][:-2] + "e"
        for i in range(len(self.cyrillic)):
            if self.cyrillic[i].endswith("аы"):
                self.cyrillic[i] = self.cyrillic[i][:-2] + "ы"
        
        self.coded_cyrillic = parts[2].strip()
        self.english_gloss_combined = parts[3].strip()
        self.english_gloss = list()
        if parts[4].strip():
            self.english_gloss.append(parts[4].strip())
        if parts[5].strip():
            self.english_gloss.append(parts[5].strip())
        if parts[6].strip():
            self.english_gloss.append(parts[6].strip())
        if parts[7].strip():
            self.english_gloss.append(parts[7].strip())
        self.raw_examples = YupikBase.replace_english_apostrophe(parts[8].strip())
        self.examples = self.raw_examples.strip().replace(' / ', '; ').split("; ") if len(self.raw_examples) > 0 else []
        self.examples = [e.strip() for e in self.examples if len(e.strip()) > 0]
        self._identify_part_of_speech()
        self.examples = [Example(example) for example in self.examples]
        self.russian_gloss = parts[9].strip()
        self.derived_forms = parts[10].strip()
        self.queries = parts[11].strip()
        self.etymology = parts[12].strip()
        self.source = parts[13].strip()
        self.semantic_code = parts[14].strip()
        self.alphabetization_field_a = parts[15].strip()
        self.alphabetization_field_b = parts[16].strip()
        for i in range(len(self.latin)):
            if self.latin[i].endswith('-'):
                self.latin[i] = self.latin[i][:-1]
        for i in range(len(self.cyrillic)):
            if self.cyrillic[i].endswith('-'):
                self.cyrillic[i] = self.cyrillic[i][:-1]
    
    def _identify_part_of_speech(self):
        if ((len(self.examples) > 0 and (self.examples[0] == 'demonstrative adverb base' or
                                         self.examples[0] == 'demonstrative adverb, localis case' or
                                         self.examples[0] == 'extended demonstrative pronoun' or
                                         self.examples[0] == 'extended demonstrative pronoun' or
                                         self.examples[0] == 'obscured demonstrative base' or
                                         self.examples[0] == 'obscured demonstrative pronoun' or
                                         self.examples[0] == 'restricted demonstrative pronoun' or
                                         self.examples[0] == 'obscured demonstrative pronoun' or
                                         self.examples[0] == 'interrogative demonstrative adverb')) or
            (len(self.examples) > 1 and (self.examples[1] == 'extended demonstrative pronoun' or
                                         self.examples[1] == 'demonstrative pronoun' or
                                         self.examples[1] == 'extended demonstrative pronoun' or
                                         self.examples[1] == 'restricted demonstrative pronoun'))):
            self.part_of_speech = "demonstrative"
        elif len(self.examples) > 0 and (self.examples[0] == 'essentially a particle' or
                                         self.examples[0] == 'particle (?)' or
                                         self.examples[0] == 'effectively a particle' or
                                         self.examples[0] == 'particle (perhaps two different particles)' or
                                         self.examples[0] == 'particle (actually inflected form)'):
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0] == 'particle':
            self.examples = self.examples[1:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0] == 'particle':
            self.examples = self.examples[1:]
            self.examples[0] = "" + self.examples[0]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[1] == 'particle':
            self.examples = [self.examples[0]] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0] == 'particle':
            self.examples = self.examples[1:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0] == 'particle':
            self.examples = self.examples[1:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0].startswith('particle, '):
            self.examples[0] = '' + self.examples[0][len('particle, '):]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and self.examples[0].startswith('particle: '):
            self.examples[0] = self.examples[0][len('particle: '):]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[0] == 'Chukotkan (R)' and self.examples[1] == 'particle':
            self.examples = [self.examples[0] + ""] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[0] == 'Chukotkan (R,V&amp;E)' and self.examples[1] == 'particle':
            self.examples = [self.examples[0] + ""] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[0] == 'Chukotkan' and self.examples[1] == 'particle':
            self.examples = [self.examples[0] + ""] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 1 and self.examples[0] == 'Chukotkan' and self.examples[1] == 'particle':
            self.examples = [self.examples[0] + ""] + self.examples[2:]
            self.part_of_speech = "particle"
        elif len(self.examples) > 0 and (self.examples[0] == 'exclamatory particle' or
                                         self.examples[0] == 'exclamatory particle' or
                                         self.examples[0] == 'exclamatory particle'):
            self.examples = self.examples[1:]
            self.part_of_speech = "exclamatory particle"
        elif len(self.examples) > 1 and (self.examples[1] == 'exclamatory particle' or
                                         self.examples[1] == 'exclamatory particle' or
                                         self.examples[1] == 'exclamatory particle'):
            self.examples = [self.examples[0]] + self.examples[2:]
            self.part_of_speech = "exclamatory particle"
        elif len(self.examples) > 0 and self.examples[0] == 'exclamatory particle said when one is about to lift a heavy object':
            self.examples[0] = 'said when one is about to lift a heavy object'
            self.part_of_speech = 'exclamatory particle'
        elif len(self.examples) > 0 and self.examples[0].startswith('exclamatory particle: pinighhalek kiigmi uqfigmi'):
            self.examples[0] = 'pinighhalek kiigmi uqfigmi'
            self.part_of_speech = 'exclamatory particle'
        elif len(self.examples) > 0 and self.examples[0] == 'conjunctive particle':
            self.examples = self.examples[1:]
            self.part_of_speech = "conjunctive particle"
        elif len(self.examples) > 0 and self.examples[0] == 'interjectional particle':
            self.examples = self.examples[1:]
            self.part_of_speech = "interjectional particle"
        elif len(self.examples) > 0 and (self.examples[0] == 'adverbial particle' or self.examples[0] == 'adverbial particle'):
            self.examples = self.examples[1:]
            self.part_of_speech = "adverbial particle"
        elif len(self.examples) > 0 and self.examples[0] == 'emotional root':
            self.examples = self.examples[1:]
            self.part_of_speech = "emotional root"
        elif len(self.examples) > 0 and self.examples[0].startswith('emotional root: '):
            self.examples[0] = self.examples[0][len('emotional root: '):]
            self.part_of_speech = "emotional root"
        elif len(self.examples) > 0 and self.examples[0] == 'postural root':
            self.examples = self.examples[1:]
            self.part_of_speech = "postural root"
        elif len(self.examples) > 0 and self.examples[0] == 'postural root':
            self.examples = self.examples[1:]
            self.part_of_speech = "postural root"
        elif len(self.examples) > 1 and self.examples[0] == 'Chukotkan (R)' and self.examples[1] == 'postural root':
            self.examples = [self.examples[0] + ""] + self.examples[2:]
            self.part_of_speech = "postural root"
        elif len(self.examples) > 0 and self.examples[0].startswith('postural root: '):
            self.examples[0] = self.examples[0][len('postural root: '):]
            self.part_of_speech = "postural root"
        elif len(self.examples) > 0 and self.examples[0] == 'dimensional root':
            self.examples = self.examples[1:]
            #print(self.latin)
            self.part_of_speech = "dimensional root"
        elif len(self.latin[0]) > 0 and self.latin[0][0].isalpha() and (self.latin[0][-1].isalpha() or self.latin[0][-1] == '*' or self.latin[0].endswith('(t)')):
            if self.latin[0][0].isupper():
                self.part_of_speech = "proper noun"
                #print(self.latin)
            else:
                self.part_of_speech = "noun"
        elif len(self.latin[0]) > 0 and self.latin[0][0].isalpha() and self.latin[0][-1] == '-':
            self.part_of_speech = "verb"
        else:
            raise ValueError(f"Unable to determine part of speech for {self.latin}")

    @staticmethod
    def replace_english_apostrophe(s):
        import re
        modifier_letter_apostrophe = '\u02BC'
        for index in [m.start() for m in re.finditer(r"’|'", s)]:
            if index-1 >= 0 and index+1 < len(s) and s[index-1].isalpha() and s[index+1].isalpha():
                s = s[:index] + modifier_letter_apostrophe + s[index+1:]
        return s
    
    def compound_word():
        for form in self.latin + self.cyrillic:
            if " " in form:
                return True
        return False
    
    def __str__(self):
        return self.xml()
        
    def xml(self):
        newline = "\n"
        spaces = "        "
        return f"""\
    <entry lang="ess" id="{f'ESSB{self.id:04}'}" part-of-speech="{self.part_of_speech}">
    
        <forms>
{newline.join(['            <form script="latin">' + form + '</form>' for form in self.latin])}
{newline.join(['            <form script="cyrillic">' + form + '</form>' for form in self.cyrillic])}
        </forms>
    
        <glosses>
{newline.join(['            <gloss lang="eng">' + gloss + '</gloss>' for gloss in self.english_gloss])}
        </glosses>  

        <examples-etc>{self.raw_examples}</examples-etc>
        
        <source>{self.source}</source>
        
        <etymology>{self.etymology.replace('<', '&lt;')}</etymology>
        
        <semantic-code>{self.semantic_code}</semantic-code>
        
    </entry>
"""
#{(newline + newline.join([str(e) for e in self.examples])) if len(self.examples) > 0 else ""}
#            <form script="jacobson">{self.coded_cyrillic}</form>

        
        
class YupikBases:

    def __init__(self, filename: str):
        self.entry = []
        self.headers = []
        blank_lines = 0
        alphabet_headers = 0
        id = 0
        with open(filename) as tsv_file:
            for line in tsv_file:
                entry = line.strip().split("\t")
                if len(entry) == 1:
                    blank_lines += 1
                elif len(entry) == 13:
                    alphabet_headers += 1
                elif len(entry) == 17:
                    if len(self.headers) == 0:
                        self.headers = entry
                    else:
                        id += 1
                        self.entry.append(YupikBase(entry, id))
                else:
                    raise ValueError("UnexpectedSize")
                    
        if blank_lines != 10:
            raise ValueError(f"Expected 10 blank lines but instead encountered {blank_lines}")
        
        if alphabet_headers != 19:
            raise ValueError(f"Expected 19 alphabet header lines but instead encountered {alphabet_header}")

        if len(self.entry) != (8806 - 10 - 19):
            raise ValueError(f"Expected 8777 content lines but instead encountered {len(self.entry)}")
               
    def __iter__(self):
        return iter(self.entry)

    def __len__(self) -> int:
        return len(self.entry)
        
    def __getitem__(self, item):
        return self.entry[item]


if __name__ == "__main__":

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print(f"Usage:\t{sys.argv[0]} bases.tsv (output.xml)", file=sys.stderr, flush=True)
        sys.exit(0)
    
    else:
        dictionary = YupikBases(filename=sys.argv[1])
        if len(sys.argv) == 2 or (len(sys.argv) == 3 and sys.argv[2] == '-'):
            for entry in dictionary:
                print(entry)
#                 for l in entry.latin + entry.cyrillic:
#                     if ' ' in l:
#                         print(entry)
#                         break
                    
        else:
            with open(sys.argv[2], 'wt') as xml:
                for entry in dictionary:
                    print(entry, file=xml)
