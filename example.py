import nksm_parser

p = nksm_parser.Parser()
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
p.render()

