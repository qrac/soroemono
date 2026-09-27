# v2.0.0正式ビルドのWindows 11検証

記録日: 2026-09-27。対象は[正式ビルド検証記録](../../v2-formal-build-2026-09-26/mac/report.md)で生成したローカルの `SOROEMONO_v2.0.0.zip`。公開v1.0.0の現物と比較した。これはGitHub Releasesへのv2.0.0公開を示す記録ではない。撮影画像と環境の保存版は[証跡](README.md)、ファイル別SHA-256は[manifest](manifest.json)を参照。

## 環境と手順

- Parallels Desktop 27.0.2 (58673)、Parallels Tools 27.0.2-58673の `Windows 11` VM。Windowsビルド `10.0.26200.9457`。Chrome 154.0.8037.57、VS Code 1.104.0、Windows Terminal 1.24.11911.0、Windows メモ帳 11.2606.15.0。
- Windowsの論理解像度1600×862、OS拡大率200%（`LogPixels=192`）、保存画像3200×1724。ClearTypeは `FontSmoothing=2` / `FontSmoothingType=2`。ブラウザproofのヘッドレス画像は1600×2200pxで、device scale factorは未測定。対話ChromeのOS拡大率は200%。フォント描画の細かな設定、仮想GPU型番、物理DPIは未取得。
- 公開v1.0.0はリリースの実物から保全したRegular/Boldを使用した。SHA-256はRegular `83994897f9a4ee58cab502861f47718b4638b1836e379e1479035b4a664ea8d3`、Bold `320f342c6517885d5358251f231b4c0bf09049095caf35f46bcacf604c950f84`。リポジトリ内の旧 `dist/` ZIPやGit履歴上の `build.py` から再生成したものは比較基準にしていない。
- v2.0.0 ZIPのSHA-256は `603ed8c7197a20ef3827191253bcdf65b8f3f3fa3d821abfc62af401ee0c918c`。4スタイルのTTFハッシュは[manifest](manifest.json)に記録した。ブラウザproofは両版のTTFを `FontFace` で直接読み、4スタイルの `overview` / `before` / `after` / `diff` を撮影した。全overviewで読込・幅検査の成功表示を確認した。Windowsでの実使用フォントAPI照会は未実施。
- VMに復元用スナップショットを作り、公開版と新版を別々の復元サイクルでログイン中の `qrac` ユーザーへ試験登録した。`prlctl exec --current-user` を使用し、ユーザー別フォントレジストリとTTFのハッシュ、GDIのファミリー認識を確認した。MacのOSにはフォントを登録していない。実アプリの撮影後、スナップショットへ復元し、VMを当初の `paused` 状態に戻した。

## Issueごとの結果

