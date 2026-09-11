#!/usr/bin/env python3
"""kakesu-lp の共通部分（head の alternate・ヘッダー・フッター）を全言語ぶん書き戻す。

各 HTML は次の3つの目印を持つ。目印のあいだはこのスクリプトが上書きするので、
手で書かない。目印の外（title / description / 本文）だけを手で書く。

    <!--chrome:alt-->   ... <!--/chrome:alt-->
    <!--chrome:head-->  ... <!--/chrome:head-->
    <!--chrome:foot-->  ... <!--/chrome:foot-->

使い方: python3 tools/i18n.py        （全ファイルを書き戻す）
        python3 tools/i18n.py --check（差分が出るなら異常終了。CI 用）
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://fukuidinotech.github.io/kakesu-lp/"

# ja は repo 直下。既に公開済みの URL を変えないため、ja だけサブディレクトリを持たない
PAGES = ["index.html", "features.html", "guide.html",
         "terms.html", "privacy.html", "contact.html"]

LANGS = {
    "ja": {
        "dir": "", "native": "日本語",
        "nav": ["ホーム", "機能", "使い方", "お問い合わせ"],
        "foot": ["ホーム", "機能一覧", "使い方", "利用規約", "プライバシーポリシー", "お問い合わせ"],
        "pick": "言語を選ぶ",
    },
    "en": {
        "dir": "en", "native": "English",
        "nav": ["Home", "Features", "Guide", "Contact"],
        "foot": ["Home", "Features", "Guide", "Terms", "Privacy", "Contact"],
        "pick": "Choose a language",
    },
    "de": {
        "dir": "de", "native": "Deutsch",
        "nav": ["Start", "Funktionen", "Anleitung", "Kontakt"],
        "foot": ["Start", "Funktionen", "Anleitung", "Nutzungsbedingungen", "Datenschutz", "Kontakt"],
        "pick": "Sprache wählen",
    },
    "fr": {
        "dir": "fr", "native": "Français",
        "nav": ["Accueil", "Fonctionnalités", "Guide", "Contact"],
        "foot": ["Accueil", "Fonctionnalités", "Guide", "Conditions", "Confidentialité", "Contact"],
        "pick": "Choisir la langue",
    },
    "es": {
        "dir": "es", "native": "Español",
        "nav": ["Inicio", "Funciones", "Guía", "Contacto"],
        "foot": ["Inicio", "Funciones", "Guía", "Términos", "Privacidad", "Contacto"],
        "pick": "Elegir idioma",
    },
    "ko": {
        "dir": "ko", "native": "한국어",
        "nav": ["홈", "기능", "사용법", "문의"],
        "foot": ["홈", "기능 목록", "사용법", "이용약관", "개인정보 처리방침", "문의"],
        "pick": "언어 선택",
    },
    "zh-Hans": {
        "dir": "zh-Hans", "native": "简体中文",
        "nav": ["首页", "功能", "使用方法", "联系"],
        "foot": ["首页", "功能一览", "使用方法", "使用条款", "隐私政策", "联系"],
        "pick": "选择语言",
    },
    "zh-Hant": {
        "dir": "zh-Hant", "native": "繁體中文",
        "nav": ["首頁", "功能", "使用方式", "聯絡"],
        "foot": ["首頁", "功能一覽", "使用方式", "使用條款", "隱私權政策", "聯絡"],
        "pick": "選擇語言",
    },
}

FOOT_PAGES = ["index.html", "features.html", "guide.html",
              "terms.html", "privacy.html", "contact.html"]
NAV_PAGES = ["index.html", "features.html", "guide.html", "contact.html"]


def url_for(lang: str, page: str) -> str:
    d = LANGS[lang]["dir"]
    return BASE + (f"{d}/{page}" if d else page)


def rel(from_lang: str, to_lang: str, page: str) -> str:
    """from_lang のページから to_lang の同じページへの相対パス"""
    src, dst = LANGS[from_lang]["dir"], LANGS[to_lang]["dir"]
    if src == dst:
        return page
    up = "../" if src else ""
    return f"{up}{dst}/{page}" if dst else f"{up}{page}"


def asset(lang: str, name: str) -> str:
    """style.css や shots/ は repo 直下に1つだけ置く"""
    return f"../{name}" if LANGS[lang]["dir"] else name


_css_version: str | None = None


def css_version() -> str:
    """`style.css` の中身から作る短い印。**手で上げない。**

    HTML と CSS は別々にキャッシュされる。GitHub Pages は両方に `max-age=600` を付けるので、
    CSS を変えた直後は「新しい HTML ＋ 古い CSS」で見る人が出る。
    markup はあるのにそれを整える規則が無い、という壊れ方をして、
    言語切替が素の箇条書きになって縦に伸びた（2026-09-11 に実際に起きた）。

    URL に中身の印を入れておけば、CSS を直した時点で URL も変わるので必ず取り直しになる。
    **中身から導出しているので上げ忘れが起きない。**
    CSS を直して書き戻しを忘れたら `--check` が落ちる（`/lp-sync` の L9）
    """
    global _css_version
    if _css_version is None:
        data = (ROOT / "style.css").read_bytes()
        _css_version = hashlib.sha256(data).hexdigest()[:8]
    return _css_version


def block_alt(lang: str, page: str) -> str:
    lines = [f'<link rel="canonical" href="{url_for(lang, page)}">']
    for other in LANGS:
        lines.append(f'<link rel="alternate" hreflang="{other}" href="{url_for(other, page)}">')
    # 一致する言語が無い人には英語を出す
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{url_for("en", page)}">')
    lines.append(f'<link rel="icon" href="{asset(lang, "icon-512.png")}">')
    lines.append(f'<link rel="apple-touch-icon" href="{asset(lang, "icon-512.png")}">')
    lines.append(
        f'<link rel="stylesheet" href="{asset(lang, "style.css")}?v={css_version()}">')
    lines.append(block_route())
    return "\n".join(lines)


# **この LP で唯一の JavaScript。**
#
# 静的配信なのでサーバ側で `Accept-Language` を見られない。ja を直下に置いている以上、
# ルート URL をそのまま踏んだ人には日本語が出る（SNS で共有されたリンク、直打ち）。
# App Store とアプリからの導線は言語別 URL を指しているので届かないのはここだけだが、
# 英語圏の人に日本語を出して終わる経路が1本残るのは具合が悪い。
#
# **止めたいときはこの関数が返す文字列を空にして `python3 tools/i18n.py` を流す。**
# それだけで全ページから消える（HTML を手で直す必要はない）。
#
# 検索エンジンへの影響: Google は言語による自動転送を勧めていない。
# hreflang は全ページに入れてあるので索引付けの手がかりは残るが、
# ja のページが英語版として扱われる可能性は残る。
# この LP の主な入口は App Store なので、その不利より取りこぼしを減らすほうを採った。
def block_route() -> str:
    return (
        '<script>\n'
        '/* 言語の自動振り分け。JS が無ければ日本語のまま出て、右上の言語切替で選べる */\n'
        '(function(){try{\n'
        '  /* **行き先は必ずこの表から選ぶ。** ?lang= も localStorage も外から書ける値なので、\n'
        '     そのまま URL に繋ぐと "https://..." や "javascript:..." を入れられる */\n'
        "  var OK={ja:1,en:1,de:1,fr:1,es:1,ko:1,'zh-Hans':1,'zh-Hant':1};\n"
        "  var PAGE={'index.html':1,'features.html':1,'guide.html':1,\n"
        "            'terms.html':1,'privacy.html':1,'contact.html':1};\n"
        "  var q=new URLSearchParams(location.search).get('lang');\n"
        "  if(q){if(OK[q]){try{localStorage.setItem('kakesu-lang',q)}catch(e){}}return}\n"
        "  if(document.documentElement.lang!=='ja')return;  /* 飛ばすのは ja のページだけ */\n"
        '  var pick=null;\n'
        "  try{pick=localStorage.getItem('kakesu-lang')}catch(e){}\n"
        '  if(pick&&!OK[pick])pick=null;  /* 表に無いものは捨てる（古い値・細工された値） */\n'
        '  if(!pick){\n'
        "    var l=navigator.languages||[navigator.language||''];\n"
        '    for(var i=0;i<l.length&&!pick;i++){\n'
        "      var t=String(l[i]).toLowerCase(),b=t.split('-')[0];\n"
        "      if(b==='ja')pick='ja';\n"
        "      else if(b==='zh')pick=/hant|tw|hk|mo/.test(t)?'zh-Hant':'zh-Hans';\n"
        "      else if(OK[b])pick=b;\n"
        '    }\n'
        "    if(!pick)pick='en';  /* hreflang の x-default と同じ */\n"
        '  }\n'
        "  if(pick==='ja')return;\n"
        "  var page=location.pathname.split('/').pop();\n"
        "  if(!PAGE[page])page='index.html';\n"
        "  location.replace(pick+'/'+page+location.hash);  /* 戻るで戻れるよう replace */\n"
        '}catch(e){}})();\n'
        '</script>'
    )


def block_head(lang: str, page: str) -> str:
    cfg = LANGS[lang]
    out = ['<header class="site-header">', '  <div class="inner">',
           f'    <a class="brand" href="{rel(lang, lang, "index.html")}">',
           f'      <img src="{asset(lang, "icon-512.png")}" width="28" height="28" alt="">',
           '      Kakesu', '    </a>', '    <nav>']
    for name, label in zip(NAV_PAGES, cfg["nav"]):
        cur = ' aria-current="page"' if name == page else ""
        out.append(f'      <a href="{name}"{cur}>{label}</a>')
    out.append('    </nav>')
    # 言語切替。JS を使わない（GitHub Pages に置くだけで動くようにする）
    out.append('    <details class="langpick">')
    out.append(f'      <summary aria-label="{cfg["pick"]}">{cfg["native"]}</summary>')
    out.append('      <ul>')
    for other, ocfg in LANGS.items():
        cur = ' aria-current="true"' if other == lang else ""
        # **`?lang=` は自動振り分けを黙らせるための印。**
        # 自分で選んだ言語は覚えて、次からは勝手に飛ばさない（`block_route`）
        out.append(f'        <li><a lang="{other}" hreflang="{other}" '
                   f'href="{rel(lang, other, page)}?lang={other}"{cur}>{ocfg["native"]}</a></li>')
    out.append('      </ul>')
    out.append('    </details>')
    out.append('  </div>')
    out.append('</header>')
    return "\n".join(out)


def block_foot(lang: str, page: str) -> str:
    cfg = LANGS[lang]
    out = ['<footer class="site-footer">', '  <div class="inner">', '    <nav>']
    for name, label in zip(FOOT_PAGES, cfg["foot"]):
        out.append(f'      <a href="{name}">{label}</a>')
    out.append('    </nav>')
    out.append('    <p class="copy">© 2026 Toru Fukui</p>')
    out.append('  </div>')
    out.append('</footer>')
    return "\n".join(out)


BLOCKS = {"alt": block_alt, "head": block_head, "foot": block_foot}


def apply(text: str, lang: str, page: str) -> str:
    for key, fn in BLOCKS.items():
        pattern = re.compile(f"(<!--chrome:{key}-->).*?(<!--/chrome:{key}-->)", re.S)
        if not pattern.search(text):
            raise SystemExit(f"目印 chrome:{key} が無い: {lang}/{page}")
        text = pattern.sub(lambda m: f"{m.group(1)}\n{fn(lang, page)}\n{m.group(2)}", text)
    # <html lang> も合わせる
    text = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', text, count=1)
    return text


def main() -> int:
    check = "--check" in sys.argv
    stale, missing = [], []
    for lang, cfg in LANGS.items():
        for page in PAGES:
            path = ROOT / cfg["dir"] / page if cfg["dir"] else ROOT / page
            if not path.exists():
                missing.append(str(path.relative_to(ROOT)))
                continue
            before = path.read_text(encoding="utf-8")
            after = apply(before, lang, page)
            if before != after:
                stale.append(str(path.relative_to(ROOT)))
                if not check:
                    path.write_text(after, encoding="utf-8")

    for name in missing:
        print(f"無い: {name}")
    for name in stale:
        print(("ずれ: " if check else "直した: ") + name)
    if check and (stale or missing):
        return 1
    if missing:
        return 1
    if not stale:
        print("共通部分は全ページ一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
