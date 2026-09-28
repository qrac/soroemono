# メモ帳の日本語送り回帰: 平均文字幅の修正候補

記録日: 2026-09-28。[参照会話「原因分析: メモ帳の日本語字間拡大」](chatgpt-conversation://6ab92e4d-a9c0-83e8-9428-d6ea68a07bb3)の後半で挙がった `xAvgCharWidth` を調査し、Mac側で修正・検証した。Windowsテストはユーザーの指定により行っていない。**メモ帳での解消とIssue #2の受け入れは未確認**。

## 調査と判断

変更前はコミット `ff26ca177117fa8edfb47d2a8e14f6bf7b12ea88` のコードから4スタイルを再生成した。TTFのSHA-256は[正式ビルドの記録](../../v2-formal-build-2026-09-26/mac/report.md)と一致する。公開v1.0.0の現物も引き続き比較基準にした。

| フォント | UPM | A / 元 / ｱ の送り | xAvgCharWidth | isFixedPitch | bProportion |
| --- | ---: | --- | ---: | ---: | ---: |
| 公開SOROEMONO v1.0.0 Regular | 1000 | 600 / 1200 / 500 | 1123 | 0 | 0 |
| 変更前SOROEMONO v2、4スタイル共通 | 1000 | 600 / 1200 / 600 | 1115 | 1 | 9 |
| UDEV Gothic v2.2.0 Regularの配布TTF | 2048 | 1024 / 2048 / 1024 | 1024 | 1 | 9 |
| 今回の修正候補、4スタイル共通 | 1000 | 600 / 1200 / 600 | 600 | 1 | 9 |

UDEV Gothicは[固定タグv2.2.0の実装](https://github.com/yuru7/udev-gothic/blob/v2.2.0/fonttools_script.py)と[設定](https://github.com/yuru7/udev-gothic/blob/v2.2.0/build.ini)、[公開ZIP](https://github.com/yuru7/udev-gothic/releases/tag/v2.2.0)を照合した。通常の1:2版は平均文字幅を半角セル1024に設定している。今回取得したZIPのSHA-256は `c104c171f6ed8922ca52d74cd915a271e427f1e884e51431aae71d99e8b3b47b`、Regular TTFは `25fa0eca4be611ac125f03411d280c85494153da01dfa02ba734399c05f6289d`。比較用データはGit管理外の `build/notepad-metrics-2026-09-28/reference/` に置き、SOROEMONOのビルド入力には加えていない。

fontTools 4.64.0の `Merger._postMerge()` は `OS/2.recalcAvgCharWidth()` を呼ぶ。これにより、SOROEMONOは合成後の非ゼロ幅グリフの平均1115となっていた。従来の `metadata()` はその値を上書きしていなかった。UDEV GothicとSOROEMONOの `ulUnicodeRange1..4` および `ulCodePageRange1..2` は同値だった。PANOSEの他の分類値、UPM、グリフ数、hhea/maxp/head、cmapの構成等には差があるが、収録字形や工程も異なるのでそのまま転用しない。テーブル別の実測値とハッシュは[数値比較](metrics-comparison.json)に保存した。

**原因候補:** メモ帳が等幅フォントのセル幅に `xAvgCharWidth` を使っている可能性。`1115 / 600 ≈ 1.858` は[前回のWindows画像](../../windows-v2-2026-09-27/win/report.md)の約 `118 / 63 ≈ 1.873` と近い。前回は等幅メタデータを両方0にすると送りが戻った。これらは仮説を支持するが、メモ帳内部のAPIや分岐を確認したものではなく、UDEV Gothicのメモ帳動作も今回実測していない。

[MicrosoftのOS/2仕様](https://learn.microsoft.com/en-us/typography/opentype/spec/os2#xavgcharwidth)では現在の定義は非ゼロ幅グリフの算術平均で、アプリがこの値から個々の文字送りを決めることは推奨されない。一部CJKフォントが平均の約半分を設定していることも記載されている。したがって1115を算術計算の誤りとは扱わず、今回の600は**1:2のCJKフォントとしての互換性方針**とする。仕様が600を必須としているわけではない。

## 実装範囲

- `builder.metadata()` で合成後の `OS/2.xAvgCharWidth=600` と `panose.bProportion=9` を明示する。`post.isFixedPitch=1` は維持する。
- `check` は生成済みTTFから3項目を読み、600 / 1 / 9を要求する。build/checkのJSONにも実測値を記録する。
- 1115への逆戻りと、等幅フラグ各項目を0へ変更したTTFを検査が拒否する回帰テストを追加する。既存の4スタイル・ZIPのテストでも新しい検査を通す。
- 字形、hmtxの送り、ヒント、cmap/IVS、GSUB/GPOS、行間、スタイル名は変更しない。

## Macでの検証結果

対象は上記コミットに今回の未コミット修正を加えた作業ツリー。ビルド・検査・テストのソースファイルおよびロックのSHA-256を[数値比較](metrics-comparison.json)へ記録した。後から文書をコミットしたHEADを、撮影時のコミットと読み替えない。

- `uv sync --locked --extra proof` を実施。Python 3.14.6、fontTools 4.64.0、HarfBuzz 14.5.0、uv 0.9.20。既存の `.venv` と固定依存関係を使用し、ロックファイルは変更していない。通常のサンドボックス内ではuvのキャッシュアクセス／macOSシステム設定の初期化とChrome起動が失敗したため、uv同期・テストと一時プロファイルのChrome撮影は権限を拡張して実行した。ブラウザはTTFを直接読み込み、OSへのフォント登録は行っていない。
- `uv run --locked python -m unittest discover -s tests -v`: **7件合格**（[ログ](tests.txt)）。旧平均1115と各等幅フラグの破損検出、4スタイルの数値・シェーピング検査、TTF再生成とZIP再生成のバイト一致を含む。
- `.venv/bin/python -m soroemono.cli release --output build/notepad-metrics-2026-09-28/release` で検証用ZIPを別出力先へ作成した。ZIPのCRC検査も合格。SHA-256は `b137decc684a1dcb1921ad7b38e6b4acf54ba95c2e9b4b451c312045a5f01043`。既存の `build/formal/` や `dist/` は上書きしていない。
- ZIPから取り出した4スタイルを変更前TTFと全テーブルの生バイトで比較した。差は **`OS/2.xAvgCharWidth` と `head.checkSumAdjustment` だけ**。OS/2のオフセット2〜3とheadの8〜11を除いたバイト一致も確認した。全字形・送り・ヒント・cmap・レイアウト・行間・名前のバイナリは維持される。
- 変更前と変更後それぞれを `make_proof()` / `capture_proof(channel="chrome")` で撮影し、双方のv2側見本を同じ領域で比較した。macOS 26.6.2 / arm64、Chrome 154.0.8037.57、ヘッドレス、1200×1100 CSS px、deviceScaleFactor 1、ブラウザ倍率1、既定ラスタライズ。物理DPIは未取得。各フォントの読み込みとCDPの実使用フォント検査が成功し、見本のフォールバックはなかった。
- **4スタイルとも変更前後の画像が画素一致**（1096×1101px、差分領域なし）。100pxでの `A=60 / 日=120 / ｱ=60px` と、16px・通常行送りの4行見本84pxを維持した。公開v1との比較も併存させた。4スタイルの一覧、Regularの前後切り抜きと白一色の差分を目視し、予期しない表示差はなかった。

| スタイル | 修正後TTF SHA-256 |
| --- | --- |
| Regular | `209cb5666ab6ec80f8270d954565920bcc185cf8d4c3adc049419b78486afc43` |
| Bold | `3c58fc099294e4a2f5bac0b30c638927ede87afbdb96bfecdc5c75a6234f5e87` |
| Italic | `15a03a7486788baec0b9687579130e4fbaa7de0c5f351549692ac280fac72ea2` |
| Bold Italic | `4c8b510b284a9f2314dc7300dc8843e36434f611a5f7759be73f0a630683b071` |

次の「前・後」は公開v1との比較ではなく、今回の平均文字幅修正前v2と修正後v2の比較。「公開v1比較」だけは公開Regular/Boldを基準とし、Italic系の比較元は直立字形。

| スタイル | 修正前v2 | 修正後v2 | 差分 | 公開v1比較 | 環境・ハッシュ |
| --- | --- | --- | --- | --- | --- |
| Regular | [前](regular/before.png) | [後](regular/after.png) | [差分](regular/diff.png) | [一覧](regular/public-v1-overview.png) | [manifest](regular/manifest.json) |
| Bold | [前](bold/before.png) | [後](bold/after.png) | [差分](bold/diff.png) | [一覧](bold/public-v1-overview.png) | [manifest](bold/manifest.json) |
| Italic | [前](italic/before.png) | [後](italic/after.png) | [差分](italic/diff.png) | [一覧](italic/public-v1-overview.png) | [manifest](italic/manifest.json) |
| Bold Italic | [前](bold-italic/before.png) | [後](bold-italic/after.png) | [差分](bold-italic/diff.png) | [一覧](bold-italic/public-v1-overview.png) | [manifest](bold-italic/manifest.json) |

各ディレクトリの `before-capture.json` / `after-capture.json` は公開v1と各v2を撮影した元manifest。`manifest.json` はそこからv2同士の対応を明示した比較記録。`comparison-detail.png` は原寸画像の同一領域を上=修正前・下=修正後に連結したもの（クロップ座標はmanifest）。TTF・ZIP・TTF内包HTMLはGit管理外の `build/notepad-metrics-2026-09-28/` に保持する。

## Windows側への引き継ぎ

今回はWindowsのビルド・ブラウザ・実アプリ操作・フォント登録を実施していない。次の検証は[Windows検証・Git受け渡し手順](../../../windows-verification.ja.md)に従い、Windows側の独立cloneで行う。

1. 修正コードの対象コミットを記録して `uv sync --locked --extra proof`、`uv run --locked python -m unittest discover -s tests -v`、`uv run --locked soroemono release` を実行する。各TTFハッシュを本記録と照合する。ZIPは環境情報も含むため、OS間の比較はまずTTFハッシュを用いる。
2. 4スタイルのブラウザproofで読み込み、半角600 / 全角1200、通常行送りを確認する。
3. 復元可能な隔離環境で、変更前v2と修正候補を別々に登録してメモ帳を再起動する。同名・同バージョンのため、登録先TTFのSHA-256を必ず照合する。変更前は上記 `ff26ca1…` を別checkoutで生成するか、前回のハッシュと一致する保全TTFを使う。新しい `check` が変更前1115を拒否するのは意図した動作。
4. 前回と同じメモ帳のRegular・20pt・ズーム100%・OS拡大率200%で「元元」とASCII混在行を比較する。日本語の送りが公開版に近い約63pxへ戻るか、約70pxの行送りを維持するか確認し、修正前・後・差分を保存する。これらのpx値は前回画像の目安であり、異なる版・DPI・文字サイズに固定しない。Bold/Italic/Bold Italicでも600/1200の関係と字形を確認する。
5. Windows TerminalとVS Codeのターミナル・エディタで、フォントの認識、1:2のセル、行間に回帰がないか確認する。メモ帳で未改善なら、600 / 1 / 9の登録を確かめたうえで結果を報告する。自動的に0 / 0へ切り替えない。

結果は新しい `context/artifacts/<run-id>/win/` に保存する。Issue #5の自動斜体切替、#6の欠け、配布公開は、この修正による解消とは扱わない。
