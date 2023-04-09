#!/usr/bin/env python3

import re
import hashlib
from html2xml import *
from redouble_and_convert2ipa import *

class JsonEntry:

    def __init__(self, entry: "Entry"):
        self.entry = entry
        self.entry.temp = self.entry.latin + self.entry.combined_english_gloss[0]
        self.UUID = hashlib.sha1(bytes(self.entry.temp, 'utf-8'))
        search_word = re.sub(r'\<\/*\w+\>', '', self.entry.latin)
        self.entry.search = re.sub(r'[^a-zA-Z]+', '', search_word)
        self.entry.root = self.rootGen(self.entry.search)
        self.entry.ipa = self.phoneticize(self.entry.root)


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
"search_word":"{self.entry.search}",
"headword":"{self.entry.latin.replace('<b>', '').replace('</b>', '')}",
"root":"{self.entry.root}",
"cyrillic":"{self.entry.cyrillic}",
"ipa":"{self.entry.ipa}",
"jacobson":"{self.entry.coded_cyrillic}",
"pos":"{self.entry.part_of_speech}",
"gloss":{gloss_string}
"notes":{note_string}
"examples":{example_string}
"source":"{self.entry.source if self.entry.source != '' else "Badten et al, 2001"}",
"etymology":"{self.entry.etymology.replace('< ', '&lt; ')}",
"semantic_code":"{self.entry.semantic_code}",
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

    def phoneticize(self, word):
        result = tokenize(word)
        result = redouble(result)
        result = convert2ipa(result)
        result = tokens2string(result)
        return result

    def rootGen(self, word):
        #verbs
        if "-" in self.entry.latin:
            result = word
        #nouns: "kw"
        elif word[-2:] == "kw":
            result = word[:-2] + "w"
        #nouns: "qw"
        elif word[-2:] == "qw":
            result = word[:-2] + "ghw"
        #nouns: marked strong gh
        elif "*" in self.entry.latin:
            result = word[:-1] + "gh*"
        #nouns: all other gh - "qikmiq"
        elif word[-1] == "q":
            result = word[:-1] + "gh"
        #nouns: g - "sikik"
        elif word[-1] == "k":
            result = word[:-1] + "g"
        #noun:e-underlying - "aaggaatae" 
        elif word[-2:] == "ae":
            result = word[:-2] + "e"
        #vowel final roots: "repa"(N), "aafte"(V)
        elif word[-1] in ["a", "i", "u", "e"]:
            result = word
        #nouns: te
        elif word[-1] == "n":
            result = word[:-1] + "te"
        else:
            result = word
        return result

if __name__ == "__main__":

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print(f"Usage:\t{sys.argv[0]} lexicon.html (output.json)", file=sys.stderr, flush=True)
        sys.exit(0)

    else:
        dictionary = HtmlDictionary(filename=sys.argv[1])
        if len(sys.argv) == 2 or (len(sys.argv) == 3 and sys.argv[2] == '-'):
            for html_entry in dictionary:
                entry = Entry(html_entry)
                if len(entry.latin) > 0:
                    print(JsonEntry(entry))
        else:
            with open(sys.argv[2], 'wt') as json:
                for html_entry in dictionary:
                    entry = Entry(html_entry)
                    if len(entry.latin) > 0:
                        print(JsonEntry(entry), file=json)