| Issue | 今回確認できた事実 | 判定 |
| --- | --- | --- |
| [#2 行間](https://github.com/qrac/soroemono/issues/2) | Windows Terminal、VS Codeのターミナル、Windows メモ帳で同じ試験文を公開版と新版で表示。OS拡大率200%の画像では3アプリとも新版の行送りが広がった。メモ帳のRegular・サイズ20・ズーム100%では、画像上の繰り返し行の間隔が約53pxから70pxになった。一方、正式v2のメモ帳では連続する「元」の水平送りが公開版の約63pxから118pxへ広がる意図しない差も見つかった。 | 行間改善は確認。メモ帳の文字間の回帰が残るため、Issue全体の受け入れは保留。 |
| [#5 イタリック](https://github.com/qrac/soroemono/issues/5) | v2はJetBrains Mono由来のItalic/Bold Italicを含む4スタイル。WindowsのGDI `FontFamily.IsStyleAvailable` が4件とも `True`、メモ帳のスタイル一覧もRegular / Italic / Bold / Bold Italicを列挙。Chromeの4スタイルproofでItalic系の字形を目視した。 | 生成、Windowsでの認識、ブラウザ描画を確認。VS Code等の自動スタイル切替は未撮影。 |
| [#6 「元」の欠け](https://github.com/qrac/soroemono/issues/6) | WindowsヘッドレスChromeの比較画像では公開版の「元」の上部が欠け、新版では正常に見える。一方、OS拡大率200%の対話Chromeと実アプリでは、公開版でも同じ欠けを再現できなかった。 | ヘッドレスChrome条件での改善を確認。報告条件の100%/200%での再現と解消判定は未完了。 |

### #2 の実アプリ画像

Windows Terminalの[公開版](windows-terminal-v1-detail-200.png)と[新版](windows-terminal-v2-detail-200.png)は、同じフォントサイズ20、同じサンプルで撮影した。サンプル先頭を揃えた[画素差分](windows-terminal-diff-detail-200.png)も保存した。VS Codeは両版とも使い捨てプロファイル、拡張無効、`editor.fontSize=20`、`editor.lineHeight=0`、`terminal.integrated.fontSize=20`、`terminal.integrated.lineHeight=1`。ターミナルの[公開版](vscode-terminal-v1-200.png)と[新版](vscode-terminal-v2-200.png)で行送りの差が見える。エディタ画像も[公開版](vscode-editor-v1-200.png)と[新版](vscode-editor-v2-200.png)を残した。

メモ帳のフォント設定は両版とも `SOROEMONO`、Regular、サイズ20、ズーム100%。[公開版](notepad-v1-detail-200.png)は行が詰まり、[新版](notepad-v2-detail-200.png)では行間が見える。[同じ画面領域の差分](notepad-diff-detail-200.png)を保存した。約53→70pxは画像の先頭「元」の水平線が2行ごとに並ぶ位置から求めた物理画素上の値。アプリ内の行高設定値や他の拡大率を示す数値ではない。3アプリともフォント指定、ユーザー別登録と画面表示を照合したが、アプリ内部の使用フォントを直接返すAPIでは照会していない。

#### メモ帳で見つかった文字間の回帰

同じ画像の1行目で、連続する「元元」の上線左端は公開版でおよそx=113, 176、新版でx=168, 286にあり、送りは約63pxから118pxへ広がった。これは字形の外接幅ではなくメモ帳画像上の配置差である。TTF内の `hmtx` は両版とも「元」1200、「A」600で変わらない。VS Codeエディタでは同様の横方向の拡大は見られず、アプリ依存の表示差として扱う。

原因候補を絞るため、正式v2 Regularからメタデータだけを変えた試験用TTFを3種類作り、VMを毎回スナップショットへ戻してメモ帳を撮影した。正式v2は `post.isFixedPitch=1`、`OS/2.panose.bProportion=9`、公開版は両方0。`post` だけ0にした[画像](notepad-v2-post0-detail-200.png)とPANOSEだけ0にした[画像](notepad-v2-panose0-detail-200.png)は、正式v2の同じ切り出し領域と画素一致した。両方0にした[画像](notepad-v2-mono0-detail-200.png)では連続する「元」の送りが約63pxへ戻り、約70pxの行間は残った。[正式v2との差分](notepad-v2-mono0-diff-detail-200.png)も保存した。各試験用TTFでは変更対象の `post` / `OS/2` と再計算される `head` 以外のコンパイル済みテーブルが正式v2と一致することを検査した。TTFハッシュと変更値は[manifest](manifest.json)に記録した。メモ帳内部の分岐は直接確認できておらず、2項目の組み合わせが表示に関係するという段階の推定である。両方0にした版のターミナルでの認識・行間・文字幅や他スタイルは未検証で、修正版として採用していない。正式v2 ZIPは変更していない。

### #5 と #6 の画像

メモ帳の[4スタイル一覧](notepad-v2-four-styles-200.png)とChromeの[Italic](italic-overview-full.png)・[Bold Italic](bold-italic-overview-full.png)を確認した。公開版はItalic系を含まないため、ChromeのItalic系beforeは直立Regular/Boldとの比較である。

「元」は[ヘッドレスChromeの詳細](regular-glyphs-headless-detail.png)で公開版の欠けと新版の改善を確認した。[対話Chromeの200%画面](regular-overview-interactive-200.png)では公開版の同じ欠けが見えない。ヘッドレスChromeのdevice scale factorは未測定なので、この画像をOS拡大率100%での再現証拠とは扱わない。今回のVMでOS拡大率100%、125%、150%は未実施。原因を `gasp` のみに特定する根拠も得ていない。

## 残る確認

- #2のメモ帳における日本語の送り拡大の原因を確定し、他アプリの等幅認識と行間改善を維持する修正を検証する。現状の正式v2を文字間も含めて合格とは判定しない。
- #6を報告どおりWindows実アプリ・OS拡大率100%/200%で再現する条件の特定と、新版での同条件比較。200%では公開版の欠けを再現できていない。
- #5のVS Code等における自動Italic/Bold Italic切替の実表示。今回確認したのはWindowsによる4スタイル列挙とChromeの各スタイル描画。
- OTS/FontBakery、CIの実行結果、他OSでの最終受け入れと配布公開は別の作業として残る。
