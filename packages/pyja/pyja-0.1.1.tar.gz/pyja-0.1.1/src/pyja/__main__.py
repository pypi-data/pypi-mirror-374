import subprocess
import sys
import os
import deepl

def translate_error(error_text: str) -> str:
    """
    DEEPL API を使ってエラーメッセージを日本語に翻訳する
    """
    try:
        # DEEPLのAPIキーを環境変数から取得
        auth_key = os.getenv("DEEPL_API_KEY")
        if not auth_key:
            return "[エラー] DEEPL_API_KEY 環境変数が設定されていません"

        # DEEPLクライアントの初期化
        translator = deepl.Translator(auth_key)

        # 翻訳実行
        result = translator.translate_text(
            error_text,
            source_lang="EN",
            target_lang="JA"
        )
        return str(result)
    except Exception as e:
        return f"[翻訳失敗] {e}\n元のエラーメッセージ:\n{error_text}"

def main():
    if len(sys.argv) < 2:
        print("使い方: pyjp <pythonスクリプト> [引数...]")
        sys.exit(1)

    script = sys.argv[1]
    args = sys.argv[2:]

    # Python スクリプトを実行
    result = subprocess.run(
        ["python", script, *args],
        capture_output=True,
        text=True
    )

    # 標準出力はそのまま表示
    if result.stdout:
        print(result.stdout, end="")

    # 標準エラーは翻訳して表示
    if result.stderr:
        translated = translate_error(result.stderr)
        print(translated, file=sys.stderr)

    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
