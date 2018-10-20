# nksmtemplate

## 概要

テンプレートに変数の値をはめ込むことができる単純なプログラムです。

python3.6.5で作成。

## 使い方

### テンプレートのファイルを用意する。

例 template.txt
```
this is \(hoge).
\name is my name.
```

### 変数のキーと値を書いたJSONファイルを作成。

例 variables.json
```json
{
    "hoge": "テストです",
    "name": "nakashima"
}
```

### プログラムを実行

```sh
$ python nksm_parser.py template.txt variables.json
```

結果
```
this is テストです.
nakashima is my name.
```

### if文

if.txt 
```
line 1.
if hoge:
    line 2.
line 3.
```
if.json
```json
{
  "hoge": false
}
```
結果
```
line 1.
line 3.
```

if2.json
```json
{
  "hoge": true
}
```

結果
```
line 1.
line 2.
line 3.
```
ifブロックの中のインデントは、ifブロックが書いてある行のインデントと揃えられます。（フラットになります）

ネストするとこうなります。

if_nested.txt
```
line 1.
if cond1:
    line 2.
    if cond2:
        line 3.
        if cond3:
            line4.
```
if_nested.json
```json
{
    "cond1": true,
    "cond2": true,
    "cond3": true
}
```
結果
```
line 1.
line 2.
line 3.
line 4.
```

### ifブロックの中でもインデントをそのまま出力したい場合

未実装です。
実装する予定です。
