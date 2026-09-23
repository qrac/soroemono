# Regular/Bold試作の開発・検証

実装日: 2026-09-22。2026-09-23にBoldの生成・比較を追加。正式な2.0リリースではない。

## 実行

リポジトリ直下で実行する。開発・CIの既定Pythonは `.python-version` の3.14.6、依存ライブラリは `uv.lock`、元TTFと公開基準版は `sources.lock.json` で固定する。`pyproject.toml` の `requires-python = ">=3.12"` は対応下限を示し、既定版とは別に維持する。初回の環境構築・基準版取得・ブラウザ取得にはネットワークが必要。それ以降の生成と比較ページ作成はローカルで完結する。

```sh
uv sync --locked --extra proof
uv run --locked soroemono build
uv run --locked soroemono check
uv run --locked soroemono build --style Bold
uv run --locked soroemono check --style Bold
uv run --locked python -m unittest discover -s tests -v
uv run --locked soroemono fetch-baseline
uv run --locked soroemono proof
uv run --locked soroemono proof --style Bold
uv run --locked playwright install chromium
uv run --locked soroemono capture
uv run --locked soroemono capture --proof build/proofs/bold
```

取得済みの公開ZIPを使う場合は `fetch-baseline --archive /path/to/SOROEMONO_v1.0.0.zip`。アーカイブと中のRegular/Bold両TTFのハッシュを検査する。`build --output /path/to/directory`、`check --font /path/to/font.ttf`、`proof --font /path/to/font.ttf --output /path/to/proof`、`capture --proof /path/to/proof` で出力・検査先を指定できる。Boldの `build` / `check` / `proof` には `--style Bold` を付ける。リポジトリ外からはサブコマンドの前に `--root /path/to/soroemono` を付ける。

macOSの既存Chromeを使う場合は `capture --channel chrome`。新しい一時プロファイルを使い、日常のChromeのプロファイルは利用しない。OSへのフォント登録は行わない。

## 今回の実装

- fontTools中心の生成。通常のJetBrains Monoグリフ1,743個の輪郭・hmtx・グリフ命令を保持し、`fpgm` / `prep` / `cvt ` / `gasp` も元のJetBrains Monoと一致させる。
- BIZの採用範囲をcmapで決め、subsetterにGSUB・合成参照・IVSの依存先を残させる。加工するグリフは合成を展開して変形し、古いヒント命令を除去する。
- 全角は `x'=round(x*1080/2048+60)`、`y'=round(y*1000/2048)`、advance 1200。旧工程とは丸めと輪郭再生成が異なるので全座標の完全一致は保証しない。
- BIZ半角は元の500相当の輪郭サイズを保ち左右50を足してadvance 600。結合文字は別分類でadvance 0。U+FEFFも0幅を維持する。
- 全角波括弧U+FF5B/U+FF5DはBIZへ切替。U+26A1/U+FE62はJetBrains Monoの輪郭を複製し300移動して1200セルへ配置する。元のグリフは維持し、複製側のヒントは除去する。
- 日本語のGSUBは `ccmp, locl, jp78, jp83, jp90, hojo, nlck, trad, expt` に限定。エディタの等幅性と相容れないプロポーショナル・縦組み・幅切替は採用しない。ラテン側の機能は維持し、HarfBuzzで元フォントと比較する。
- BIZ由来の結合文字には追加GPOSを作成。かなの濁点は右上、追加IPAは結合クラスに応じた上・下・重ね合わせの暫定アンカー。かなの合成不能な例もproofへ入れる。IPA全組合せ、複数マークの積み重ねは受け入れ未完了。
- 行送りはhhea/Typoを1020/-300/0、USE_TYPO_METRICSを有効化。Winのクリッピング範囲は全グリフの外接矩形から計算する（今回1120/400）。結合後の全組合せのクリッピングまでは保証しない。
- 別ファミリー `SOROEMONO Preview`、両入力の著作権、OFL、入力・ツール情報を出力。TTFの時刻を固定し、同一環境の再ビルドをバイト比較する。
- Boldは固定したJetBrains Mono BoldとBIZ UDGothic Boldから同じ工程で生成する。Regularと同じファミリー・行メトリクスに、Boldの名前・ウェイト700・スタイルフラグを設定する。Mac/Windows画像比較は[2026-09-23の検証記録](verification-2.0.0a1-2026-09-23.ja.md)を参照。

## 出力

| 場所 | 内容 |
| --- | --- |
| `build/preview/` | Regular/Bold TTF、両OFL、`build.json` / `build-bold.json`、`checks.json` / `checks-bold.json` |
| `build/proofs/<style>/report.html` | 公開v1.0.0と試作版のTTF・OFLを内包する比較ページ。HTML単体をVMへコピー可能 |
| `build/proofs/regular/screenshots.html` | スクリーンショット一覧 |
| `build/proofs/regular/overview.png` | 旧版・新版の比較一覧 |
| `build/proofs/regular/before.png`, `after.png` | 同位置の比較領域の原寸画像 |
| `build/proofs/regular/diff.png` | 絶対画素差をグレースケール反転。白は一致。サイズ差は右・下を白で補う |
| `build/proofs/regular/details/` | 各比較項目の詳細画像 |
| `build/proofs/regular/manifest.json` | TTFハッシュ、Git状態、文字列、検査結果、OS・ブラウザ、表示条件、実使用フォント |

