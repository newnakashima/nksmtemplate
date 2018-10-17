import re
import unittest
import sys
import os
sys.path.append(os.getcwd())
import nksm_parser
from io import StringIO
import textwrap
from nksm_errors import IfClauseError, NotBooleanError

class ParserTest(unittest.TestCase):

    def test_read_template(self):
        p = nksm_parser.Parser()
        p.read_template('./test/templates/test.txt')
        self.assertEqual('this is test\n', p.template)

    def test_read_json(self):
        p = nksm_parser.Parser()
        p.read_json('./test/json/var_test.json')
        expected = {
                'hoge': 'fuga',
                'piyo': 'piyopiyo',
                }
        self.assertEqual(expected, p.variables)

    def test_parse_variable(self):
        p = nksm_parser.Parser()
        p.read_template('./test/templates/test2.txt')
        p.tokenize()
        p.variables = {
            'hoge': 'unko',
        }
        expected = textwrap.dedent('''
        this is test2.
        unko
        ''').strip()
        self.assertEqual(expected, p.parse_syntax())

    def test_render(self):
        self.maxDiff = 2000
        tmp_buffer = StringIO()
        sys.stdout = tmp_buffer
        p = nksm_parser.Parser()
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
        p = nksm_parser.Parser()
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
                'value': 'if test',
                'type': 'if_condition',
                'indent': '',
                'if_level': 1,
                'for_level': 0,
            }, {
                'value': '\n    ほんわか\n',
                'type': 'text',
                'if_level': 1,
                'for_level': 0,
            }, {
                'value': 'if test2',
                'type': 'if_condition',
                'indent': '    ',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': '\n        出ないはず\n',
                'type': 'text',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': 'fi',
                'type': 'if_close',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': 'fi',
                'type': 'if_close',
                'if_level': 0,
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

    def test_parse_if_indent(self):
        p = nksm_parser.Parser()
        p.variables = {
            'test': True,
            'test2': True,
        }
        p.tokens = [
            {
                'value': 'ふふふふ\n',
                'type': 'text',
                'if_level': 0,
                'for_level': 0,
            }, {
                'value': 'rif test',
                'type': 'if_condition',
                'indent': '',
                'if_level': 1,
                'for_level': 0,
            }, {
                'value': '\n    ほんわか\n',
                'type': 'text',
                'if_level': 1,
                'for_level': 0,
            }, {
                'value': 'if test2',
                'type': 'if_condition',
                'indent': '    ',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': '\n        出るはず\n',
                'type': 'text',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': 'fi',
                'type': 'if_close',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': 'fi',
                'type': 'if_close',
                'if_level': 0,
                'for_level': 0,
            }, {
                'value': '\n終わったあと\n',
                'type': 'text',
                'if_level': 0,
                'for_level': 0,
            }
        ]
        expected = 'ふふふふ\n    ほんわか\n    出るはず\n終わったあと\n'
        self.assertEqual(expected, p.parse_syntax())

    def test_parse_rif(self):
        p = nksm_parser.Parser()
        p.variables = {
            'test': True,
            'test2': True,
        }
        p.tokens = [
            {
                'value': 'ふふふふ\n',
                'type': 'text',
                'if_level': 0,
                'for_level': 0,
            }, {
                'value': 'rif test',
                'type': 'if_condition',
                'indent': '',
                'if_level': 1,
                'for_level': 0,
            }, {
                'value': '\n    ほんわか\n',
                'type': 'text',
                'if_level': 1,
                'for_level': 0,
            }, {
                'value': 'rif test2',
                'type': 'if_condition',
                'indent': '    ',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': '\n        出るはず\n',
                'type': 'text',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': 'fi',
                'type': 'if_close',
                'if_level': 2,
                'for_level': 0,
            }, {
                'value': 'fi',
                'type': 'if_close',
                'if_level': 0,
                'for_level': 0,
            }, {
                'value': '\n終わったあと\n',
                'type': 'text',
                'if_level': 0,
                'for_level': 0,
            }
        ]
        expected = '''ふふふふ
    ほんわか
        出るはず
終わったあと
'''
        self.assertEqual(expected, p.parse_syntax())

    def test_if_error(self):
        p = nksm_parser.Parser()
        p.read_template('./test/templates/if_error.txt')
        p.tokenize()
        p.variables = {
                'cond1': True,
                'cond2': True,
                }
        with self.assertRaises(IfClauseError):
            p.parse_syntax()

    def test_if_not_boolean(self):
        p = nksm_parser.Parser()
        p.read_template('./test/templates/if_error.txt')
        p.tokenize()
        p.variables = {
                'cond1': True,
                'cond2': 'fuckyou'
                }
        with self.assertRaises(NotBooleanError):
            p.parse_syntax()

    def test_tokenize(self):
        p = nksm_parser.Parser()
        p.read_template('./test/templates/tokenize_test.txt')
        p.tokenize()
        expected = [
                {
                    'value': 'this is ',
                    'type': 'text',
                    'if_level': 0,
                    'for_level': 0 },
                {
                    'value': 'test',
                    'type': 'variable',
                    'if_level': 0,
                    'for_level': 0 },
                {
                    'value': '\n',
                    'type': 'text',
                    'if_level': 0,
                    'for_level': 0 },
                {
                    'value': 'if hoge',
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
                    'value': 'fuga',
                    'type': 'variable',
                    'if_level': 1,
                    'for_level': 0 },
                {
                    'value': '\n    ',
                    'type': 'text',
                    'if_level': 1,
                    'for_level': 0 },
                {
                    'value': 'rif hoge2',
                    'type': 'if_condition',
                    'indent': '    ',
                    'if_level': 2,
                    'for_level': 0 },
                {
                    'value': '\n        ',
                    'type': 'text',
                    'if_level': 2,
                    'for_level': 0 },
                {
                    'value': 'piyo',
                    'type': 'variable',
                    'if_level': 2,
                    'for_level': 0 },
                {
                    'value': '\n    ',
                    'type': 'text',
                    'if_level': 2,
                    'for_level': 0 },
                {
                    'value': 'fi',
                    'type': 'if_close',
                    'if_level': 2,
                    'for_level': 0, },
                {
                    'value': '\n',
                    'type':  'text',
                    'if_level': 1,
                    'for_level': 0 },
                {
                    'value': 'fi',
                    'type': 'if_close',
                    'if_level': 1,
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
