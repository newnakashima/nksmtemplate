# nksm_parser

## 概要

テンプレートに変数の値をはめ込むことができる単純なプログラムです。

python3.6.5で作成。

## 使い方

### テンプレートのファイルを用意する。

例 template.txt
```
this is {{ hoge }}.
```

### 変数のキーと値を書いたJSONファイルを作成。

例 variables.json
```json
{
    "hoge": "テストです"
}
```

### プログラムを実行

```sh
$ python nksm_parser.py template.txt variables.json
```

結果
```
this is テストです.
```

