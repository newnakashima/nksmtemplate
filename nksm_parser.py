import re
import sys
import os
sys.path.append(os.getcwd() + '/error')
from nksm_errors import IfClauseError, NotBooleanError
import json
class Parser:
    """The template parser."""

    # Original template.
    template = ''

    # Text that has been replaced with variables.
    text = ''

    # Variables for template.
    variables = {}

    # Template splitted by token.
    tokens = []

    # Tokens replaced by tempalte syntax.
    replaced = []

    def read_template(self, path):
        data = ''
        with open(path, 'r') as f:
            data += f.read()
        self.template = data

    def read_json(self, path):
        with open(path, 'r') as f:
            self.variables = json.load(f)

    def parse_syntax(self):
        out = ''
        ignore_level = -1
        raw_flag = False
        for t in self.tokens:
            if t['if_level'] < ignore_level:
                ignore_level = -1
            if ignore_level != -1 and t['if_level'] >= ignore_level:
                # if条件がFalseの範囲は出力しない
                continue
            if t['type'] == 'text':
                m = re.match('\n?(\s*(.*))', t['value'], re.M|re.S)
                if raw_flag:
                    out += m.group(1)
                else:
                    out += m.group(2)
            elif t['type'] == 'variable':
                out += self.variables[t['value'].strip()]
            elif t['type'] == 'if_condition':
                m = re.match('\s*(r?if)(\s*)(\w+)\s*', t['value'])
                if m == None:
                    raise IfClauseError()
                if m.group(1) == 'rif':
                    raw_flag = True
                if (
                        self.variables[m.group(3)] != True and
                        self.variables[m.group(3)] != False
                    ):
                    raise NotBooleanError()
                if not self.variables[m.group(3)]:
                    ignore_level = t['if_level']
            elif t['type'] == 'if_close':
                ignore_level = -1
                saved_indent = ''
                raw_flag = False
        if self.tokens[-1]['if_level'] != 0:
            raise IfClauseError()
        return out

    def parse_variable(self, token):
        return self.variables[token.strip()]

    def tokenize(self):
        reg = re.compile('{{(.+)}}')
        v_reg = re.compile('^\s*\w+\s*$')
        if_reg = re.compile('^\s*(r?if)\s+(.+)\s*$')
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
            if_m = if_reg.match(t_value)
            if if_m != None:
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
        if self.template[prev:] != '':
            # 最後に追加すべき文字列があれば追加
            self.tokens.append({
                'value': self.template[prev:],
                'type': 'text',
                'if_level': if_level,
                'for_level': for_level,
            })

    def render(self):
        self.tokenize()
        text = self.parse_syntax()
        print(text)

    def run(self):
        self.read_template(sys.argv[1])
        self.read_json(sys.argv[2])
        self.render()

if __name__ == '__main__':
    parser = Parser()
    parser.run()

