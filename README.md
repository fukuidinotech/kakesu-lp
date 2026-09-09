# Kakesu LP

iOS アプリ **Kakesu**（あとで掘り出すためのブックマーク）の紹介サイト。
GitHub Pages で公開する。

| ページ | 役割 |
|---|---|
| `index.html` | 何のアプリかを最初に言う |
| `features.html` | 機能一覧。各機能から使い方の該当箇所へ飛べる |
| `guide.html` | 使い方。実機のスクリーンショット付き |
| `terms.html` | 利用規約（無保証・免責） |
| `privacy.html` | プライバシーポリシー。**App Store の申告と一致させる** |
| `contact.html` | 問い合わせ窓口。サポートURLとして使う |

## 決まりごと

- **これは public。** 個人情報・内部情報を入れない。
  連絡先は公開窓口 `fukuidinotech@gmail.com` のみ、名義は `Toru Fukui` で統一する
- 色は `../docs/DESIGN.md` が正本。**瑠璃＝操作できるもの / 赤茶＝状態の印**。この役割分担を崩さない
- Web フォントを入れない（システムフォント。アプリと揃える）
- ダークモードは `prefers-color-scheme` で切り替える

## スクリーンショット

`shots/*.png` はアプリの UI テストが撮っている。手で撮らない。

```bash
cd ../kakesu-app && OUT=../kakesu-lp/shots make guide-shots
```

長押しメニューや削除の「元に戻す」は、押さないと画面に出ないので XCUITest で撮る。
**署名を切って撮らない。** 切ると App Group を開けず、設定画面がエラー状態で写る。

## アプリを変えたとき

LP とストア掲載文は放っておくと取り残される。`/lp-sync` を通す。

```bash
python3 ../.claude/skills/lp-sync/scripts/lp-sync.py
```

デザイントークンの食い違い・スクショの陳腐化・リンク切れ・掲載文の欠落を検出する。
「この機能を LP に載せるべきか」は検出できないので、そこは人が読む。
