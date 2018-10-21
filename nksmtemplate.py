#!/usr/bin/env python
import re
import sys
import os
sys.path.append(os.getcwd() + '/error')
from nksm_errors import IfClauseError, NotBooleanError
import json
class Parser:
    """The template parser."""

    BLOCK_TOP = 0
    BLOCK_IF = 1
    BLOCK_FOR_LOOP = 2

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

    # Parameters for create tokens.
    if_level = 0
    for_level = 0
    block_stack = [BLOCK_TOP]

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
        query = re.sub(r'\\|\(|\)', '', query)
        m = re.match('([^\[\]]*?)(\[.*\])', query)
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
        post_if_for = False
        for t in self.tokens:
            if t['if_level'] < ignore_level:
                ignore_level = -1
            if ignore_level != -1 and t['if_level'] >= ignore_level:
                # Not output if condition is false.
                continue
            if t['type'] == 'text':
                if len(t['value']) > 2:
                    m = re.match('\n?(\s*(.*))', t['value'], re.M|re.S)
                    if raw_flag:
                        out += m[1]
                    elif post_if_for:
                        out += indent[-1] + m[2]
                        post_if_for = False
                    else:
                        out += indent[-1] + m[0]
                else:
                    out += indent[-1] + t['value']
            elif t['type'] == 'variable':
                out += self.get_value(t['value'])
            elif t['type'] == 'if_condition':
                post_if_for = True
                m = re.match('\s*(r?if)(\s*)(\w+)\s*', t['value'])
                if m == None:
                    raise IfClauseError()
                # TODO: on raw_flag here.
                # raw_flag = m.group(1) == 'rif'
                indent.append(t['indent'])
                if (
                        self.get_value(m.group(3)) != True and
                        self.get_value(m.group(3)) != False
                    ):
                    raise NotBooleanError()
                if not self.variables[m.group(3)]:
                    ignore_level = t['if_level']
        if self.tokens[-1]['if_level'] != 0:
            raise IfClauseError()
        return out

    def parse_variable(self, token):
        return self.variables[token.strip()]

    def tokenize(self):
        reg = re.compile(r'(?<!\\)\\\(([^\s\\])+\)|(?<!\\)\\([^\s\\])+|if\s+.+:')
        if_reg = re.compile('^if\s+(.+):$')
        fi_reg = re.compile('^\s*fi\s*$')
        prev = 0
        self.tokens = []
        indent = ['']
        for r in reg.finditer(self.template):
            pre_value = self.template[prev:r.start()]
            if pre_value != '':
                indent = self.__append_text(pre_value, indent)
            token = {}
            token['value'] = r[0]
            if_m = if_reg.match(token['value'])
            if if_m != None:
                token['type'] = 'if_condition'
                self.if_level += 1
                token['indent'] = indent[-(self.if_level)]
                self.block_stack.append(self.BLOCK_IF)
            elif fi_reg.match(token['value']) != None:
                token['type'] = 'if_close'
            else:
                token['type'] = 'variable'
            token['if_level'] = self.if_level
            token['for_level'] = self.for_level
            self.tokens.append(token)
            prev = r.end()
        last_text = re.sub(r'\n$', '', self.template[prev:])
        if last_text != '':
            # 最後に追加すべき文字列があれば追加
            self.__append_text(last_text, indent)
        # 後始末
        self.if_level = 0
        self.for_level = 0
        self.block_stack = [self.BLOCK_TOP]

    def __append_text(self, text, indent):
        ind_reg = re.compile('^\n*([ \t]*)')
        m = ind_reg.match(text)
        closed_blocks = []
        if len(indent[-1]) < len(m[1]):
            indent.append(m[1])
        elif len(indent[-1]) >= len(m[1]):
            matched_index = 0
            for i in range(len(indent)-1, -1, -1):
                if indent[i] == m[1]:
                    matched_index = i
                    break
                else:
                    indent.pop(i)
                    closed_blocks.append(self.block_stack.pop())
            else:
                raise IndentationError()
            for c in closed_blocks:
                if c == self.BLOCK_IF:
                    self.if_level -= 1
                elif c == self.BLOCK_FOR_LOOP:
                    self.for_level -= 1

        self.tokens.append({
            'value':     text,
            'type':      'text',
            'if_level':  self.if_level,
            'for_level': self.for_level
        })
        return indent

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

