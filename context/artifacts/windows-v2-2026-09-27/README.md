# 2026-09-27 Windows 11検証の証跡

[検証記録](../../verification-v2-windows-2026-09-27.ja.md)に対応する、Windows 11 VMで撮影した確定画像と環境情報。元データはGit管理外の `build/proofs/windows-20260927/` に置いた。複製前後のSHA-256が一致することを確認した。各画像のSHA-256、画素数、TTFハッシュ、OS・アプリ・VMの情報は [manifest.json](manifest.json) と [inventory.json](inventory.json) に記録した。

| 対象 | 比較一覧・設定 | 公開v1.0.0 | 正式v2.0.0 | 差分 |
| --- | --- | --- | --- | --- |
| Chrome Regular | [overview](regular-overview-full.png) | [before](regular-before-full.png) | [after](regular-after-full.png) | [diff](regular-diff-full.png) |
| Chrome Bold | [overview](bold-overview-full.png) | [before](bold-before-full.png) | [after](bold-after-full.png) | [diff](bold-diff-full.png) |
| Chrome Italic | [overview](italic-overview-full.png) | [before](italic-before-full.png) | [after](italic-after-full.png) | [diff](italic-diff-full.png) |
| Chrome Bold Italic | [overview](bold-italic-overview-full.png) | [before](bold-italic-before-full.png) | [after](bold-italic-after-full.png) | [diff](bold-italic-diff-full.png) |
| Windows Terminal | 同じ20のフォント設定 | [全画面](windows-terminal-v1-200.png)・[詳細](windows-terminal-v1-detail-200.png) | [全画面](windows-terminal-v2-200.png)・[詳細](windows-terminal-v2-detail-200.png) | [詳細差分](windows-terminal-diff-detail-200.png) |
| Windows メモ帳 | Regular、20、ズーム100% | [全画面](notepad-v1-200.png)・[詳細](notepad-v1-detail-200.png) | [全画面](notepad-v2-200.png)・[詳細](notepad-v2-detail-200.png) | [詳細差分](notepad-diff-detail-200.png) |
| VS Code | 同じ使い捨て設定 | [エディタ](vscode-editor-v1-200.png)・[ターミナル](vscode-terminal-v1-200.png) | [エディタ](vscode-editor-v2-200.png)・[ターミナル](vscode-terminal-v2-200.png) | 画面配置が異なるため画素差分は作成しない |

「元」のヘッドレスChrome比較は[詳細画像](regular-glyphs-headless-detail.png)、OS拡大率200%の対話Chromeは[画面](regular-overview-interactive-200.png)を参照。v2のメモ帳が4スタイルを列挙した画面は[こちら](notepad-v2-four-styles-200.png)。Italic系のbeforeは公開版の直立Regular/Boldであり、公開版にItalicは含まれない。

メモ帳で見つかった日本語の送り拡大について、正式v2 Regularのメタデータだけを変更した対照画像を残した。`post.isFixedPitch` だけ0にした[post0](notepad-v2-post0-detail-200.png)と `OS/2.panose.bProportion` だけ0にした[panose0](notepad-v2-panose0-detail-200.png)は正式v2の詳細画像と画素一致した。両方0にした[mono0](notepad-v2-mono0-detail-200.png)では日本語の送りが公開版に近い約63pxへ戻り、v2の行間は維持された。[正式v2とmono0の差分](notepad-v2-mono0-diff-detail-200.png)も参照。試験用TTFのハッシュと変更項目はmanifestに記録した。試験用TTFそのものは保存版や正式配布物に含めない。

Windows Terminalの詳細差分は、ウィンドウ全体の配置差を避けるため、先頭の試験行の位置を合わせた同サイズの領域から作った。メモ帳の詳細差分は両画像の同じ画面座標を切り出したもの。差分は画素変化の位置を示し、不具合の合否や原因を単独では示さない。ヘッドレスChromeと対話Chromeは撮影条件が異なるので、直接の画素比較には使わない。

一時的な画面、設定前のメモ帳、試験用TTF、TTFを内包するHTML、撮影補助スクリプトは保存版に含めない。VMは検証後に試験前のスナップショットへ戻した。
