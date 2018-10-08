import re
import sys
import os
sys.path.append(os.getcwd() + '/error')
from nksm_errors import IfClauseError, NotBooleanError
import json
class Parser:

    # テンプレートの原文を保持しておくメンバ
    template = ''

    # ifや変数をイジイジしたあとのテキストを保持しておく
    text = ''

    # テンプレートに渡す変数
    variables = {}

    def read_template(self, path):
        data = ''
        with open(path, 'r') as f:
            data += f.read()
        self.template = data

    def read_json(self, path):
        with open(path, 'r') as f:
            self.variables = json.load(f)

    def set_variables(self, variables):
        self.variables = variables;

    def parse_if(self):
        lines = self.template.split("\n")
        self.text = '\n'.join(self.__parse_if(lines))

    def __parse_if(self, lines):
        indent = ''
        ignore_flg = False
        inside_if = False
        raw_flg = False
        result_lines = []
        nested_lines = []
        if_count = 0
        ind_reg = re.compile('^(\s*)\S')
        if_reg = re.compile('^\s*{{\s*(r)?if\s*(\w+)\s*}}$')
        fi_reg = re.compile('^\s*{{\s*fi\s*}}$')
        for line in lines:
            if_matched = if_reg.match(line)
            fi_matched = fi_reg.match(line)
            if if_matched != None:
                if_count += 1
                ind_matched = ind_reg.match(line)
                if (ind_matched != None and not inside_if):
                    # トップレベルのif文行の場合
                    indent = ind_matched.group(1)
                    raw_flg = if_matched.group(1) != None
                if inside_if:
                    # ifブロック内にif文がある => ネスト
                    if not raw_flg:
                        # ネスト内のインデントは最初のif文行にそろえる
                        line = re.sub('^\s*', indent, line)
                    nested_lines.append(line)
                    continue
                inside_if = True
                # if文の行の場合は出力行に含めない
                # if if_matched.group(2) == 'cond2':
                #     print(if_matched.group(2))
                #     print(self.variables[if_matched.group(2)])
                if type(self.variables[if_matched.group(2)]) is not bool:
                    raise NotBooleanError
                if not self.variables[if_matched.group(2)]:
                    # ifの条件がFalseのときは無視フラグを立てる
                    ignore_flg = True
                continue
            if fi_matched != None:
                if_count -= 1
                if if_count > 0:
                    # if_countがまだ1以上 => ネスト
                    nested_lines.append(line)
                    if if_count == 1:
                        # if_countが1 => ネスト終了
                        result_lines.extend(self.__parse_if(nested_lines))
                    continue
                inside_if = False
                # if文から抜けるときは無視フラグ解除。出力行に含めない
                ignore_flg = False
                continue
            if ignore_flg:
                # if文の中かつ条件に一致しない場合は出力しない
                continue
            if if_count > 1:
                # ネスト内の普通の行
                nested_lines.append(line)
                continue
            if inside_if and not raw_flg and if_count == 1:
                # if文行のインデントを引き継ぐ
                line = re.sub('^\s*', indent, line)
            # それ以外の場合は普通に出力
            result_lines.append(line)
        if if_count != 0:
            # パース終了時にif_countが0じゃない => ifが全部閉じられてない
            raise IfClauseError('if clauses is not closed properly.')
        return result_lines

    def parse_variable(self):
        result_str = self.text
        dic = self.variables
        for key in dic:
            variable = re.compile('{{\s*' + key + '\s*}}')
            result_str = variable.sub(str(dic[key]), result_str)
        return result_str

    def render(self):
        self.parse_if()
        text = self.parse_variable()
        print(text, end='')

    def run(self):
        self.read_template(sys.argv[1])
        self.read_json(sys.argv[2])
        self.render()

if __name__ == '__main__':
    parser = Parser()
    parser.run()