生成物・キャッシュ・仮想環境はGit管理外。比較ページはFont Loading APIの成功と実測幅を確認する。自動撮影ではさらにChromiumの実使用フォントを取得し、見本にシステムフォントのフォールバックがあれば失敗する。

`.github/workflows/preview.yml` はUbuntu 24.04でRegular/Boldの数値テスト、ビルド、基準版取得、ブラウザ撮影を行い、成果物を保存する設定。GitHub上での今回の変更後の実行は未確認。OSイメージの完全固定やコンテナによる画素回帰、リリース自動公開はまだ実装していない。

## 初回の確認結果

- macOS 26.6.2 / arm64、Chrome 153.0.8010.53、ヘッドレス、1200×1100 CSS px、deviceScaleFactor 1、ブラウザ倍率1。OSのDPIやWindowsの拡大率を模擬した結果ではない。
- 入力保持、再ビルド一致、500幅を故意に混入した場合の検出、不正ハッシュの拒否を含む4テストが合格。
- 通常cmap 12,442文字、IVS 10,160組。幅の内訳は1200が10,877、600が1,518、0が47。コードポイント単位で数え、0には結合文字とU+FEFFを含む。
- ブラウザ実測の100px表示: 旧版 `A=60, 日=120, ｱ=50px`、新版 `A=60, 日=120, ｱ=60px`。見本のフォールバックなし。
- 16px、4行、`line-height: normal` の高さは64pxから84pxへ変化。画像上でも旧版の詰まった行間から余裕が増えている。
- 日本語の大きさ・配置は従来の変換を基準に維持。今回確認した「元・日・あ・ア」のxMaxは旧版より1フォント単位小さい。例えば「元」は旧版x=87..1104、新版87..1103。半角「ｱ」の輪郭は旧版30..471から新版80..521へ移動し、横幅441は一致。
- 固定line-heightでも旧版と新版で描画のベースライン位置に画素差がある。これは行メトリクス変更とラスタライズを含む差で、diffの全画素一致を合格条件にはしない。英数字の輪郭・配置・ヒント保持は別途TTFの数値比較で確認している。
- ここまでが2026-09-22の初回結果。後続のRegular/BoldのMac/Windowsブラウザ検証結果は[2026-09-23の検証記録](verification-2.0.0a1-2026-09-23.ja.md)を参照。

その後のCLI接続調査（2026-09-23）では、`prlctl exec` でWindows内の読み取り専用コマンドを実行し、共有リポジトリを参照できた。`prlctl capture` によるデスクトップ撮影も成功した。Windows上のフォントproofと実アプリ表示は引き続き未実施。結果と次の操作手順は [Parallels DesktopによるWindows検証](windows-parallels.ja.md) に記録した。

次の受け入れ項目は、確立したCLI操作経路でこのHTMLをWindowsゲストに表示・撮影すること。その後にWindowsのVS Code・Terminal等、100/125/150/200%で確認する。Bold/Italic、Prettierの実整形、独立したOTS/FontBakery検査、正式ZIP、Nerd Fonts、全角スペース可視化は今後の範囲。

## Python 3.14.6への既定版変更（2026-09-23）

- macOS 26.6.2 / arm64 のPython 3.14.6で、ロック済みの通常・proof依存関係を別の仮想環境に導入し、unittest 4件すべて合格。Regularを独立した出力先に生成し、`check` も合格した。
- 3.12.11で生成した既存TTFと3.14.6で生成したTTFはSHA-256 `dbb57d5d8a634ecbb5527832ad52d8df06c5ea7b87be54dddedd9e052c549674` で一致し、バイト比較も一致した。検査値はUnicode 12,442文字、advance 0/600/1200が47/1,518/10,877、保持したラテン字形1,743、IVS 10,160組。`build.json` ではPython版記録が3.12.11から3.14.6、同梱Unicodeデータ版が15.0.0から16.0.0へ変わった。
- `build/proofs/python-3.14-verify/` に3.14.6生成TTFの比較proofを作成し、Chrome 154.0.8037.57で撮影した。OS、表示条件、TTFハッシュ、実使用フォント、旧版・新版・差分画像は同ディレクトリの `manifest.json` と各PNGに記録した。既存の3.12.11生成TTFの画像と、overview/before/after/diffの各画像は寸法・全画素が一致し、新旧Pythonで生成したTTFの表示差を `python-version-diff.png`（全白）に保存した。画像も目視確認した。
- CIの実行用uvは、3.14.6の取得に対応する0.12.17に更新した。uv 0.9.20は3.14.6を取得できず、0.12.17で取得可能と確認した。GitHub Actions上の実行は未確認。
