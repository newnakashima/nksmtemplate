import re
import sys
import json
class Parser:

    text = ''
    variables = {}

    def read_template(self, path):
        data = ''
        with open(path, 'r') as f:
            data += f.read()
        self.text = data

    def read_variable(self, path):
        with open(path, 'r') as f:
            self.variables = json.load(f)

    def parse_variable(self):
        result_str = self.text
        dic = self.variables
        for key in dic:
            variable = re.compile('{{\s+' + key + '\s+}}')
            result_str = variable.sub(dic[key], result_str)
        return result_str

    def run(self):
        self.read_template(sys.argv[1])
        self.read_variable(sys.argv[2])
        print(self.parse_variable(), end='')

if __name__ == '__main__':
    parser = Parser()
    parser.run()

