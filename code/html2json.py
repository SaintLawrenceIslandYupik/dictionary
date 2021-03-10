import logging
from typing import Dict, List
import sys

from html2xml import *


class JsonEntry:
  
  def __init__(self, entry: "Entry"):
    self.entry = entry
  
  def __str__(self):
    # TODO: Ben write code that turns this object into a nice JSON string
    #
    result = ""
    
    # Add in the other bits that JSON wants (curly braces, quotation marks, newlines, etc)
    result += entry.latin
    #result += entry.cyrillic
    
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
                        print(JsonEntry(entry), file=xml)
