#!/usr/bin/env python3
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import re
import hashlib
from html2xml import *
from redouble_and_convert2ipa import *
from freq_counts import freqCount
from errata import err
from errata import additions
import json
import pprint

class JsonEntry:

    def __init__(self, entry: "Entry"):
        self.entry = entry
        self.entry.temp = self.entry.latin + self.entry.combined_english_gloss[0]
        self.UUID = hashlib.sha1(bytes(self.entry.temp, 'utf-8'))

        self.entry.headword = self.entry.latin.replace('<b>', '').replace('</b>', '')
        self.entry.search = self.searchWord(self.entry.headword)
        first_search_word = self.entry.search[0]
        self.entry.root = self.rootGen(first_search_word)
        self.entry.ipa = self.phoneticize(first_search_word)
        self.entry.tags = self.makeTags(self.entry.notes, self.entry.part_of_speech, self.entry.headword)
        if self.entry.word_type == "postbase":
            self.entry.part_of_speech = "postbase"
        self.entry.pos = self.simplifyPos(self.entry.part_of_speech)
        if self.entry.pos == "postbase":
            self.entry.search.extend([f'-{x}-' for x in self.entry.search])
            self.entry.search.append(f'-{self.entry.root}-')
        if self.entry.pos == "verb":
            self.entry.search = [f'{x}-' for x in self.entry.search]
        self.entry.search.append(self.entry.root)
        self.entry.search.append(self.entry.headword)


        #build entryObject
        for i, element in enumerate(self.entry.combined_english_gloss):
            self.entry.combined_english_gloss[i] = element.replace('"', "&#34;")
            self.entry.combined_english_gloss[i] = element.replace('"', "&#34;")

        note_list = [f'{self.listFormat(str(note))}' for note in self.entry.notes]
        example_list = [f'{self.listFormat(str(example))}' for example in self.entry.examples]
        
        id = self.UUID.hexdigest()

        self.entryObject = {"UUID":id,
            "search_word":list(set(self.entry.search)),
            "headword":self.entry.headword,
            "root":self.entry.root,
            "cyrillic":self.entry.cyrillic,
            "ipa":self.entry.ipa,
            "jacobson":self.entry.coded_cyrillic,
            "source_pos":self.entry.part_of_speech,
            "pos":f"<span class='tag {self.entry.pos.replace(" ", "")}Tag'>{self.entry.pos.upper()}</span>",
            "tags":self.entry.tags,
            "gloss":self.entry.combined_english_gloss,
            "notes":note_list,
            "examples":example_list,
            "source":self.entry.source if self.entry.source != '' else "Badten et al (2008)",
            "etymology":self.entry.etymology.replace('< ', '&lt; ') if self.entry.etymology != '' else "No data available",
            "semantic_code":self.entry.semantic_code,
            "postbase_head_form":self.entry.postbase_head_form,                     
            "postbase_alphabetization_form":self.entry.postbase_alphabetization_form,
            "alphaA":self.entry.alphabetizationA,
            "alphaB":self.entry.alphabetizationB
            }

        #trying to introduce errata here
        keyList = ["UUID", "search_word", "headword", "root", "cyrillic", 
         "ipa", "jacobson", "source_pos", "pos", "tags", "gloss", "notes", 
         "examples", "source","etymology", "semantic_code", "postbase_head_form", 
         "postbase_alphabetization_form", "alphaA", "alphaB"]
        if id in err:
            for key in keyList:
                if key in err[id]:
                    self.entryObject[key] = err[id][key]

    def __str__(self):

        return f"{self.entry.examples[0]}"
        # for i, element in enumerate(self.entry.combined_english_gloss):
        #     self.entry.combined_english_gloss[i] = element.replace('"', "&#34;")
        #     self.entry.combined_english_gloss[i] = element.replace('"', "&#34;")

        # # gloss_string = '[' + ", ".join([f'"{gloss}"' for gloss in self.entry.combined_english_gloss]) + ']'
        # # note_string = '[' + ", ".join([f'"{gloss}"' for gloss in self.entry.notes]) +  ']'
        # # example_string = '[' + ", ".join([f'"{gloss}"' for gloss in self.entry.examples]) + ']'
        
        # # note_string = self.listFormat(note_string)
        # # example_string = self.listFormat(example_string)

        # note_list = [f'{self.listFormat(str(note))}' for note in self.entry.notes]
        # example_list = [f'{self.listFormat(str(example))}' for example in self.entry.examples]


