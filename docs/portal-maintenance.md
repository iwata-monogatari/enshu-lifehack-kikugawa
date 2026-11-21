# 菊川ライフハックの更新元と再生成

2026年11月21日、既存の暮らしのガイドを保持し、目的別ガイド・質問検索・チェックリスト・地域スポット・制度比較を追加。

- `data/topics_master.json`：155項目の基本情報と出典。`content_review` は差分を確認した日・範囲・根拠で、全内容の再確認を意味しない。
- `data/content/*.json`：各ガイドの本文、質問、手順。
- `data/portal_content.json`：目的別の原稿、チェックリスト、地域スポット。日付だけを自動更新せず、出典との再照合が済んだ範囲を変更する。
- `data/fact_labels.json`：窓口情報の日本語表示名。
- `scripts/build_portal.py`：新規ページと共通導線を生成。既存トップのカテゴリ・写真・相談先欄は保持する。

今回の再生成コマンド（リポジトリ直下で実行）：

```sh
python scripts/generate_pages.py --content-only --review-date 2026-11-21
python scripts/build_portal.py
node scripts/build-search-index.mjs
python scripts/build_sitemap.py
node scripts/test-search.mjs
python scripts/inspect_all.py
```

`--content-only` は既存HTMLのhead・フッター・計測処理を保持する。指定日にcontent_reviewを付けた項目だけを再生成し、更新していない記事を旧生成元で一括上書きしない。

11月21日時点で、保育・児童クラブ・検診・窓口時間・創業支援・耐震除却・高齢者補聴器支援・相続登記・相続空き家の税特例等を更新。差分の詳細と根拠は `/updates/`。旧リンク4件を置換済み。水道電子申請と一部窓口の表記差は、公式情報の不一致として確認先を掲載している。

質問集は既存の質問・回答を統合した検索機能で、掲載回答すべてを新規執筆・全件再確認したという意味ではない。地域案内の32項目は市観光一覧を整理したもので、現地検査や全施設網羅を意味しない。チェック状況は端末のlocalStorageだけに保存し、申請情報は送信しない。

公開前に最新remote mainと競合を照合し、通常のfast-forward pushを使用する。公開後はHTTP取得に加え、実ブラウザで固有本文・導線・画像・狭幅表示を確認する。今回の証拠は依頼チャットの `outputs/kikugawa-refresh-2026-11-21/` に保存。
