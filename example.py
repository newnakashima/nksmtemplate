import nksm_parser

p = nksm_parser.Parser()
v = {
        'hoge': 'この世はもうおしまい'
        }
p.set_variables(v)
p.read_template('templates/template.nt')
p.render()

