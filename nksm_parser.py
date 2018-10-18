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

    def get_value(self, query):
        """
        Get value for the query.
        """
        m = re.match('\s*([^\[\]]*?)(\[.*\])', query)
        if m != None:
            return eval('self.variables[m[1]]' + m[2])
        else:
            return self.variables[query.strip()]

    def parse_syntax(self):
        """
        Parse nksmtemplate's syntax.
        'if' and variables.
        """
        out = ''
        ignore_level = -1
        raw_flag = False
        indent = ['']
        for t in self.tokens:
            if t['if_level'] < ignore_level:
                ignore_level = -1
            if ignore_level != -1 and t['if_level'] >= ignore_level:
                # if条件がFalseの範囲は出力しない
                continue
            if t['type'] == 'text':
                if len(t['value']) > 2:
                    m = re.match('\n?(\s*(.*))', t['value'], re.M|re.S)
                    if raw_flag:
                        out += m.group(1)
                    else:
                        out += indent[-1] + m.group(2)
                else:
                    out += indent[-1] + t['value']
            elif t['type'] == 'variable':
                out += self.get_value(t['value'])
            elif t['type'] == 'if_condition':
                m = re.match('\s*(r?if)(\s*)(\w+)\s*', t['value'])
                if m == None:
                    raise IfClauseError()
                raw_flag = m.group(1) == 'rif'
                indent.append(t['indent'])
                if (
                        self.get_value(m.group(3)) != True and
                        self.get_value(m.group(3)) != False
                    ):
                    raise NotBooleanError()
                if not self.variables[m.group(3)]:
                    ignore_level = t['if_level']
            elif t['type'] == 'if_close':
                ignore_level = -1
                saved_indent = ''
                raw_flag = False
                indent.pop()
        if self.tokens[-1]['if_level'] != 0:
            raise IfClauseError()
        return out

    def parse_variable(self, token):
        return self.variables[token.strip()]

    def tokenize(self):
        reg = re.compile('{{(.+)}}')
        ind_reg = re.compile('^\n*([ \t]*)')
        v_reg = re.compile('^\s*\w+\s*$')
        if_reg = re.compile('^\s*(r?if)\s+(.+)\s*$')
        fi_reg = re.compile('^\s*fi\s*$')
        if_level = 0
        for_level = 0
        prev = 0
        self.tokens = []
        indent = ''
        for r in reg.finditer(self.template):
            pre_value = self.template[prev:r.start()]
            if pre_value == '':
                continue
            m = ind_reg.match(pre_value)
            indent = m.group(1)
            self.tokens.append({
                'value':     pre_value,
                'type':      'text',
                'if_level':  if_level,
                'for_level': for_level
            })

            token = {}
            token['value'] = r.group(1)
            if_m = if_reg.match(token['value'])
            if if_m != None:
                token['type'] = 'if_condition'
                token['indent'] = indent
                if_level += 1
            elif fi_reg.match(token['value']) != None:
                token['type'] = 'if_close'
            else:
                token['type'] = 'variable'
            token['if_level'] = if_level
            token['for_level'] = for_level
            self.tokens.append(token)
            if token['type'] == 'if_close':
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

