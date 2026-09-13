# SEO ビルドスクリプト

新しい記事を追加したあとに、この2本を順に実行すると SEO 用の要素が揃います。

```bash
python tools/seo-images.py     # 画像のリネーム・WebP化・縮小、参照の書き換え
python tools/seo-build.py      # canonical / OG / JSON-LD / 関連記事 / テーマ別ページ / sitemap.xml / 404
```

- どちらも何度実行しても同じ結果になります(すでに入っている要素は触りません)。
- 記事の公開日・カテゴリ・サムネイルは blog-list.html のカードから読み取ります。先に blog-list.html へカードを追加してください。
- テーマ別ページ(topic-*.html)の振り分けは seo-build.py の HUBS のキーワードで決まります。新しい記事がどのテーマにも当てはまらない場合は「労働時間・就業規則」に入ります。
