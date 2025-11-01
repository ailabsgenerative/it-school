# 静的サイトビルドスクリプト
# articles/ のMarkdownを docs/ にHTML変換し、Qiita/GitHub/Zenn風デザイン・SEO・広告枠を反映

import os
from pathlib import Path
import markdown
from jinja2 import Environment, FileSystemLoader
import shutil

ARTICLES_DIR = Path("articles")
DOCS_DIR = Path("docs")
TEMPLATES_DIR = Path("templates")



# SEO用メタタグ生成
import re

def make_seo_meta(title, description, tags):
    return f'<meta property="og:title" content="{title}">\n<meta property="og:description" content="{description}">\n<meta name="keywords" content="{tags}">'

def process_markdown_file(mdfile_path: Path, env: Environment, base_template, language_slug: str) -> dict:
    """単一のMarkdownファイルを処理し、HTMLを生成してメタデータを返す"""
    with open(mdfile_path, encoding="utf-8") as f:
        mdtext = f.read()

    fm = re.match(r"---\n(.*?)---\n", mdtext, re.DOTALL)
    meta = {"title": "", "description": "", "tags": "", "slug": mdfile_path.stem, "language_slug": language_slug}
    content_start_index = 0
    if fm:
        for line in fm.group(1).splitlines():
            if line.startswith("title:"): meta["title"] = line[6:].strip()
            if line.startswith("tags:"): meta["tags"] = line[5:].strip()
            if line.startswith("description:"): meta["description"] = line[12:].strip() # descriptionを追加
        content_start_index = fm.end()
    
    # Front Matterの後に本文が続く場合を考慮
    article_content = mdtext[content_start_index:].strip()
    if not meta["description"] and article_content:
        # descriptionがFront Matterにない場合、記事の最初の段落から生成
        first_paragraph = article_content.split('\n\n')[0] # 最初の段落を取得
        meta["description"] = (first_paragraph[:150] + '...') if len(first_paragraph) > 150 else first_paragraph


    html_content = markdown.markdown(article_content, extensions=["fenced_code", "tables"])
    seo = make_seo_meta(meta["title"], meta["description"], meta["tags"])

    return {
        "meta": meta,
        "html": base_template.render(
            title=meta["title"],
            description=meta["description"],
            content=html_content,
            seo=seo
        )
    }

def build():
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    base_template = env.get_template("base.html")
    main_index_template = env.get_template("main_index.html")
    language_index_template = env.get_template("language_index.html")

    # docsディレクトリをクリーンアップして再作成
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(exist_ok=True)

    # CSSファイルをdocs直下にコピー
    shutil.copy(TEMPLATES_DIR / "style.css", DOCS_DIR / "style.css")

    all_languages_data = []
    all_articles_data = [] # すべての記事のデータを格納するリスト

    # 各言語のディレクトリを処理
    for lang_dir in ARTICLES_DIR.iterdir():
        if lang_dir.is_dir():
            language_name = lang_dir.name.capitalize() # 例: python -> Python
            language_slug = lang_dir.name.lower() # 例: python

            (DOCS_DIR / language_slug).mkdir(exist_ok=True)
            
            articles_in_lang = []
            # 言語ディレクトリ内のMarkdownファイルを処理
            for mdfile in sorted(lang_dir.glob("*.md")):
                processed_data = process_markdown_file(mdfile, env, base_template, language_slug)
                
                # 個別記事のHTMLを保存
                output_path = DOCS_DIR / language_slug / (processed_data["meta"]["slug"] + ".html")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(processed_data["html"])
                
                articles_in_lang.append(processed_data["meta"])
                all_articles_data.append(processed_data["meta"]) # すべての記事のリストにも追加
            
            # 言語別インデックスページの生成
            lang_index_html = language_index_template.render(
                language_name=language_name,
                articles=articles_in_lang,
                title=f"{language_name} 学習ロードマップ",
                description=f"{language_name} の学習ロードマップです。",
                seo=make_seo_meta(f"{language_name} 学習ロードマップ", f"{language_name} の学習ロードマップです。", f"{language_name}, 学習, ロードマップ")
            )
            with open(DOCS_DIR / language_slug / "index.html", "w", encoding="utf-8") as f:
                f.write(lang_index_html)
            
            all_languages_data.append((language_name, language_slug))
    
    # メインインデックスページの生成
    main_index_html = main_index_template.render(
        languages=all_languages_data,
        articles=all_articles_data, # すべての記事のデータを渡す
        title="IT学習ブログ - ロードマップ",
        description="IT学習ブログのプログラミング言語別学習ロードマップです。",
        seo=make_seo_meta("IT学習ブログ - ロードマップ", "IT学習ブログのプログラミング言語別学習ロードマップです。", "IT, 学習, プログラミング, ロードマップ")
    )
    with open(DOCS_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(main_index_html)

if __name__ == "__main__":
    build()
