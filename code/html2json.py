#!/usr/bin/env python3
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import re
import hashlib
from html2xml import *
from redouble_and_convert2ipa import *
from freq_counts import freqCount

class JsonEntry:

    def __init__(self, entry: "Entry"):
        self.entry = entry
        self.entry.temp = self.entry.latin + self.entry.combined_english_gloss[0]
        self.UUID = hashlib.sha1(bytes(self.entry.temp, 'utf-8'))
        #search_word = re.sub(r'\<\/*\w+\>\w*', '', self.entry.latin)
        self.entry.headword = self.entry.latin.replace('<b>', '').replace('</b>', '')
        #self.entry.search = re.sub(r'[^a-zA-Z]+', '', search_word)
        self.entry.search = self.searchWord(self.entry.latin)
        self.entry.root = self.rootGen(self.entry.search)
        self.entry.ipa = self.phoneticize(self.entry.search)
        self.entry.tags = self.makeTags(self.entry.notes, self.entry.part_of_speech, self.entry.headword)
        if self.entry.word_type == "postbase":
            self.entry.part_of_speech = "postbase"
        self.entry.pos = self.simplifyPos(self.entry.part_of_speech)


    def __str__(self):
        for i, element in enumerate(self.entry.combined_english_gloss):
            self.entry.combined_english_gloss[i] = element.replace('"', "&#34;")
            self.entry.combined_english_gloss[i] = element.replace('"', "&#34;")

        gloss_string = '[' + ", ".join([f'"{gloss}"' for gloss in self.entry.combined_english_gloss]) + '],'
        note_string = '[' + ", ".join([f'"{gloss}"' for gloss in self.entry.notes]) +  '],'
        example_string = '[' + ", ".join([f'"{gloss}"' for gloss in self.entry.examples]) + '],'
        
        note_string = self.listFormat(note_string)
        example_string = self.listFormat(example_string)
        
        return f"""
{{"UUID":"{self.UUID.hexdigest()}",
"search_word":{self.entry.search},
"headword":"{self.entry.headword}",
"root":{self.entry.root},
"cyrillic":"{self.entry.cyrillic}",
"ipa":{self.entry.ipa},
"jacobson":"{self.entry.coded_cyrillic}",
"source_pos":"{self.entry.part_of_speech}",
"pos":"<span class='tag {self.entry.pos}Tag'>{self.entry.pos.upper()}</span>",
"tags":"{self.entry.tags}",
"gloss":{gloss_string}
"notes":{note_string}
"examples":{example_string}
"source":"{self.entry.source if self.entry.source != '' else "Badten et al, 2001"}",
"etymology":"{self.entry.etymology.replace('< ', '&lt; ')}",
"semantic_code":"{self.entry.semantic_code}",
"postbase_head_form":"{self.entry.postbase_head_form}",                     
"postbase_alphabetization_form":"{self.entry.postbase_alphabetization_form}",
"alphaA":"{self.entry.alphabetizationA}",
"alphaB":"{self.entry.alphabetizationB}"
}},"""

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
        result = result.replace("<citation>", "\n\t\t<span class='citation'>")
        result = re.sub(r"</citation>\n\s*", "</span>", result)
        result = re.sub(r"\n\s*", "", result)
       #result = result.replace("</citation>", "</span>")
        return result

    def phoneticize(self, roots):
        result = []
        for word in roots:
            temp = tokenize(word)
            temp = redouble(temp)
            temp = convert2ipa(temp)
            temp = tokens2string(temp)
            result.append(temp)
        return result

    def rootGen(self, roots):
        result = []
        for word in roots:
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
            result.append(temp)
        return result

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
        #dialect specific tags
        #expressions?

        tagList = ""

        #if above some threshold frequency taglist += common
        if headword in freqCount:
            if freqCount[headword] < 10:
                tagList+= uncommon 
        if "Chukotkan" in " ".join([f'"{gloss}"' for gloss in notes]):
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
        
        return tagList
    
    def searchWord(self, latin):
        result = []
        search_word = []
        if("," in latin):
            search_word = self.entry.latin.split(", ")
            for word in search_word:
                word = re.sub(r'\<\/*\w+\>[ef\d]*', '', word)
                word = re.sub(r'[^a-zA-Z]+', '', word)
                result.append(word)
        else:
            search_word = self.entry.latin
            search_word = re.sub(r'\<\/*\w+\>[ef\d]*', '', search_word)
            search_word = re.sub(r'[^a-zA-Z]+', '', search_word)
            result.append(search_word)
        return result

if __name__ == "__main__":

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print(f"Usage:\t{sys.argv[0]} lexicon.html (output.json)", file=sys.stderr, flush=True)
        sys.exit(0)

    else:
        dictionary = HtmlDictionary(filename=sys.argv[1])
        html_tag_pattern = re.compile(r'<.*?>') #html tag regex
        if len(sys.argv) == 2 or (len(sys.argv) == 3 and sys.argv[2] == '-'):
            for html_entry in dictionary:
                entry = Entry(html_entry)
                if len(html_tag_pattern.sub('', entry.latin)) > 0: # addition for catching empty strings with only html tags
                    print(JsonEntry(entry))
        else:
            with open(sys.argv[2], 'wt') as json:
                for html_entry in dictionary:
                    entry = Entry(html_entry)
                    if len(html_tag_pattern.sub('', entry.latin)) > 0: # addition for catching empty strings with only html tags
                        print(JsonEntry(entry), file=json)
