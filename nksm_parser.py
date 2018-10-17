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
        out = ''
        ignore_level = -1
        for t in tokens:
            if t['if_level'] < ignore_level:
                ignore_level = -1
            if ignore_level != -1 and t['if_level'] >= ignore_level:
                # if条件がFalseの範囲は出力しない
                continue
            if t['type'] == 'text':
                m = re.match('\n?\s*(.*)', t['value'], re.M|re.S)
                out += m.group(1)
            elif t['type'] == 'if_condition':
                m = re.match('\s*if\s*(\w+)\s*', t['value'])
                if m == None:
                    raise IfClauseError()
                if not self.variables[m.group(1)]:
                    ignore_level = t['if_level']
            elif t['type'] == 'if_close':
                ignore_level = -1
        return out

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
        self.tokenize()
        self.parse_if()
        # text = self.parse_variable()
        print(text, end='')

    def run(self):
        self.read_template(sys.argv[1])
        self.read_json(sys.argv[2])
        self.render()

if __name__ == '__main__':
    parser = Parser()
    parser.run()

