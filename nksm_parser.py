import re
import sys
import os
sys.path.append(os.getcwd() + '/error')
from nksm_errors import IfClauseError, NotBooleanError
import json
class Parser:
    """The template parser."""

    template = ''
    """This keeps original template."""

    text = ''
    """Text than has been replaced variables."""

    variables = {}
    """Variables for template."""

    tokens = []
    """Template splitted by token."""

    replaced = []
    """Tokens replaced by tempalte syntax."""

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

    def parse_if(self, tokens):
        for t in tokens:
            pass

        # lines = self.template.split("\n")
        # self.text = '\n'.join(self.__parse_if(lines))

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

    def iterate_token(self):
        v_flag = False
        result = ''
        v_reg = re.compile('^\s*\w+\s*$')
        if_reg = re.compile('^\s*if\s+(.+)\s*$')
        for t in self.tokens:
            if_m = if_reg(t)
            if t == '}}':
                v_flag = False
            elif v_flag:
                if v_reg.match(t) != None:
                    result += self.parse_variable(t)
            elif t == '{{':
                v_flag = True
            else:
                result += t
        return result

    def parse_variable(self, token):
        return self.variables[token.strip()]

    def tokenize(self):
        reg = re.compile('{{(.+)}}')
        v_reg = re.compile('^\s*\w+\s*$')
        if_reg = re.compile('^\s*if\s+(.+)\s*$')
        fi_reg = re.compile('^\s*fi\s*$')
        if_level = 0
        for_level = 0
        prev = 0
        self.tokens = []
        for r in reg.finditer(self.template):
            pre_value = self.template[prev:r.start()]
            if pre_value == '':
                continue
            self.tokens.append({
                'value':     pre_value,
                'type':      'text',
                'if_level':  if_level,
                'for_level': for_level
            })

            t_value = r.group(1)
            t_type = ''
            if if_reg.match(t_value) != None:
                t_type = 'if_condition'
                if_level += 1
            elif fi_reg.match(t_value) != None:
                t_type = 'if_close'
            else:
                t_type = 'variable'
            
            self.tokens.append({
                'value':     t_value,
                'type':      t_type,
                'if_level':  if_level,
                'for_level': for_level,
            })
            if t_type == 'if_close':
                if_level -= 1
            prev = r.end()
        self.tokens.append(self.template[prev:])

    def render(self):
        # self.tokenize()
        self.parse_if()
        text = self.parse_variable()
        print(text, end='')

    def run(self):
        self.read_template(sys.argv[1])
        self.tokenize()
        self.read_json(sys.argv[2])
        self.render()

if __name__ == '__main__':
    parser = Parser()
    parser.run()

