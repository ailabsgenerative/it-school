
import os
import datetime
from pathlib import Path
import subprocess
import json
import sys
from article_topics import TOPICS

ARTICLES_DIR = Path("articles")
PROMPT_PATH = Path("roadmap/gemini-prompt.md")

def load_prompt() -> str:
    """Gemini用プロンプトをロード"""
    with open(PROMPT_PATH, encoding="utf-8") as f:
        return f.read()

def call_gemini_api(prompt: str, language: str, date: str, theme: str) -> str:
    """geminiコマンドを実行して記事を生成する"""
    print(f"「{theme}」について記事を生成します...")
    try:
        # プロンプトを作成
        prompt_text = f"""以下のテーマについて、初心者にも分かりやすいように、マークダウン形式で技術解説記事を作成してください。

テーマ: {language}の{theme}

記事の構成案:
1. はじめに (テーマの概要と重要性)
2. 具体的な使い方や概念の説明 (サンプルコードを必ず含める)
3. まとめ (学習した内容の振り返り)

必ず、以下のJSON形式で応答してください。
{{
  "article_body": "（ここにマークダウン形式の記事本文を記述）"
}}
"""

        # geminiコマンドを実行
        command = f'echo "{prompt_text}" | gemini -o json --yolo'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            raise RuntimeError(f"geminiコマンドの実行に失敗しました。\n{result.stderr}")

        # geminiコマンドの出力をパース
        response_data = json.loads(result.stdout)
        # `response` キーから内部のJSON文字列を取得
        inner_json_str = response_data.get("response", "{}")
        # 内部のJSONをパースして、記事本文を取得
        article_data = json.loads(inner_json_str)
        article_body = article_data.get("article_body", "")

        if not article_body:
            raise ValueError("geminiからの応答が空です。")

        return f"""---\ntitle: {language}の{theme}入門\ndate: {date}\ncategories: [{language}]\ntags: [AI, Gemini, 自動生成, {language}, {theme}]\n---\n\n{article_body}
"""

    except Exception as e:
        print(f"記事の生成中にエラーが発生しました: {e}")
        return f"""---\ntitle: {language}の{theme}入門 ({date})\ndate: {date}\ncategories: [{language}]\ntags: [AI, Gemini, 自動生成, {language}, {theme}]\n---\n\n# 記事の生成に失敗しました\n\nテーマ「{theme}」の記事生成中にエラーが発生しました。
"""

def generate_and_save_article(language: str, date: str, prompt: str, theme: str, index: int):
    """Gemini APIで記事生成し保存"""
    content = call_gemini_api(prompt, language, date, theme)
    # ファイル名を「01_テーマ名.md」のように整形
    # テーマ名にファイル名として不適切な文字が含まれる場合を考慮
    safe_theme = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in theme)
    safe_theme = '_'.join(filter(None, safe_theme.split('_')))
    filename = ARTICLES_DIR / language.lower() / f"{index:02d}_{safe_theme}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_articles.py <language>")
        sys.exit(1)

    target_language = sys.argv[1]
    if target_language not in TOPICS:
        print(f"Error: Language '{target_language}' not found in TOPICS.")
        sys.exit(1)

    today = datetime.date.today().isoformat()
    lang_dir = ARTICLES_DIR / target_language.lower()
    archive_dir = lang_dir / "archive"
    lang_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(exist_ok=True)

    # 既存のMarkdownファイルをアーカイブ
    for f in lang_dir.glob("*.md"):
        f.rename(archive_dir / f.name)

    prompt = load_prompt()

    for i, topic in enumerate(TOPICS[target_language]):
        generate_and_save_article(target_language, today, prompt, topic, i + 1)
    print(f"{target_language} の記事生成完了")

if __name__ == "__main__":
    main()
