# SOROEMONO

JetBrains Mono に対して BIZ UDGothic を 1:2 に調整して合わせたエディタ用の等幅フォント。JetBrains Mono のバランスはそのまま、日本語フォントだけ少し幅広にした JetBrains Mono 優先・JetBrains Mono 好きのための等幅フォント。

<img src="https://github.com/user-attachments/assets/110fa64e-b8d6-4d69-b960-b8b736fb72d9">

- 通常の英数字は JetBrains Mono の輪郭と600幅を維持
- Markdown のテーブルで Prettier の文字数計算と幅が揃う

## How To Use

[Releases](https://github.com/qrac/soroemono/releases) の Assets から zip ファイルをダウンロードしてご利用ください。ファイルをフォント管理ツールにインストール後、Font Family に `SOROEMONO` を入力すれば適応されます。

## Build

新しいビルドは **Regular/Boldの試作版** です。既存の見た目を基準に、半角幅・行間・ヒンティングの整合を修正しています。ファミリー名は `SOROEMONO Preview`。Mac/Windowsのブラウザ表示を確認済みですが、Windows実アプリでの既存Issuesの解消は未検証です。

```sh
uv sync --locked --extra proof
uv run --locked soroemono build
uv run --locked soroemono check
uv run --locked soroemono build --style Bold
uv run --locked soroemono check --style Bold
uv run --locked python -m unittest discover -s tests -v
```

出力は `build/preview/`。元フォントは同梱ファイルのSHA-256を確認して使い、ビルド中にダウンロードしません。

OSにインストールせず、公開v1.0.0と比較できます。

```sh
uv run --locked soroemono fetch-baseline
uv run --locked soroemono proof
uv run --locked soroemono proof --style Bold
uv run --locked playwright install chromium
uv run --locked soroemono capture
uv run --locked soroemono capture --proof build/proofs/bold
```

`build/proofs/regular/report.html` と `build/proofs/bold/report.html` はTTFを内包する比較ページ、`screenshots.html` は撮影結果です。旧版・新版・差分PNGと環境情報も同じ場所に保存します。既存Chromeで撮る場合は `capture --channel chrome` を使います。2026-09-23のMac/Windows確認結果は[検証記録](context/verification-2.0.0a1-2026-09-23.ja.md)を参照してください。

Windows 11での確認には、Parallels DesktopのCLIと共有フォルダを使う[プロジェクト用Skill](.agents/skills/soroemono-windows-check/SKILL.md)と[検証手順](context/windows-parallels.ja.md)を用意しています。Windows Chromeで両スタイルのブラウザ描画を確認しました。既存Issuesの実アプリでの解消は未検証です。既存のGitHub ActionsはUbuntuでの継続的なビルド・検査用として維持します。

[作業の状態と資料の索引](context/README.md) / [開発・検証手順](context/development.ja.md) / [再設計計画](context/rebuild-plan.ja.md) / [現行字形の基準](context/font-baseline.ja.md)

従来の `build.py` / `build.ini` は調査用に残しています。公開版を再現する手段としては使わず、通常の開発は上記コマンドを使ってください。

## Respect

- [yuru7/udev-gothic](https://github.com/yuru7/udev-gothic)

## License

- SOROEMONO: licensed under the SIL OFL 1.1
- JetBrains Mono: licensed under the SIL OFL 1.1
- BIZUDGothic: licensed under the SIL OFL 1.1

## Credit

- Author: [Qrac](https://qrac.jp)
- Organization: [QRANOKO](https://qranoko.jp)
