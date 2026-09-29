# Issue #2・メモ帳の日本語送り: Windows 11 再検証

検証日: 2026-09-28〜29。対象は `v2` のコミット `43a1a92bb8b44962ebba8dfa9f26788144d2b05a`、修正コミットは `824915f`。この記録は [Mac 側の修正・検証](../mac/report.md) と [前回の Windows 実アプリ検証](../../windows-v2-2026-09-27/win/report.md) に続くもの。Windows 側ではソースを変更していない。検証開始時の HEAD は `43a1a92`。検証中にローカル HEAD は Windows 証跡のみを含む `5a9a7b988c7223fc4bc91c7608b03f12a309c1c7` へ進んだが、`src/` や依存関係に差分はない。後者を検証対象コミットと読み替えない。画像、試験文、環境、SHA-256 は [manifest](manifest.json) にまとめた。

## 結果

**メモ帳の Regular・サイズ20・ズーム100%・OS拡大率200%では、修正前 v2 の日本語文字送り拡大を再現し、今回の TTF で解消を確認した。** 行送りは修正前後で一致し、前回確認した v2 の広い行間を維持した。結合後の TTF で `OS/2.xAvgCharWidth` のみ 1115 から 600 に変えたときに現れる表示差である。メモ帳内部がこの値を直接使うかは調べていない。

| メモ帳画像の実測（論理 px） | 修正前 v2 | 修正後 v2 |
| --- | ---: | ---: |
| 1行目の連続する「元元」の上線左端 | x=94, 153 | x=67, 99 |
| その2文字の送り | 約59px | 約32px |
| 同じ「元」の上線位置（1・3・5・7行目） | y=103, 173, 243, 313 | y=103, 173, 243, 313 |

画像は Windows 画面の論理ピクセルで保存した。OS拡大率200%なので、連続する「元」の送りは物理画素換算で約118pxから64px。後者は[公開 v1 の前回画像](../../windows-v2-2026-09-27/win/report.md#メモ帳で見つかった文字間の回帰)の約63物理pxに近い。2行おきの上線位置差70論理pxから、隣接行の送りは前後とも約35論理px（約70物理px）。これは画像上の配置測定で、メモ帳が内部で返す行高・文字幅ではない。

- [修正前の原寸画面](notepad-before.png) / [修正後の原寸画面](notepad-after.png)
- [同じ領域の並列比較](notepad-comparison.png) / [先頭2行の画素差分](notepad-diff.png)
- [修正前のメモ帳設定](notepad-settings-before.png) / [修正後のメモ帳設定](notepad-settings-after.png)

## 対象と手順

- ユーザーが `build/formal/SOROEMONO-Regular.ttf` を対象コミットからビルドした。Windows 側でファイルの SHA-256 `209cb5666ab6ec80f8270d954565920bcc185cf8d4c3adc049419b78486afc43` を再計算し、[Mac 側の候補](../mac/report.md#macでの検証結果)と一致した。`build/formal/checks-regular.json` は `passed: true`、`xAvgCharWidth=600`、`isFixedPitch=1`、`panose.bProportion=9`、HarfBuzz 14.5.0 と記録している。Codex の隔離プロセスからユーザー所有の `.venv` が読めず、単体テストはこの Windows セッションでは実行できなかった。
- 比較元は修正後の TTF の `OS/2.xAvgCharWidth` を 1115 に戻し、テーブルとフォント全体のチェックサムを再計算した。SHA-256 `56f46b6042efc0911317895aa7dbcd281af3f4ba129925316d8422f96e6b1ea1` が、[前回の正式 v2 の現物](../../windows-v2-2026-09-27/win/manifest.json)と一致した。生成スクリプトと TTF は Git 管理外の `build/issue2-windows-20260928/` に置き、証跡ディレクトリへは入れていない。`hmtx`、字形、行間のテーブルは変更していない。
- ユーザーの指示に従い、復元スナップショットは使わなかった。修正後と修正前を順に現在のユーザーへ一時インストールし、各回に `C:\Users\qrac\AppData\Local\Microsoft\Windows\Fonts\SOROEMONO-Regular.ttf` の SHA-256 を対象 TTF と照合した。版の切替時はフォントをアンインストールし、メモ帳を終了・再起動した。同名フォントの重複登録は避けた。
- 同じ `sample.txt` をメモ帳 11.2607.14.0 で表示した。設定は両回とも `SOROEMONO` / Regular / サイズ20、ズーム100%、折り返し・書式設定オン。2行の試験文を4回繰り返し、ASCII、全角、半角カナを混在させた。試験文のハッシュと全画面画像のハッシュは [manifest](manifest.json) を参照。
- Windows 11 25H2、ビルド 26200.9457、ARM64 の Parallels VM。DPI-aware プロセスでシステム DPI 192、物理解像度 3200×1724 を読み、OS 拡大率200%を確認した。フォントスムージング有効、ClearType (`SystemParametersInfoW` の type 2)。物理 DPI と仮想 GPU、Parallels Tools の現行版は未取得。保存したメモ帳ウィンドウ画像は 1190×587 論理px。

## Windows ブラウザ proof

OSへフォントを再登録せず、SHA-256を照合した2つのTTFを `data:font/ttf` としてローカルHTMLへ埋め込み、Windows の Chrome 154.0.8037.58 をヘッドレスで実行した（[原寸画面](browser-proof.png)）。HTML は Git 管理外の `build/issue2-windows-20260928/` に置いた。画面に `Before=loaded, After=loaded` が表示され、各フォントで 100 CSS px の `A=60 / 日=120 / ｱ=60` を測定した。`line-height: normal` の4行見本も両者で同じ表示。見本部分の同一領域を225pxずらして比較すると画素差はなかった（切り出し座標は [manifest](manifest.json)）。HTML の FontFace 読み込み成功と表示幅を確認したが、CDP の実使用フォント照会は実行していない。Chrome の device scale factor も未測定。この proof は Regular のみで、Mac 側の4スタイル proof に追加する Windows 確認である。

## 後片付けと判定範囲

試験後は修正前 TTF もアンインストールした。ユーザー別 Fonts の同名ファイルは存在せず、Windows の Fonts 一覧で `SOROEMONO` の検索結果は0件（[画像](font-uninstalled.png)）。メモ帳の設定を検証前の `Merged Yaku Han JP` / Black / サイズ20 に戻し（[画像](notepad-settings-restored.png)）、試験用 `sample.txt` タブを閉じた。スナップショットは戻していない。`build/` の生成物と本報告は残している。この継続作業で追加したブラウザ画像・manifest・報告追記は未コミットで、エージェントはコミット・pushしていない。

今回の**メモ帳での回帰は解消確認**。Issue #2 の元の行間問題は、前回の Windows Terminal、VS Code ターミナル、メモ帳の比較で v2 の改善を確認済み。今回の変更は TTF の平均文字幅とチェックサムだけで、行間メトリクスは維持された。ただし、今回の修正後 TTF を Windows Terminal と VS Code ターミナルで再撮影していないため、現コミットの3アプリすべての実表示を再確認したとはしない。Regular の Windows ブラウザ直接読込は上記のとおり確認した。固定 Python 環境へのアクセス制限によりプロジェクト既定の `soroemono capture` は実行できず、Chrome CLI で別ページを撮影した。Mac 側の4スタイル proof は別記録であり、この Windows の Regular 結果を他スタイルへ拡張しない。メモ帳の内部で実際に選ばれたグリフを API で照会していないため、ファミリー設定、登録先 TTF ハッシュ、修正前後の意図した差を合わせた検証である。今回の Regular 以外のスタイル、別の文字サイズ・倍率も未確認。
