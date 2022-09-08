import os.path
import unittest

from core.anki import Anki
from md2anki import md2anki


class TestMdParser(unittest.TestCase):
    os.getcwd()
    folder = os.path.join(os.getcwd() + '/test')
    note_sep = '\n\n%\n\n'
    module_sep = '\n\n----\n\n'
    md2anki = md2anki(folder, note_sep, module_sep, 'pic', run_on_init=False)

    def test_img_parser(self):
        parser = TestMdParser.md2anki.parser
        self.assertEqual(parser('<img src=pic/test.png width=50% />'), '<img src=test.png width=50%>')
        self.assertEqual(parser('<img src=pic%2Ftest.png width=50%>'), '<img src=test.png width=50%>')

    def test_get_media_files_names(self):
        anki = Anki()
        filenames = anki.get_media_files_names('向前差分格式.png')
        self.assertEqual(filenames, ['向前差分格式.png'])

    def test_exsits_meida(self):
        anki = Anki()
        self.assertTrue(anki.exists_media('向前差分格式.png'))
        self.assertFalse(anki.exists_media('test.png'))

    def test_md2anki(self):
        TestMdParser.md2anki.to_anki(TestMdParser.folder)