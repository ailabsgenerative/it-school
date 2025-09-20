
import os
import datetime
from pathlib import Path
import requests

LANGUAGES = ["Python", "JavaScript", "Java", "C#", "Ruby", "Go", "PHP"]
ARTICLES_DIR = Path("articles")
PROMPT_PATH = Path("roadmap/gemini-prompt.md")

def load_prompt() -> str:
    """Gemini用プロンプトをロード"""
    with open(PROMPT_PATH, encoding="utf-8") as f:
        return f.read()

def call_gemini_api(prompt: str, language: str, date: str) -> str:
    """Gemini APIに記事生成を依頼"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # ダミーモード: APIキーがなければサンプル記事を返す
        return f"""---\ntitle: {language}入門 ({date})\ndate: {date}\ncategories: [{language}]\ntags: [AI, Gemini, 自動生成]\n---\n\nこの記事はAI（Gemini API/ダミーモード）によって自動生成されています。\n\n# {language}とは？\n\n（ここに{language}の概要や学習ポイントがダミーで生成されます）\n"""
    # TODO: Gemini APIのエンドポイント・パラメータは本番用に調整
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt.format(language=language, date=date)}]
        }]
    }
    params = {"key": api_key}
    resp = requests.post(url, headers=headers, json=data, params=params)
    resp.raise_for_status()
    # Gemini APIのレスポンスから記事本文を抽出（仮実装）
    result = resp.json()
    # TODO: 本番はresultから適切に本文抽出
    return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

def insert_ad_and_notice(article_md: str) -> str:
    """広告枠・AI明記・SEO用要素を挿入"""
    ad_block = "\n> **PR: ITスクールのご案内はこちら（アフィリエイトリンク）**\n"
    ai_notice = "\n---\nこの記事はAI（Gemini API）によって自動生成されています。内容の正確性は保証されません。\n---\n"
    # 記事末尾に広告・AI明記を追加
    return article_md.strip() + ad_block + ai_notice

def generate_and_save_article(language: str, date: str, prompt: str):
    """Gemini APIで記事生成し保存"""
    content = call_gemini_api(prompt, language, date)
    content = insert_ad_and_notice(content)
    filename = ARTICLES_DIR / f"{date}_{language.lower()}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    today = datetime.date.today().isoformat()
    ARTICLES_DIR.mkdir(exist_ok=True)
    prompt = load_prompt()
    for lang in LANGUAGES:
        generate_and_save_article(lang, today, prompt)
    print("記事生成完了")

if __name__ == "__main__":
    main()
