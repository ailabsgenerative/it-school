---
title: Pythonのファイル入出力とwith文入門
date: 2025-11-08
categories: [Python]
tags: [AI, Gemini, 自動生成, Python, ファイル入出力とwith文]
---

# 記事本文をここに記述してください

## Gemini CLIでの生成方法

以下のコマンドを参考に、Gemini CLIで記事本文を生成し、このファイルに追記してください。
プロンプトは `roadmap/gemini-prompt.md` を参考に作成してください。

```bash
# 例:
# gemini -o json --yolo "以下のテーマについて、初心者にも分かりやすいように、マークダウン形式で技術解説記事を作成してください。

テーマ: Pythonのファイル入出力とwith文

記事の構成案:
1. はじめに (テーマの概要と重要性)
2. 具体的な使い方や概念の説明 (サンプルコードを必ず含める)
3. まとめ (学習した内容の振り返り)

必ず、以下のJSON形式で応答してください。
{"article_body": "ここにマークダウン形式の記事本文を記述"}" > temp_output.json
# cat temp_output.json | jq -r '.response | fromjson.article_body' >> articles/python/13_ファイル入出力とwith文.md
# rm temp_output.json
```
