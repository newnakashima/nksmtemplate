import re
import unittest
import sys
import os
sys.path.append(os.getcwd())
import nksmtemplate
from io import StringIO
import textwrap
from nksm_errors import IfClauseError, NotBooleanError

class ParserTest(unittest.TestCase):

    def test_read_template(self):
        """Test of read_template()"""
        p = nksmtemplate.Parser()
        p.read_template('./test/templates/test.txt')
        self.assertEqual('this is test\n', p.template)

    def test_read_json(self):
        """Test of read_json()"""
        p = nksmtemplate.Parser()
        p.read_json('./test/json/var_test.json')
        expected = {
                'hoge': 'fuga',
                'piyo': 'piyopiyo',
                }
        self.assertEqual(expected, p.variables)

    def test_get_value(self):
        """Tests get_value()"""
        p = nksmtemplate.Parser()
        p.variables = {
            'key1': 'orange',
            'key2': {
                'apple': 'pen',
            }
        }
        expected = 'pen'
        actual = p.get_value('key2[\'apple\']')
        self.assertEqual(expected, actual)

    def test_parse_variable(self):
        """
        Test of parse_syntax. This method tests feature of
        printing variables.
        """
        p = nksmtemplate.Parser()
        p.read_template('./test/templates/test_variable.txt')
        p.tokenize()
        p.variables = {
            'hoge': 'unko',
            'fuga': 'clap',
            'test': 'テスト',
            'dic': {
                'one': 'value1',
            },
            'ary': [
                '一個目',
                '二個目',
            ]
        }
        expected = '''this is test2.
unko
value1

変数が２つ続いているときのテスト
unkoclap

文中に区切り無しで変数を使うときのテスト
これはテストです。

単なる配列のテスト
一個目
二個目'''
        self.assertEqual(expected, p.parse_syntax())

    def test_render(self):
        """Test of render()"""
        self.maxDiff = 2000
        tmp_buffer = StringIO()
        sys.stdout = tmp_buffer
        p = nksmtemplate.Parser()
        hoge = {
                'hoge': 'これは非常に長い文字列を格納するための変数であり、非常に長い値を持つことにその特色があると言っても過言ではないというのが現時点における私の見解であるとともに、これを機会に周知しておかねばならぬと常日頃考えているところのものの懸案事項であることは間違いないのであるが、このことが世間一般にほとんど認知されておらず、問題とも認識されていないどころか、この問題の存在そのものが社会から抹殺され忘却されきってしまおうとしているのは本当に残念極まりないことであると世情を憂うことでしかわびしい余生を過ごすすべを知らぬつまらぬ男の嘆きを演じているのがこの私の現状なのである。悲しい。',
                }
        p.variables = hoge
        p.read_template('./test/templates/test2.txt')
        expected = '''this is test2.
{hoge}
'''.format(hoge=hoge['hoge'])
        p.render()
        sys.stdout = sys.__stdout__
        self.assertEqual(expected, tmp_buffer.getvalue())

    def test_parse_if(self):
        """
        Test of parse_syntax.
        This method tests the feature of 'if' keyword.
        """
        p = nksmtemplate.Parser()
        p.variables = {
            'test': True,
            'test2': False,
        }
        p.tokens = [
            {
                'value': 'ふふふふ\n',
                'type': 'text',
                'if_level': 0,
                'for_level': 0,
            }, {
                'value': 'if test:',
                'type': 'if_condition',
                'indent': '',
                'if_level': 1,
                'for_level': 0,
            }, {
                'value': '\nほんわか\n',
                'type': 'text',
                'if_level': 1,
                'for_level': 0,
            }, {
                'value': 'if test2:',
                'type': 'if_condition',
                'indent': '',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': '\n        出ないはず\n',
                'type': 'text',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': '\n終わったあと\n',
                'type': 'text',
                'if_level': 0,
                'for_level': 0,
            }
        ]
        expected = 'ふふふふ\nほんわか\n終わったあと\n'
        self.assertEqual(expected, p.parse_syntax())

    def test_tokenize(self):
        """
        Tests tokenize().
        """
        p = nksmtemplate.Parser()
        p.read_template('./test/templates/tokenize_test.txt')
        p.tokenize()
        expected = [
                {
                    'value': 'this is ',
                    'type': 'text',
                    'if_level': 0,
                    'for_level': 0 },
                {
                    'value': r'\test',
                    'type': 'variable',
                    'if_level': 0,
                    'for_level': 0 },
                {
                    'value': '\n',
                    'type': 'text',
                    'if_level': 0,
                    'for_level': 0 },
                {
                    'value': 'if hoge:',
                    'type': 'if_condition',
                    'indent': '',
                    'if_level': 1,
                    'for_level': 0 },
                {
                    'value': '\n    ',
                    'type': 'text',
                    'if_level': 1,
                    'for_level': 0 },
                {
                    'value': r'\fuga',
                    'type': 'variable',
                    'if_level': 1,
                    'for_level': 0 },
                {
                    'value': '\n    ',
                    'type': 'text',
                    'if_level': 1,
                    'for_level': 0 },
                {
                    'value': 'if hoge2:',
                    'type': 'if_condition',
                    'indent': '',
                    'if_level': 2,
                    'for_level': 0 },
                {
                    'value': '\n        ',
                    'type': 'text',
                    'if_level': 2,
                    'for_level': 0 },
                {
                    'value': r'\piyo',
                    'type': 'variable',
                    'if_level': 2,
                    'for_level': 0 },
                ]
        for i in range(len(expected)):
            self.assertEqual(expected[i]['value'], p.tokens[i]['value'])
            self.assertEqual(expected[i]['type'], p.tokens[i]['type'])
            if 'indent' in expected[i]:
                self.assertEqual(expected[i]['indent'], p.tokens[i]['indent'])
            self.assertEqual(expected[i]['if_level'], p.tokens[i]['if_level'])
            self.assertEqual(expected[i]['for_level'], p.tokens[i]['for_level'])

if __name__ == '__main__':
    unittest.main()
