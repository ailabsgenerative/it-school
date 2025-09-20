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

# テンプレート・CSSのセットアップ（初回のみ）
def setup_templates():
    TEMPLATES_DIR.mkdir(exist_ok=True)
    # ベーステンプレート
    (TEMPLATES_DIR / "base.html").write_text('''
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{ title }}</title>
  <meta name="description" content="{{ description }}">
  <link rel="stylesheet" href="/style.css">
  {{ seo | safe }}
</head>
<body>
  <header><h1><a href="/index.html">IT学習ブログ</a></h1></header>
  <main>
    {{ content | safe }}
  </main>
  <footer><small>© 2025 IT School Blog</small></footer>
</body>
</html>
''', encoding="utf-8")
    # CSS
    (DOCS_DIR / "style.css").write_text('''
body { font-family: 'Yu Gothic', 'Meiryo', sans-serif; background: #f7f7f7; color: #222; line-height: 1.8; }
header, footer { background: #222; color: #fff; padding: 1em; text-align: center; }
main { max-width: 700px; margin: 2em auto; background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 2px 8px #0001; }
h1, h2, h3 { color: #2d6cdf; }
a { color: #2d6cdf; text-decoration: none; }
a:hover { text-decoration: underline; }
blockquote, .ad { background: #eaf3ff; border-left: 4px solid #2d6cdf; margin: 1em 0; padding: 1em; }
@media (max-width: 600px) { main { padding: 1em; } }
''', encoding="utf-8")

# SEO用メタタグ生成
def make_seo_meta(title, description, tags):
    return f'<meta property="og:title" content="{title}">\n<meta property="og:description" content="{description}">\n<meta name="keywords" content="{tags}">' 

def build():
    setup_templates()
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("base.html")
    DOCS_DIR.mkdir(exist_ok=True)
    # 記事ごとにHTML生成
    for mdfile in ARTICLES_DIR.glob("*.md"):
        with open(mdfile, encoding="utf-8") as f:
            mdtext = f.read()
        # Front Matter抽出
        import re
        fm = re.match(r"---\n(.*?)---\n", mdtext, re.DOTALL)
        meta = {"title": "", "description": "", "tags": ""}
        if fm:
            for line in fm.group(1).splitlines():
                if line.startswith("title:"): meta["title"] = line[6:].strip()
                if line.startswith("tags:"): meta["tags"] = line[5:].strip()
        meta["description"] = mdtext.split("\n", 10)[-1][:80]
        html = markdown.markdown(mdtext, extensions=["fenced_code", "tables"]) 
        seo = make_seo_meta(meta["title"], meta["description"], meta["tags"])
        out = template.render(title=meta["title"], description=meta["description"], content=html, seo=seo)
        outname = DOCS_DIR / (mdfile.stem + ".html")
        with open(outname, "w", encoding="utf-8") as f:
            f.write(out)
    # index.html生成
    index_html = "<h2>新着記事</h2><ul>"
    for mdfile in sorted(ARTICLES_DIR.glob("*.md"), reverse=True):
        title = mdfile.stem
        index_html += f'<li><a href="{mdfile.stem}.html">{title}</a></li>'
    index_html += "</ul>"
    out = template.render(title="IT学習ブログ", description="IT初心者向け自動生成ブログ", content=index_html, seo="")
    with open(DOCS_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(out)

if __name__ == "__main__":
    build()
