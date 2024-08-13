# SOROEMONO

JetBrains Mono に対して BIZ UDGothic を 1:2 に調整して合わせたエディタ用の等幅フォント。JetBrains Mono のバランスはそのまま、日本語フォントだけ少し幅広にした JetBrains Mono 優先・JetBrains Mono 好きのための等幅フォント。

- JetBrains Mono はオリジナルのまま
- Markdown のテーブルで Prettier の文字数計算と幅が揃う

## Build

```sh
$ brew install fontforge
$ fontforge -script build.py
```

## Font Family

```
SOROEMONO, ...
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
