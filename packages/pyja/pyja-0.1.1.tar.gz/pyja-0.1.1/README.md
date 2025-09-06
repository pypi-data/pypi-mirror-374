# pyja

Python スクリプトを日本語エラーメッセージ付きで実行するコマンドラインツールです。  
エラーが出た場合、DeepL API を使って日本語に翻訳して表示します。

---

## 特徴

- `pyja sample.py` で Python スクリプトを実行
- 標準出力はそのまま表示
- 標準エラーは DeepL で日本語に翻訳して表示

---


- Python 3.10 以上
- DeepL API Key
- `deepl` パッケージ

---

## インストール（開発用）

```bash
git clone https://github.com/gonggonggo/pyja.git
cd pyja
pip install -e .
```

---

## DeepL API キーの設定

1. DeepL の [API プラン](https://www.deepl.com/pro-api) に登録  
2. 環境変数 `DEEPL_API_KEY` に API キーを設定

### Windows (PowerShell)

```powershell
setx DEEPL_API_KEY "あなたのAPIキー"
```

### macOS / Linux

```bash
export DEEPL_API_KEY="あなたのAPIキー"
```

設定後、ターミナルを再起動してください。

---

## 使い方

```bash
pyja sample.py
```

- `sample.py` は Python スクリプト
- エラーが出た場合、DeepL API で日本語に翻訳して表示

### 引数付きスクリプトの実行

```bash
pyja sample.py arg1 arg2
```

- `arg1`, `arg2` は `sample.py` に渡される引数

---

## 注意点

- DeepL API の翻訳には通信が発生します
- エラーが多いスクリプトは少し遅くなる可能性があります
- MIT ライセンスの下で公開しています。自由に使用・改変できます

