import nksmtemplate

p = nksmtemplate.Parser()
v = {
        "hoge": "この世はもうおしまい",
        "arr": [
            "one",
            "two",
            "three"
        ]
    }
p.variables = v
p.read_template('templates/template.nt')
# p.tokenize()
# for t in p.tokens:
#     print(t)
p.render()

