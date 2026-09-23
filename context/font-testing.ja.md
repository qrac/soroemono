# インストール不要・仮想環境でのフォント検証計画

ユーザーの日常環境のフォントを差し替えず、エージェントが検証し、変更前・変更後・差分のスクリーンショットを提出する運用にする。以下は検証全体の設計。初回実装ではTTF内包HTML、Playwright撮影、フォールバック検出、環境記録を実装し、macOSで実行した。2026-09-23にWindows VM内のRegular/Boldブラウザ描画も確認した。結果は[検証記録](verification-2.0.0a1-2026-09-23.ja.md)。Windows実アプリでの受け入れは未実施。実行手順は [開発・検証手順](development.ja.md)、Windowsの接続と検証手順は [Parallels DesktopによるWindows検証](windows-parallels.ja.md) を参照する。

1. **日常の比較は、TTFを直接読むブラウザで行う**

   HTMLの `@font-face` またはFontFace APIで、公開v1.0.0と試作TTFをファイルから読み込む。OSのフォント一覧への登録は不要。CSS上で別ファミリー名を付け、同じページに並べて表示する。参照URLにファイルのSHA-256を含め、`local()` によるインストール済みフォントの選択を避ける。[CSS Font Loading API](https://developer.mozilla.org/en-US/docs/Web/API/CSS_Font_Loading_API)

   Playwrightで撮影と画像比較を自動化し、固定したLinuxコンテナを通常の回帰検査に使う。macOS上でも同じHTMLを読み込めばインストールせずに比較できる。ただしブラウザの隔離コンテキストはOSの仮想化ではない。各OSの描画確認には、そのOS上での実行が必要になる。[Playwright Docker](https://playwright.dev/docs/docker)

   撮影前に個別のFontFace.load()の成功、document.fonts.ready、必要文字のcmap/IVS収録を確認する。読み込み失敗はエラーにする。可能な環境では実際に使われたフォントも調べ、フォールバックによって偶然正常に見えるケースを除外する。通常字形を保つ試験では `font-synthesis: none` とし、意図しない擬似太字・斜体を使わせない。

   行間の試験には `line-height: normal` を使う。字形比較用の固定行間の見本も併設するが、固定行間だけでIssue #2の修正を判定しない。リガチャ・字形切り替えはON/OFFを明示し、字間の追加や表示倍率で幅の問題を隠さない。

2. **Windowsの問題は、Windows 11 VMで確認する**

   スナップショットに戻せるWindows 11 VMを、#2/#6の受け入れ検証環境にする。OSビルド、ブラウザ・アプリの版、画面解像度、DPI、ClearType、仮想GPU、リモート接続の有無を記録する。比較元と変更後は同じ環境・同じ設定で撮影する。

   WindowsブラウザでもTTFの直接読み込みを使う。VS Code、Windows Terminal、メモ帳を試す場合は、VM内だけへ試験フォントを登録し、使い捨てのアプリ設定で起動・撮影する。フォント更新後はアプリを起動し直す。検証後はスナップショットに戻す。ユーザーの日常OSにインストールしたり、既存フォントを削除したりする必要はない。

   自作のDirectWrite検証アプリであれば、Custom Font Collectionによりシステムへインストールせずに描画できる。ただし、それだけではWindows Terminal等のフォント列挙・選択・スタイル認識まで検証したことにはならない。[DirectWrite公式資料](https://learn.microsoft.com/en-us/windows/win32/directwrite/custom-font-collections)

   Windowsホストを使える場合はWindows Sandboxも候補になる。読み取り専用の入力フォルダ、結果出力フォルダ、LogonCommandを設定できる。ただしmacOS上でそのまま動く仕組みではないため、このMacからの作業は別途利用できるWindows 11 VMまたはリモート実行環境を用意する設計にする。[Windows Sandbox公式資料](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)

   GitHub ActionsのWindowsランナーを利用する場合も、実際のOSと対話デスクトップの利用可否を確認する。Windows Server上のブラウザ撮影をWindows 11の実アプリ試験と同等に扱わない。GUI自動化が必要なジョブは、対話セッションを管理できる専用VMで実行する。

   Linuxコンテナ、Wine、CSSのdeviceScaleFactor変更だけではWindows 11のDirectWriteやOSのDPI設定を再現できない。Windows拡大率100/125/150/200%はVMの実設定で確認し、ブラウザ側の倍率設定とは分けて記録する。仮想GPU等による実機との差が残る場合は、該当環境への適用範囲も報告する。

3. **提出する成果物を固定する**

   | 成果物 | 内容 |
   | --- | --- |
   | overview.png | 旧版・新版を同条件で並べた比較一覧 |
   | before.png / after.png | 切り抜き前の原寸スクリーンショット |
   | diff.png | 同じOS・描画条件における画素差分 |
   | details/ | 「元」、半角カナ、濁点、罫線、行間等の詳細画像 |
   | report.html | 画像、検査結果、意図した変更と意図しない差を確認できるレポート |
   | manifest.json | TTFハッシュ、コミット、OS、アプリ、表示設定、使用機能、テスト文字列 |

   成果物は `build/proofs/<run-id>/` にまとめ、CIではダウンロードできる成果物として保存する。エージェントは実際に確認した代表画像を会話に提示し、全レポートへリンクする。現物のスクリーンショットの代わりに生成画像や手描きの文字を使わない。拡大見本には原寸を併記する。

   初期基準は公開v1.0.0。スクリーンショットの基準画像はOS・ブラウザ・描画設定ごとに持つ。LinuxとWindowsを画素一致させる判定にはしない。差分が出た場合は、入力や環境の変化を調べてから判断し、テストを通すためだけに基準画像を更新しない。[Playwrightの視覚比較](https://playwright.dev/docs/test-snapshots)

   古い版に既知の不具合があるので、すべての画素差を失敗にも、すべての差を改善にも分類しない。維持する輪郭・幅の数値検査と、修正対象の描画・行間の画像検査を組み合わせる。検証できなかったOS・アプリは未検証として残す。

4. **導入順序**

   まず現行TTFを使うインストール不要の比較ページと撮影コマンドを実装し、現在の見た目を保存する。次に新しいRegularを同じページへ追加して差分を提出する。その後、Windows 11 VMへの転送・アプリ起動・撮影・結果回収を自動化し、#2/#6の検証へつなげる。VMが未準備でもブラウザproofの実装は進められるが、Windows確認済みとは報告しない。