#         entryObject = f"""
# {{"UUID":"{id}",
# "search_word":{list(set(self.entry.search))},
# "headword":"{self.entry.headword}",
# "root":{self.entry.root},
# "cyrillic":"{self.entry.cyrillic}",
# "ipa":{self.entry.ipa},
# "jacobson":"{self.entry.coded_cyrillic}",
# "source_pos":"{self.entry.part_of_speech}",
# "pos":"<span class='tag {self.entry.pos}Tag'>{self.entry.pos.upper()}</span>",
# "tags":"{self.entry.tags}",
# "gloss":{gloss_string},
# "notes":{note_string},
# "examples":{example_string},
# "source":"{self.entry.source if self.entry.source != '' else "Badten et al (2008)"}",
# "etymology":"{self.entry.etymology.replace('< ', '&lt; ') if self.entry.etymology != '' else "No data available"}",
# "semantic_code":"{self.entry.semantic_code}",
# "postbase_head_form":"{self.entry.postbase_head_form}",                     
# "postbase_alphabetization_form":"{self.entry.postbase_alphabetization_form}",
# "alphaA":"{self.entry.alphabetizationA}",
# "alphaB":"{self.entry.alphabetizationB}"
# }},"""

    def listFormat(self, baseString: str):
        result = baseString

        #format notes
        result = re.sub(r"\s+<note>", "", result)
        #result = result.replace(r"\s+<note>", "")
        result = result.replace("</note>", "")

        #format examples
        result = re.sub(r"\s+<example>\n\s*", "", result)
        result = result.replace("</example>\n", "")
        result = result.replace("<yupik-example>", "<span class='yupik_ex'>")
        result = result.replace("</yupik-example>", "</span>")
        result = result.replace(r"</yupik-example>\n\s*", "</span>")
        result = result.replace("<english-example>", "<span class='english_ex'>")
        result = re.sub(r"</english-example>\n\s*", "</span>", result)
        result = result.replace("</english-example>\n", "</span>")
        result = result.replace("<citation>", "<a href='about.html#exRefs'><span class='citation'>")
        result = re.sub(r"</citation>\n\s*", "</span></a>", result)
        result = re.sub(r"\n\s*", "", result)
       #result = result.replace("</citation>", "</span>")
        return result

    def phoneticize(self, word):
        temp = tokenize(word)
        temp = redouble(temp)
        temp = convert2ipa(temp)
        temp = tokens2string(temp)
        return temp

    def rootGen(self, word):
        #verbs
        if "-" in self.entry.latin:
            temp = word
        #nouns: "kw"
        elif word[-2:] == "kw":
            temp = word[:-2] + "w"
        #nouns: "qw"
        elif word[-2:] == "qw":
            temp = word[:-2] + "ghw"
        #nouns: marked strong gh
        elif "*" in self.entry.latin:
            temp = word[:-1] + "gh*"
        #nouns: all other gh - "qikmiq"
        elif word[-1] == "q":
            temp = word[:-1] + "gh"
        #nouns: g - "sikik"
        elif word[-1] == "k":
            temp = word[:-1] + "g"
        #noun:e-underlying - "aaggaatae" 
        elif word[-2:] == "ae":
            temp = word[:-2] + "e"
        #vowel final roots: "repa"(N), "aafte"(V)
        elif word[-1] in ["a", "i", "u", "e"]:
            temp = word
        #nouns: te
        elif word[-1] == "n":
            temp = word[:-1] + "te"
        else:
            temp = word
        return temp

    def simplifyPos(self, pos):
        if "root" in pos:
            pos = "root"
        elif "particle" in pos:
            pos = "particle"
        return pos

    def makeTags(self, notes, pos, headword):
        chukotkan = "<span class='tag ChukotkanTag'>CHUKOTKAN</span>"
        uncommon = "<span class='tag uncommonTag'>UNCOMMON</span>"
        emoRoot = "<span class='tag emotionalTag'>EMOTIONAL</span>"
        postRoot = "<span class='tag posturalTag'>POSTURAL</span>"
        demoRoot = "<span class='tag dimensionalTag'>DIMENSIONAL</span>"
        exclPart = "<span class='tag exclamatoryTag'>EXCLAMATORY</span>"
        conjPart = "<span class='tag conjunctiveTag'>CONJUNCTIVE</span>"
        interPart = "<span class='tag interjectionalTag'>INTERJECTIONAL</span>"
        advPart = "<span class='tag adverbialTag'>ADVERBIAL</span>"
        gamWord = "<span class='tag gambellWord'>SIVUQAQ</span>"
        savWord = "<span class='tag savoongaWord'>SIVUNGAQ</span>"
        #expressions?

        tagList = ""

        allNotes = " ".join([f'"{gloss}"' for gloss in notes])
        #if above some threshold frequency taglist += common
        if headword in freqCount:
            if freqCount[headword] < 10:
                tagList+= uncommon 
        if "Chukotkan" in allNotes:
            tagList+= chukotkan
        if "emotional" in pos:
            tagList+= emoRoot
        if "postural" in pos:
            tagList+= postRoot
        if "dimensional" in pos:
            tagList+= demoRoot
        if "exclamatory" in pos:
            tagList+= exclPart
        if "conjunctive" in pos:
            tagList+= conjPart
        if "interjectional" in pos:
            tagList+= interPart
        if "adverbial" in pos:
            tagList+= advPart
        if "a Savoonga word" in allNotes:
            tagList+= savWord
        if "a Gambell word" in allNotes:
            tagList+= gamWord
        
        return tagList
    
    def searchWord(self, latin):
        result = []
        search_word = []
        search_word = re.split(r",\s*", latin)
        for word in search_word:
            if("(" in word):
                if(re.match(r"[^<]\/", word)):
                    temp = re.sub(r'\((.*)\)', r'\1', word)
                    temproot = re.sub(r'\((.*)\)', '', word)
                    pref = temp.split("/")
                    for x in pref:
                        result.append(temp+temproot)
                else:
                    result.append(re.sub(r'\(.*\)', '', word))
            elif("<sup>e" in word):
                temp = re.sub(r'\<sup\>e\<\/sup\>', 'e', word)
                result.append(temp)
                result.reverse()
            
            word = re.sub(r'\<\/*\w+\>[sef\d]*', '', word)
            word = re.sub(r'[^a-zA-Z]+', '', word)
            result.append(word)
            #print("result: ", result)

        #if("," in latin):
        #    search_word = latin.split(", ")
        #    for word in search_word:
        #        word = re.sub(r'\<\/*\w+\>[ef\d]*', '', word)
        #        word = re.sub(r'[^a-zA-Z]+', '', word)
        #        result.append(word)
        #else:
        #    search_word = self.entry.latin
        #    search_word = re.sub(r'\<\/*\w+\>[ef\d]*', '', search_word)
        #    search_word = re.sub(r'[^a-zA-Z]+', '', search_word)
        #    result.append(search_word)
        return result

    #def errata(self):
        #check if entry exists in errata
        #if so: 
        #  check each attribute of the entry object for possible errata and replace
    #return entry

