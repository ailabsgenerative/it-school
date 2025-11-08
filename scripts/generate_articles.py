
import os
import datetime
from pathlib import Path
import subprocess
import json
import sys
from article_topics import TOPICS

ARTICLES_DIR = Path("articles")
PROMPT_PATH = Path("roadmap/gemini-prompt.md")

# call_gemini_api 関数は削除されます。

def generate_and_save_article(language: str, date: str, theme: str, index: int):
    """空のMarkdownファイル（フロントマターのみ）を生成し保存"""
    # ファイル名を「01_テーマ名.md」のように整形
    safe_theme = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in theme)
    safe_theme = '_'.join(filter(None, safe_theme.split('_')))
    filename = ARTICLES_DIR / language.lower() / f"{index:02d}_{safe_theme}.md"

    # YAMLフロントマターのみを含むコンテンツを作成
    content = f"""---
title: {language}の{theme}入門
date: {date}
categories: [{language}]
tags: [AI, Gemini, 自動生成, {language}, {theme}]
---

# 記事本文をここに記述してください

## Gemini CLIでの生成方法

以下のコマンドを参考に、Gemini CLIで記事本文を生成し、このファイルに追記してください。
プロンプトは `roadmap/gemini-prompt.md` を参考に作成してください。

```bash
# 例:
# gemini -o json --yolo "以下のテーマについて、初心者にも分かりやすいように、マークダウン形式で技術解説記事を作成してください。\n\nテーマ: Pythonの{theme}\n\n記事の構成案:\n1. はじめに (テーマの概要と重要性)\n2. 具体的な使い方や概念の説明 (サンプルコードを必ず含める)\n3. まとめ (学習した内容の振り返り)\n\n必ず、以下のJSON形式で応答してください。\n{{\"article_body\": \"ここにマークダウン形式の記事本文を記述\"}}" > temp_output.json
# cat temp_output.json | jq -r '.response | fromjson.article_body' >> {filename}
# rm temp_output.json
```
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"空の記事ファイル「{filename}」を生成しました。")


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
    print(f"既存の {target_language} 記事をアーカイブしています...")
    for f in lang_dir.glob("*.md"):
        if f.name != "index.md": # index.md はアーカイブしない
            f.rename(archive_dir / f.name)
            print(f"  - {f.name} をアーカイブしました。")
    print("アーカイブ完了。\n")

    print(f"{target_language} の記事ファイル（フロントマターのみ）を生成しています...")
    for i, topic in enumerate(TOPICS[target_language]):
        generate_and_save_article(target_language, today, topic, i + 1)
    print(f"\n{target_language} の記事ファイル生成完了。\n")

    print("--- 次のステップ ---")
    print(f"生成された各Markdownファイル（例: articles/{target_language.lower()}/01_*.md）を開き、")
    print("ファイル内の指示に従ってGemini CLIを使用して記事本文を生成し、追記してください。")
    print(f"プロンプト作成の際は、`roadmap/gemini-prompt.md` を参考にしてください。")
    print("\nすべての記事本文の追記が完了したら、以下のコマンドで静的サイトを構築できます。")
    print("  python scripts/build_site.py")


if __name__ == "__main__":
    main()
