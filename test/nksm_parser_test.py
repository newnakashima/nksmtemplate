import re
import unittest
import sys
import os
sys.path.append(os.getcwd())
import nksm_parser
from io import StringIO
import textwrap

class ParserTest(unittest.TestCase):

    def test_read_template(self):
        p = nksm_parser.Parser()
        p.read_template('./test/test.txt')
        self.assertEqual('this is test\n', p.template)

    def test_read_json(self):
        p = nksm_parser.Parser()
        p.read_json('./test/var_test.json')
        expected = {
                'hoge': 'fuga',
                'piyo': 'piyopiyo',
                }
        self.assertEqual(expected, p.variables)

    def test_set_variables(self):
        p = nksm_parser.Parser()
        variables = {
                'hoge': 'fuga',
                'piyo': 'piyopiyo',
                }
        p.set_variables(variables)
        self.assertEqual(variables, p.variables)

    def test_parse_variable(self):
        p = nksm_parser.Parser()
        p.variables = {
                'test': 'fuga',
                }
        p.text = '''this
is
{{ test }}
'''
        expected = '''this
is
fuga
'''
        self.assertEqual(expected, p.parse_variable())

    def test_render(self):
        self.maxDiff = 2000
        tmp_buffer = StringIO()
        sys.stdout = tmp_buffer
        p = nksm_parser.Parser()
        hoge = {
                'hoge': 'これは非常に長い文字列を格納するための変数であり、非常に長い値を持つことにその特色があると言っても過言ではないというのが現時点における私の見解であるとともに、これを機会に周知しておかねばならぬと常日頃考えているところのものの懸案事項であることは間違いないのであるが、このことが世間一般にほとんど認知されておらず、問題とも認識されていないどころか、この問題の存在そのものが社会から抹殺され忘却されきってしまおうとしているのは本当に残念極まりないことであると世情を憂うことでしかわびしい余生を過ごすすべを知らぬつまらぬ男の嘆きを演じているのがこの私の現状なのである。悲しい。',
                }
        p.variables = hoge
        p.read_template('./test/test2.txt')
        expected = '''this is test2.
{hoge}
'''.format(hoge=hoge['hoge'])
        p.render()
        sys.stdout = sys.__stdout__
        self.assertEqual(expected, tmp_buffer.getvalue())

    def test_parse_if(self):
        p = nksm_parser.Parser()
        hoge = {
                'hoge': True,
                'nest1': True,
                'nest2': False,
                }
        p.variables = hoge
        p.read_template('./test/if_test.txt')
        expected = textwrap.dedent('''
            これはテストです。
            hogeのときだけここが出力されます。
            nest1のときだけここが出力されます。
            ここは共通で出力されます。
            hogeはTrueでした。
            nest1はTrueでした。
            nest2はFalseでした。
            ''').strip() + "\n"
        p.parse_if()
        self.assertEqual(expected, p.parse_variable())
        hoge = {
                'hoge': True,
                'nest1': True,
                'nest2': True,
                }
        p.variables = hoge
        expected = textwrap.dedent('''
            これはテストです。
            hogeのときだけここが出力されます。
            nest1のときだけここが出力されます。
            nest2のときだけここが出力されます。
            ここは共通で出力されます。
            hogeはTrueでした。
            nest1はTrueでした。
            nest2はTrueでした。
            ''').strip() + "\n"
        p.parse_if()
        self.assertEqual(expected, p.parse_variable())

if __name__ == '__main__':
    unittest.main()
