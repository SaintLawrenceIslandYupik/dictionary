#!/usr/bin/env python3

import unittest

from html2xml import HtmlDictionary, HtmlEntry, Entry


class TestZiruliinHtmlEntry(unittest.TestCase):

    def setUp(self):
        self.entry: HtmlEntry = HtmlDictionary("ziruliin.html")[0]

    def test_length(self):
        self.assertEqual(28, len(self.entry))

    def test_latin(self):
        self.assertEqual("ziruliin", self.entry[0])

    def test_cyrillic_code(self):
        self.assertEqual("pbhek7y", self.entry[1])

    def test_english_gloss1(self):
        self.assertEqual("lube oil", self.entry[2])

    def test_russian_gloss1(self):
        self.assertEqual("", self.entry[3])

    def test_examples(self):
        self.assertEqual("", self.entry[4])

    def test_english_gloss2(self):
        self.assertEqual("", self.entry[5])

    def test_english_gloss3(self):
        self.assertEqual("", self.entry[6])

    def test_russian_gloss2(self):
        self.assertEqual("", self.entry[7])

    def test_russian_gloss3(self):
        self.assertEqual("", self.entry[8])

    def test_csy_word_cyr_num_eq(self):
        self.assertEqual("", self.entry[9])

    def test_russian_gloss_1_num_eq(self):
        self.assertEqual("", self.entry[10])

    def test_russian_gloss_2_num_eq(self):
        self.assertEqual("", self.entry[11])

    def test_russian_gloss_3_num_eq(self):
        self.assertEqual("", self.entry[12])

    def test_queries_etc(self):
        self.assertEqual("", self.entry[13])

    def test_english_gloss4(self):
        self.assertEqual("", self.entry[14])

    def test_russian_gloss4(self):
        self.assertEqual("", self.entry[15])

    def test_russian_gloss3_num_eq(self):
        self.assertEqual("", self.entry[16])

    def test_english_gloss_combined(self):
        self.assertEqual("lube oil", self.entry[17])

    def test_russian_gloss_combined(self):
        self.assertEqual("", self.entry[18])

    def test_pe_py_source(self):
        self.assertEqual("from English “Zeroline” (a brandname)", self.entry[19])

    def test_symantic_code(self):
        self.assertEqual("SLI", self.entry[20])

    def test_sib_source_code(self):
        self.assertEqual("from SLI Curriculum resource manual", self.entry[21])

    def test_derived_forms(self):
        self.assertEqual("", self.entry[22])

    def test_postbase_head_form(self):
        self.assertEqual("", self.entry[23])

    def test_postbase_alphabetization_form(self):
        self.assertEqual("", self.entry[24])

    def test_alphabetization_field_a(self):
        self.assertEqual("yz", self.entry[25])

    def test_alphabetization_field_b(self):
        self.assertEqual("zirulxn", self.entry[26])

    def test_cyrillic(self):
        self.assertEqual("зирулӣн", self.entry[27])


class TestZiruliinEntry(unittest.TestCase):

    def setUp(self):
        self.entry: Entry = Entry(HtmlDictionary("ziruliin.html")[0])

    def test_latin(self):
        self.assertEqual("ziruliin", self.entry.latin)

    def test_cyrillic(self):
        self.assertEqual("зирулӣн", self.entry.cyrillic)

    def test_cyrillic_code(self):
        self.assertEqual("pbhek7y", self.entry.coded_cyrillic)

    def test_raw_examples(self):
        self.assertEqual("", self.entry.raw_examples)

    def test_examples(self):
        self.assertEqual(0, len(self.entry.examples))

    def test_combined_english_gloss(self):
        self.assertEqual(1, len(self.entry.combined_english_gloss))
        self.assertEqual("lube oil", self.entry.combined_english_gloss[0])

    def test_part_of_speech(self):
        self.assertEqual("noun", self.entry.part_of_speech)

    def test_etymology(self):
        self.assertEqual("from English “Zeroline” (a brandname)", self.entry.etymology)

    def test_source(self):
        self.assertEqual("from SLI Curriculum resource manual", self.entry.source)


if __name__ == '__main__':
    unittest.main()
