#!/usr/bin/env python3

import unittest

from html2xml import HtmlDictionary, HtmlEntry, Entry


class TestKatamqunHtmlEntry(unittest.TestCase):

    def setUp(self):
        self.entry: HtmlEntry = HtmlDictionary("katamqun.html")[0]

    def test_length(self):
        self.assertEqual(len(self.entry), 28)

    def test_latin(self):
        self.assertEqual(self.entry[0], "katamqun")

    def test_cyrillic_code(self):
        self.assertEqual(self.entry[1], "rfnfv2ey")

    def test_english_gloss1(self):
        self.assertEqual(self.entry[2], "barely")

    def test_russian_gloss1(self):
        self.assertEqual(self.entry[3], "")

    def test_examples(self):
        self.assertEqual(self.entry[4], """<i>particle;<span class="Apple-converted-space">  </span></i>katamqun taawa qayuusim imaghhaa siipsimalghii pagunghaq saghnakaq ‘there are only a cup left of the berries that were picked’; Maaten ilangani nunalgutangit qamaglluteng Quyillegqaasimalghiit. <i>Katamqun</i> yaywaalingiighhaak<span class="Apple-converted-space">  </span>unegsimalghiik. ‘Then one time their fellow villagers all went off with the Chukchis. <i>Only</i> the two little orpans remained behind.’ (UNGAZ. UNGIP. 61)""")

    def test_english_gloss2(self):
        self.assertEqual(self.entry[5], "only")

    def test_english_gloss3(self):
        self.assertEqual(self.entry[6], "")

    def test_russian_gloss2(self):
        self.assertEqual(self.entry[7], "")

    def test_russian_gloss3(self):
        self.assertEqual(self.entry[8], "")

    def test_csy_word_cyr_num_eq(self):
        self.assertEqual(self.entry[9], "")

    def test_russian_gloss_1_num_eq(self):
        self.assertEqual(self.entry[10], "")

    def test_russian_gloss_2_num_eq(self):
        self.assertEqual(self.entry[11], "")

    def test_russian_gloss_3_num_eq(self):
        self.assertEqual(self.entry[12], "")

    def test_queries_etc(self):
        self.assertEqual(self.entry[13], "")

    def test_english_gloss4(self):
        self.assertEqual(self.entry[14], "")

    def test_russian_gloss4(self):
        self.assertEqual(self.entry[15], "")

    def test_russian_gloss3_num_eq(self):
        self.assertEqual(self.entry[16], "")

    def test_english_gloss_combined(self):
        self.assertEqual(self.entry[17], "barely; only")

    def test_russian_gloss_combined(self):
        self.assertEqual(self.entry[18], "")

    def test_pe_py_source(self):
        self.assertEqual(self.entry[19], "< katam=qun")

    def test_symantic_code(self):
        self.assertEqual(self.entry[20], "")

    def test_sib_source_code(self):
        self.assertEqual(self.entry[21], "")

    def test_derived_forms(self):
        self.assertEqual(self.entry[22], "")

    def test_postbase_head_form(self):
        self.assertEqual(self.entry[23], "")

    def test_postbase_alphabetization_form(self):
        self.assertEqual(self.entry[24], "")

    def test_alphabetization_field_a(self):
        self.assertEqual(self.entry[25], "katamqun")

    def test_alphabetization_field_b(self):
        self.assertEqual(self.entry[26], "katamqun")

    def test_cyrillic(self):
        self.assertEqual(self.entry[27], "катамқун")


class TestKatamqunEntry(unittest.TestCase):

    def setUp(self):
        self.entry: Entry = Entry(HtmlDictionary("katamqun.html")[0])

    def test_latin(self):
        self.assertEqual(self.entry.latin, "katamqun")

    def test_cyrillic(self):
        self.assertEqual(self.entry.cyrillic, "катамқун")

    def test_cyrillic_code(self):
        self.assertEqual(self.entry.coded_cyrillic, "rfnfv2ey")

    def test_raw_examples(self):
        self.assertEqual(self.entry.raw_examples, """<i>particle</i>; katamqun taawa qayuusim imaghhaa siipsimalghii pagunghaq saghnakaq ‘there are only a cup left of the berries that were picked’; Maaten ilangani nunalgutangit qamaglluteng Quyillegqaasimalghiit. <i>Katamqun</i> yaywaalingiighhaak unegsimalghiik. ‘Then one time their fellow villagers all went off with the Chukchis. <i>Only</i> the two little orpans remained behind.’ (UNGAZ. UNGIP. 61)""")

    def test_examples(self):
        self.assertEqual(len(self.entry.examples), 2)
        self.assertEqual(self.entry.examples[0].yupik, """katamqun taawa qayuusim imaghhaa siipsimalghii pagunghaq saghnakaq""")
        self.assertEqual(self.entry.examples[0].english, """‘there are only a cup left of the berries that were picked’""")
        self.assertEqual(self.entry.examples[0].citation, "")
        self.assertEqual(self.entry.examples[1].yupik, """Maaten ilangani nunalgutangit qamaglluteng Quyillegqaasimalghiit. <i>Katamqun</i> yaywaalingiighhaak unegsimalghiik.""")
        self.assertEqual(self.entry.examples[1].english, """‘Then one time their fellow villagers all went off with the Chukchis. <i>Only</i> the two little orpans remained behind.’""")
        self.assertEqual(self.entry.examples[1].citation, """(UNGAZ. UNGIP. 61)""")

    def test_combined_english_gloss(self):
        self.assertEqual(len(self.entry.combined_english_gloss), 2)
        self.assertEqual(self.entry.combined_english_gloss[0], "barely")
        self.assertEqual(self.entry.combined_english_gloss[1], "only")

    def test_part_of_speech(self):
        self.assertEqual(self.entry.part_of_speech, """particle""")

    def test_source(self):
        self.assertEqual("", self.entry.source)

    def test_etymology(self):
        self.assertEqual("< katam=qun", self.entry.etymology)


if __name__ == '__main__':
    unittest.main()
