# v2の不要ファイル整理と生成結果の確認

確認日: 2026-09-26。

## 判断と変更

- `build.ini` は旧FontForge用 `build.py` だけが読み込む。v2のCLIは `sources.lock.json` で入力TTFとSHA-256を固定し、`src/soroemono/` から生成するため、両ファイルを作業ツリーから削除した。
- `resource/LINESeedJP/` と `resource/NotoSansJP/` の各Regular/Bold TTFとOFLは、v2の入力ロック、生成、検査、proof、CIから参照されないため削除した。
- v2が参照するJetBrains Mono/BIZ UDGothicのTTFとOFL、公開v1.0.0を取得する設定は維持した。旧実装と削除した入力はGit履歴で参照できる。

## 生成と数値検査

既存の `.venv/bin/python -m soroemono.cli` で削除前後にRegular/Boldを独立した出力先へ生成した。`uv run --locked` はサンドボックスからuvの共有キャッシュを開けず実行できなかった。削除後の `check` は両スタイルで合格し、unittest 5件も合格した。

| スタイル | 削除前後で一致したTTFのSHA-256 |
| --- | --- |
| Regular | `dbb57d5d8a634ecbb5527832ad52d8df06c5ea7b87be54dddedd9e052c549674` |
| Bold | `f9f7ec6b42daca9969802b73e76ddfc15afd9cbcc8b5f8a464e62990c347237b` |

両スタイルとも通常cmap 12,442件、advance 0/600/1200は47/1,518/10,877件、保持したラテン字形1,743、IVS 10,160組。削除前後のTTFは各スタイルでバイト一致した。

## ブラウザ表示

削除前後のRegular TTFをそれぞれ公開v1.0.0と並べたブラウザproofで撮影した。[削除前](artifacts/v2-cleanup-2026-09-26/before.png)、[削除後](artifacts/v2-cleanup-2026-09-26/after.png)、[削除前後の画素差](artifacts/v2-cleanup-2026-09-26/diff.png)を確認した。1200×1562画素の画像は全画素一致し、差分画像は全白。表示も目視確認した。

撮影環境はmacOS 26.6.2 arm64、Chrome 154.0.8037.57のヘッドレス、1200×1100 CSS px、deviceScaleFactor 1、ブラウザ倍率1、ブラウザ標準の描画設定。文字サイズ14/16/20 CSS px、`font-synthesis:none`、`calt` ON。OSのDPIはヘッドレス撮影から推定していない。両回ともフォント読み込み・幅確認が成功し、見本にシステムフォントへのフォールバックはなかった。旧版TTFはSHA-256 `83994897f9a4ee58cab502861f47718b4638b1836e379e1479035b4a664ea8d3`、試作Regularは上表の値。[削除前の環境情報](artifacts/v2-cleanup-2026-09-26/before-manifest.json)と[削除後の環境情報](artifacts/v2-cleanup-2026-09-26/after-manifest.json)に詳細を残した。

今回の確認は不要ファイル削除によるv2生成結果の不変性が対象。Windows実アプリでの受け入れは既存の未完了事項のまま。