if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print(f"Usage:\t{sys.argv[0]} lexicon.html (output.json)", file=sys.stderr, flush=True)
        sys.exit(0)

    else:
        dictionary = HtmlDictionary(filename=sys.argv[1])
        html_tag_pattern = re.compile(r'<.*?>') #html tag regex
        if len(sys.argv) == 2 or (len(sys.argv) == 3 and sys.argv[2] == '-'):
            print("var LEX = [", sep="")
            for html_entry in dictionary:
                entry = Entry(html_entry)
                if len(html_tag_pattern.sub('', entry.latin)) > 0: # addition for catching empty strings with only html tags
                    output = JsonEntry(entry).entryObject
                    print(output, ",", sep="")
            if "post" not in sys.argv[1]:
                print(additions)
            print("];", sep="")
        else:
            with open(sys.argv[2], 'wt') as f:
                print("var LEX = [", file=f, sep="")
                for html_entry in dictionary:
                    entry = Entry(html_entry)
                    if len(html_tag_pattern.sub('', entry.latin)) > 0: # addition for catching empty strings with only html tags
                        output = str(JsonEntry(entry).entryObject)
                        print(output, ",", file=f, sep="")
                if "post" not in sys.argv[1]:
                    for addition in additions:
                        print(addition, file=f)
                print("];", file=f, sep="")
