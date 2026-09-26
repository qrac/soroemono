# SOROEMONO

JetBrains Mono に対して BIZ UDGothic を 1:2 に調整して合わせたエディタ用の等幅フォント。JetBrains Mono のバランスはそのまま、日本語フォントだけ少し幅広にした JetBrains Mono 優先・JetBrains Mono 好きのための等幅フォント。

<img src="https://github.com/user-attachments/assets/110fa64e-b8d6-4d69-b960-b8b736fb72d9">

- 通常の英数字は JetBrains Mono の輪郭と600幅を維持
- 半角600・全角1200の文字送り（結合文字等には例外あり）

## How To Use

[Releases](https://github.com/qrac/soroemono/releases) の Assets から公開済みのzipファイルをダウンロードしてご利用ください。v2.0.0の正式ビルドはRegular、Bold、Italic、Bold Italicの4つの静的TTFを含みます。v1.0.0から更新するときは旧版を削除してから4ファイルをインストールし、アプリを再起動してください。Font Familyは `SOROEMONO` です。Italicの欧文はJetBrains Mono純正、日本語は9度の機械的な斜体です。

ソースからの正式ビルドは `uv run --locked soroemono release`。入力は `sources.lock.json` のハッシュで固定され、生成したZIPは `dist/` に置かれます。正式公開・Windows実アプリの受け入れ状況は[進捗](context/progress.md)を参照してください。

開発・検証の手順と現在の状態は[contextの索引](context/README.md)を参照してください。

## Respect

- [yuru7/udev-gothic](https://github.com/yuru7/udev-gothic)

## License

- SOROEMONO: licensed under the SIL OFL 1.1
- JetBrains Mono: licensed under the SIL OFL 1.1
- BIZUDGothic: licensed under the SIL OFL 1.1

## Credit

- Author: [Qrac](https://qrac.jp)
- Organization: [QRANOKO](https://qranoko.jp)
