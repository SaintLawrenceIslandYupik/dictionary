# St. Lawrence Island Yupik Dictionary

This repository hosts files and conversion scripts related to the <i>St. Lawrence Island / Siberian Yupik Eskimo Dictionary</i> compiled by Linda Womkon Badten (Aghnaghaghpik), Vera Oovi Keneshiro (Uqiitlek), Marie Oovi (Uvegtu), and Christopher Koonooka (Petuwaq); edited by Steven A. Jacobson; and published by the Alaska Native Language Center at the University of Alaska Fairbanks in 2008.

## Code

The [code](code) directory contains the following files:
* [code/html2xml.py](html2xml.py)

This Python script requires Python 3.7 or later and the [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) Python library, which can be installed in a local virtual environment as follows:

```
python3.7 -m venv venv
source venv/bin/activate
pip3 install beautifulsoup4
deactivate
```

The code can then be run as follows:

```
source venv/bin/activate
./code/html2xml.py data/foo.html
deactivate
```

Where `base` or `postbase` is substituted for `foo` as appropriate.

This code is responsible for cleaning up the formatting tags and whitespace in the original html file, and creating the XML files. The idea is that this script should contain all of the tweaks and hacks necessary to handle any oddities in the original source files. The original source files themselves should not be edited.


## Exported source files

The [data](data) directory contains the following files that were extracted from the original **FileMaker Pro** source files:
* [data/bases.rtf](bases.rtf)
* [data/bases.html](bases.html)
* [data/postbases.rtf](postbases.rtf)
* [data/postbases.html](postbases.html)

These files should not be edited.


#### RTF generation procedure

The RTF files were produced using the following procedure:
1. The relevant **Filemaker Pro** file was opened.
2. Within **Filemaker Pro**, the *Script Workspace* was opened, and a new script was creating. The scripting command *Copy All Records/Requests* was added to the file, and the script was saved and then run.
3. At this point, the macOS clipboard contained the contents of the **Filemaker Pro** file in rich text format (RTF).
4. The macOS application **TextEdit** was opened, and a new document was created. The contents of the clipboard were pasted into the new document, which was then saved.

Each line in the resulting RTF file contains one dictionary entry from the **Filemaker Pro** file. The fields within each line are delineated with a tab character.


#### HTML generation procedure

The HTML files were produced using the following procedure:
1. The relevant **Filemaker Pro** file was opened.
2. Within **Filemaker Pro**, the *Script Workspace* was opened, and a new script was creating. The scripting command *Copy All Records/Requests* was added to the file, and the script was saved and then run.
3. At this point, the macOS clipboard contained the contents of the **Filemaker Pro** file in rich text format (RTF).
4. The macOS application **Terminal** was opened, and the command `pbpaste -Prefer rtf | textutil -stdin -convert html -output foo.html` was run, where `base` or `postbase` was substituted for `foo` as appropriate.

#### Raw XML generation procedure

The raw XML files were produced using the following procedure:
1. The relevant **Filemaker Pro** file was opened.
2. Within **Filemaker Pro**, *Export Records...* was selected from the *File...* menu, and XML was selected as the export type.
3. *FMPXMLRESULT* was selected as the *Grammar* type, and no XSL style sheet was used.
4. In *Specify Field Order for Export*, all fields were selected. The fields were listed in the *Field export order* in case-insensitive alphabetical order.
5. The file was exported.

#### XLSX generation procedure

The XLSX files were produced using the following procedure:
1. The relevant **Filemaker Pro** file was opened.
2. Within **Filemaker Pro**, the *Save/Send Records As... Excel* command was run.

Each line in the resulting XLSX file contains one dictionary entry from the **Filemaker Pro** file. NOTE: A few fields contain the newline character.

#### ODS generation procedure

The ODS files were produced using the following procedure:
1. The relevant **Filemaker Pro** file was opened.
2. Within **Filemaker Pro**, the *Save/Send Records As... Excel* command was run.
3. The newly created XLSX file was open using **Microsoft Excel** for Mac version 16.38.
4. Within **Microsoft Excel**, the **Save As...** command was run, selecting **OpenDocument Spreadsheet (.ods)** as the file format.

Each line in the resulting ODS file contains one dictionary entry from the **Filemaker Pro** file. NOTE: A few fields contain the newline character.


#### TSV generation procedure

The TSV files were produced using the following procedure:
1. The relevant **Filemaker Pro** file was opened.
2. Within **Filemaker Pro**, the *Save/Send Records As... Excel* command was run.
3. The newly created XLSX file was open using **Microsoft Excel** for Mac version 16.38.
4. Within **Microsoft Excel**, the **Save As...** command was run, selecting **OpenDocument Spreadsheet (.ods)** as the file format.
5. The newly created ODS file was opened using **LibreOffice** version 6.0.6.2
6. Within **LibreOffice**, the **Find & Replace** command was chosen.
7. Within the **Find & Replace** dialog box, with **Regular expressions** checked, where the **Find** value was \n and the **Replace** value was four space characters, **Replace All** was run.
8. Within **LibreOffice**, the **Save As...** command was run, selecting **Text CSV (.csv)** as the file type. The **Edit Filter Settings** box was checked. During export, the character set was **Unicode (UTF-8)**, the Field delimiter was **{Tab}**, the String delimiter was set to the empty string, and the remaining checkboxes were unchecked.

Each line in the resulting TSV file contains one dictionary entry from the **Filemaker Pro** file. NOTE: No fields in this file contain the newline character.



## License

**This resource is part of the linguistic and cultural heritage of the St. Lawrence Island Yupik people. By accessing this resource, you agree to treat this resource, the St. Lawrence Island Yupik language, the St. Lawrence Island Yupik culture, and the St. Lawrence Island Yupik people with dignity and respect. If you do not agree to these conditions, you may not access this resource and you may not make copies of this resource.**

If you agree to these conditions, you may access this resource under the terms of the Creative Commons Attribution No-Commercial 4.0 license (https://creativecommons.org/licenses/by-nc/4.0/).
