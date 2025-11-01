
import os
import datetime
from pathlib import Path
import requests
import sys
from article_topics import TOPICS

ARTICLES_DIR = Path("articles")
PROMPT_PATH = Path("roadmap/gemini-prompt.md")

def load_prompt() -> str:
    """Gemini用プロンプトをロード"""
    with open(PROMPT_PATH, encoding="utf-8") as f:
        return f.read()

def call_gemini_api(prompt: str, language: str, date: str, theme: str) -> str:
    """Gemini APIに記事生成を依頼"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # ダミーモード: APIキーがなければサンプル記事を返す
        return f"""---\ntitle: {language}の{theme}入門 ({date})\ndate: {date}\ncategories: [{language}]\ntags: [AI, Gemini, 自動生成, {language}, {theme}]\n---\n\nこの記事はAI（Gemini API/ダミーモード）によって自動生成されています。\n\n# {language}の{theme}とは？\n\n（ここに{language}の{theme}に関する概要や学習ポイントがダミーで生成されます）\n"""
    # TODO: Gemini APIのエンドポイント・パラメータは本番用に調整
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt.format(language=language, date=date, theme=theme)}]
        }]
    }
    params = {"key": api_key}
    resp = requests.post(url, headers=headers, json=data, params=params)
    resp.raise_for_status()
    # Gemini APIのレスポンスから記事本文を抽出（仮実装）
    result = resp.json()
    # TODO: 本番はresultから適切に本文抽出
    return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get(
        "text", "")



def generate_and_save_article(language: str, date: str, prompt: str, theme: str, index: int):
    """Gemini APIで記事生成し保存"""
    content = call_gemini_api(prompt, language, date, theme)
    # ファイル名を「01_テーマ名.md」のように整形
    # テーマ名にファイル名として不適切な文字が含まれる場合を考慮
    safe_theme = "".join(c if c.isalnum() or c in ['-', '_'] else '' for c in theme)
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
    # Ensure the language-specific directory exists
    (ARTICLES_DIR / target_language.lower()).mkdir(parents=True, exist_ok=True)
    prompt = load_prompt()

    for i, topic in enumerate(TOPICS[target_language]):
        generate_and_save_article(target_language, today, prompt, topic, i + 1)
    print(f"{target_language} の記事生成完了")

if __name__ == "__main__":
    main()
