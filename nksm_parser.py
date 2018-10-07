import re
import sys
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
        ignore_flg = False
        result_lines = []
        for line in lines:
            if_reg = re.compile('^{{\s*if\s*(.+)\s*}}$')
            if_matched = if_reg.match(line)
            fi_reg = re.compile('^{{\s*fi\s*}}$')
            fi_matched = fi_reg.match(line)
            if if_matched != None:
                # if文の行の場合は出力行に含めない
                if not self.variables[if_matched.group(1)]:
                    # ifの条件がFalseのときは無視フラグを立てる
                    ignore_flg = True
                continue
            if fi_matched != None:
                # if文から抜けるときは無視フラグ解除。出力行に含めない
                ignore_flg = False
                continue
            if ignore_flg:
                # if文の中かつ条件に一致しない場合は出力しない
                continue
            # それ以外の場合は普通に出力
            result_lines.append(line)
        self.text = '\n'.join(result_lines)

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

