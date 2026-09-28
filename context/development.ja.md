# v2.0.0の開発・検証手順

更新: 2026-09-28。Regular/Bold試作時の手順と初回実測値は[旧記録](development-preview-2026-09-23.ja.md)へ保存した。現在のビルドは `SOROEMONO` の4スタイルを生成する。公開v1.0.0は比較基準として保持し、旧 `build.py` は実行しない。

## 環境と入力

- Pythonは `.python-version` の3.14.6、依存関係は `uv.lock` に固定する。`uv` 0.12.17で確認済み。`requires-python >=3.12` は対応下限。
- 元TTFの版・SHA-256は `sources.lock.json` に固定する。JetBrains Mono 2.304のRegular/Bold/Italic/Bold ItalicとBIZ UDGothic 1.051のRegular/Boldを使用する。入力取得は通常のビルドに混ぜない。
- ブラウザ撮影には `uv sync --locked --extra proof` と `uv run --locked playwright install chromium` が必要。基準版は `uv run --locked soroemono fetch-baseline` で別途取得する。取得後の生成・検査はローカル入力のみを読む。
- MacとWindowsは別々のローカルcloneで実行し、`.venv`・`build/`・ブラウザ本体を共有しない。Windows側のビルド環境構築は新運用で未確認。固定版を導入できない場合は失敗したコマンド・OS/CPU構成を報告し、Windows側でロックや入力を変更しない。

## コマンド

```sh
uv sync --locked --extra proof
uv run --locked python -m unittest discover -s tests -v
uv run --locked soroemono release
uv run --locked soroemono build --style "Bold Italic"
uv run --locked soroemono check --style "Bold Italic"
uv run --locked soroemono fetch-baseline
uv run --locked soroemono proof --style "Bold Italic"
uv run --locked soroemono capture --proof build/proofs/bold-italic
```

`build` / `check` / `proof` の `--style` は `Regular`、`Bold`、`Italic`、`Bold Italic`。省略するとRegular。`build --output`、`check --font`、`proof --font --output`、`release --output` で場所を指定できる。リポジトリ外からはサブコマンドの前に `--root` を指定する。

| 出力 | 内容 |
| --- | --- |
| `build/formal/` | 個別の正式名義TTF、ビルド情報、数値検査結果、両元フォントのOFL |
| `dist/SOROEMONO_v2.0.0.zip` | 4つのTTF、両OFL、入力ロック、README、ビルド・検査結果、ファイル別SHA-256 |
| `dist/SOROEMONO_v2.0.0.zip.sha256` | ZIP全体のSHA-256 |
| `build/proofs/<style>/` | 公開v1.0.0と新版のTTF内包比較HTML、画像、撮影環境情報 |

`release` は各スタイルを2回生成してバイト一致を確認し、生成TTFの数値・シェーピング検査が通った場合だけ決まった時刻・順序でZIPを作る。Italic系の日本語はBIZの直立字形を9度傾ける。英数字はJetBrains Monoの純正Italic/Bold Italicを使う。公開v1.0.0にはItalic系がないため、そのproofの変更前は対応する直立スタイルであり、斜体同士の比較ではない。

ブラウザproofはOSにフォントを登録せず、Font Loading APIと実測幅を確認する。`capture` は実使用フォントを検査し、`before.png`、`after.png`、`diff.png` と `manifest.json` を保存する。日常の生成物はGit管理外。確定した検証画像・環境情報と報告は `context/artifacts/<run-id>/mac/` または `win/` に保存する。Windows側の実行・実アプリ受け入れ・Git同期は[Windows検証・Git受け渡し手順](windows-verification.ja.md)を参照する。

`check` は等幅メタデータ `OS/2.xAvgCharWidth=600`、`post.isFixedPitch=1`、`OS/2.panose.bProportion=9` も検査する。600は合成後の全グリフ平均を使わず半角セルに合わせるCJK互換性方針。数値検査の合格をWindowsメモ帳での解消とは扱わない。変更前v2（平均1115）はこの検査で拒否されるため、比較用TTFを新しい `check` の合格対象にしない。

初回の正式ビルド結果は[正式ビルド検証記録](artifacts/v2-formal-build-2026-09-26/mac/report.md)、平均文字幅修正の実測とWindowsへの引き継ぎは[2026-09-28の記録](artifacts/notepad-metrics-2026-09-28/mac/report.md)を参照する。
