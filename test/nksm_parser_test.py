import re
import unittest
import sys
import os
import nksm_parser

class ParserTest(unittest.TestCase):

    def test_read_template(self):
        p = nksm_parser.Parser()
        p.read_template('./test/test.txt')
        self.assertEqual('this is test\n', p.text)

    def test_read_json(self):
        p = nksm_parser.Parser()
        p.read_json('./test/var_test.json')
        expected = {
                'hoge': 'fuga',
                'piyo': 'piyopiyo'
                }
        self.assertEqual(expected, p.variables)

    def test_set_variables(self):
        p = nksm_parser.Parser()
        variables = {
                'hoge': 'fuga',
                'piyo': 'piyopiyo'
                }
        p.set_variables(variables)
        self.assertEqual(variables, p.variables)

    def test_parse_variable(self):
        p = nksm_parser.Parser()
        p.variables = {
            'test': 'fuga'
        }
        p.text = '''this
is
{{ test }}'''
        expected = '''this
is
fuga'''
        self.assertEqual(expected, p.parse_variable())

if __name__ == '__main__':
    unittest.main()
