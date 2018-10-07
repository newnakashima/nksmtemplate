import re
import sys
import json
import io
class Parser:

    text = ''
    variables = {}

    def read_template(self, path):
        data = ''
        with open(path, 'r') as f:
            data += f.read()
        self.text = data

    def read_json(self, path):
        with open(path, 'r') as f:
            self.variables = json.load(f)

    def set_variables(self, variables):
        self.variables = variables;

    def parse_variable(self):
        result_str = self.text
        dic = self.variables
        for key in dic:
            variable = re.compile('{{\s*' + key + '\s*}}')
            result_str = variable.sub(dic[key], result_str)
        return result_str

    def render(self):
        text = self.parse_variable()
        print(text, end='')

    def run(self):
        self.read_template(sys.argv[1])
        self.read_json(sys.argv[2])
        self.render()

if __name__ == '__main__':
    parser = Parser()
    parser.run()

