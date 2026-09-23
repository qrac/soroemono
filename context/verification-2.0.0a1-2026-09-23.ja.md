# 2.0.0a1 Regular/Bold のMac・Windows表示確認

実施日: 2026-09-23。公開v1.0.0の現物を変更前、2.0.0a1の `SOROEMONO Preview` を変更後として比較した。OSへのフォント登録は行っていない。生成画像はGit管理外の `build/proofs/` に保存した。

## 入力と検査

| スタイル | 公開v1.0.0 SHA-256 | 2.0.0a1 SHA-256 |
| --- | --- | --- |
| Regular | `83994897f9a4ee58cab502861f47718b4638b1836e379e1479035b4a664ea8d3` | `dbb57d5d8a634ecbb5527832ad52d8df06c5ea7b87be54dddedd9e052c549674` |
| Bold | `320f342c6517885d5358251f231b4c0bf09049095caf35f46bcacf604c950f84` | `f9f7ec6b42daca9969802b73e76ddfc15afd9cbcc8b5f8a464e62990c347237b` |

両入力は `sources.lock.json` で固定した。公開版は同じv1.0.0 ZIPから取り出し、アーカイブと両TTFのハッシュを検証した。Regular/Boldの数値検査はそれぞれ合格。通常cmapは12,442文字、IVSは10,160組、文字送りは0が47、600が1,518、1200が10,877文字。ラテン入力の輪郭・文字送り・ヒント、変形した日本語の古いヒント除去、シェーピングを検査した。Boldのウェイト700、名前、スタイルフラグ、Regularとの行メトリクス一致も確認した。ユニットテストは5件合格した。

## macOS Chrome

macOS 26.6.2 arm64、Chrome 154.0.8037.57、ヘッドレス、1200×1100 CSS px、deviceScaleFactor 1、ブラウザ倍率1、サイズ14/16/20 CSS px、`font-synthesis:none`、`calt` ON。Regular/Boldとも `FontFace.load()` 成功。Chromiumの `CSS.getPlatformFontsForNode` で表示見本にシステムフォントへのフォールバックがないことを確認した。100px実測幅は両スタイルで旧版 `A=60, 日=120, ｱ=50`、新版 `A=60, 日=120, ｱ=60` px。16px・4行の通常行送りの高さは旧版64pxから新版84pxになった。

比較画像・詳細・環境記録: `build/proofs/regular-20260923/` と `build/proofs/bold-20260923/` の `screenshots.html` / `manifest.json`。実画像で「元」、かな、英数字、半角カナ、罫線、結合文字、通常行送りを見た。半角カナのセル幅と行送り以外にも、丸め・描画位置に小さな画素差がある。日本語の意図しない大きな字形変化はこの見本では見つからなかった。IPAの全組合せは未確認。

## Windows 11 Chrome

Parallels Desktop 27.0.2 (58673)、Tools 27.0.2-58673、Windows 11ビルド10.0.26200.9457、Chrome 153.0.8010.53。VMの当初状態は `paused`、`Pause idle: on`。作業中に再開したが設定変更はしなかった。ログイン中ユーザーで `prlctl exec --current-user` を使って共有フォルダのHTMLを開いた。`--current-user` なしでは別セッションでブラウザが起動し、VM画面には表示されなかった。

対話画面は3200×1724物理px。ゲストの画面境界は1600×862、ユーザーの `LogPixels=192`、`Win8DpiScaling=1` で、表示倍率200%に対応する。`FontSmoothing=2`、`FontSmoothingType=2`。Chromeは一時プロファイル、既定の描画設定。対話画面で両スタイルのoverview/before/afterを開き、緑の「読み込み・文字幅確認 OK」と字形を撮影・確認した。ブラウザ倍率の実測値は未取得。一時プロファイルの既定値を使用した。

ページ下部までの比較には同じWindowsのChromeヘッドレスで1600×2200 pxの全画面PNGを取得した。before/afterは同一手法・条件で撮影し、差分画像を作った。対話画面の200%表示とヘッドレスの画素は直接比較していない。両スタイルの全ページで「元」、半角カナ、コード、結合文字、罫線、通常行送りを実画像で確認した。文字欠けや明らかな崩れはこの見本では見つからなかった。Windowsでは `FontFace.load()` とページ内の幅検査の成功表示を確認したが、Macで行ったCDPの実使用フォント照会は未実施。収録外文字のフォールバックを完全には除外していない。

Windowsの生画面、全ページ画像、差分、環境情報は `build/proofs/windows-20260923/` に保存した。`regular-before-full.png` / `regular-after-full.png` / `regular-diff-full.png` とBoldの対応ファイルはWindows内の同じChromeで作成した。差分には行送りによる配置の変化が含まれ、個々の字形変更のみを表さない。

| 段階 | 判定 | 範囲 |
| --- | --- | --- |
| Parallels CLI接続 | 合格 | VM状態、共有フォルダ、ゲストコマンド、撮影 |
| Macブラウザproof | 合格 | Regular/Boldの読込、実使用フォント、代表字形・幅・行送り |
| Windowsブラウザproof | 合格 | Regular/Boldの読込成功表示、代表字形・幅・行送りの実画面 |
| Windows実アプリ | 未検証 | VS Code、Windows Terminal、メモ帳、スタイル切替、#2/#6の受け入れ |

Windows固有のIssue #2/#6が実アプリで解消したとは判断しない。VM内のフォント登録や既存アプリ設定の変更は行っていない。Italic/Bold Italicと4スタイル認識も対象外。
