# SOROEMONO

JetBrains Mono に対して BIZ UDGothic を 1:2 に調整して合わせたエディタ用の等幅フォント。JetBrains Mono のバランスはそのまま、日本語フォントだけ少し幅広にした JetBrains Mono 優先・JetBrains Mono 好きのための等幅フォント。

<img src="https://github.com/user-attachments/assets/110fa64e-b8d6-4d69-b960-b8b736fb72d9">

- JetBrains Mono はオリジナルのまま
- Markdown のテーブルで Prettier の文字数計算と幅が揃う

## How To Use

[Releases](https://github.com/qrac/soroemono/releases) の Assets から zip ファイルをダウンロードしてご利用ください。ファイルをフォント管理ツールにインストール後、Font Family に `SOROEMONO` を入力すれば適応されます。

## Build

```sh
$ brew install fontforge
$ fontforge -script build.py
```

## Respect

- [yuru7/udev-gothic](https://github.com/yuru7/udev-gothic)

## License

- SOROEMONO: licensed under the SIL OFL 1.1
- JetBrains Mono: licensed under the SIL OFL 1.1
- BIZUDGothic: licensed under the SIL OFL 1.1

## Credit

- Author: [Qrac](https://qrac.jp)
- Organization: [QRANOKO](https://qranoko.jp)
