# 2.0.0a1 Regular/Bold のWindows表示確認

実施日: 2026-09-23。公開v1.0.0の現物を変更前、2.0.0a1の `SOROEMONO Preview` を変更後として比較した。OSへのフォント登録は行っていない。撮影時の出力はGit管理外の `build/proofs/` に置き、画像と環境情報の保存版は[検証証跡](README.md)にGit管理した。

## 入力と検査

| スタイル | 公開v1.0.0 SHA-256 | 2.0.0a1 SHA-256 |
| --- | --- | --- |
| Regular | `83994897f9a4ee58cab502861f47718b4638b1836e379e1479035b4a664ea8d3` | `dbb57d5d8a634ecbb5527832ad52d8df06c5ea7b87be54dddedd9e052c549674` |
| Bold | `320f342c6517885d5358251f231b4c0bf09049095caf35f46bcacf604c950f84` | `f9f7ec6b42daca9969802b73e76ddfc15afd9cbcc8b5f8a464e62990c347237b` |

両入力は `sources.lock.json` で固定した。公開版は同じv1.0.0 ZIPから取り出し、アーカイブと両TTFのハッシュを検証した。Regular/Boldの数値検査はそれぞれ合格。通常cmapは12,442文字、IVSは10,160組、文字送りは0が47、600が1,518、1200が10,877文字。ラテン入力の輪郭・文字送り・ヒント、変形した日本語の古いヒント除去、シェーピングを検査した。Boldのウェイト700、名前、スタイルフラグ、Regularとの行メトリクス一致も確認した。ユニットテストは5件合格した。

## Windows 11 Chrome

Parallels Desktop 27.0.2 (58673)、Tools 27.0.2-58673、Windows 11ビルド10.0.26200.9457、Chrome 153.0.8010.53。VMの当初状態は `paused`、`Pause idle: on`。作業中に再開したが設定変更はしなかった。ログイン中ユーザーで `prlctl exec --current-user` を使って共有フォルダのHTMLを開いた。`--current-user` なしでは別セッションでブラウザが起動し、VM画面には表示されなかった。

対話画面は3200×1724物理px。ゲストの画面境界は1600×862、ユーザーの `LogPixels=192`、`Win8DpiScaling=1` で、表示倍率200%に対応する。`FontSmoothing=2`、`FontSmoothingType=2`。Chromeは一時プロファイル、既定の描画設定。対話画面で両スタイルのoverview/before/afterを開き、緑の「読み込み・文字幅確認 OK」と字形を撮影・確認した。ブラウザ倍率の実測値は未取得。一時プロファイルの既定値を使用した。

ページ下部までの比較には同じWindowsのChromeヘッドレスで1600×2200 pxの全画面PNGを取得した。before/afterは同一手法・条件で撮影し、差分画像を作った。対話画面の200%表示とヘッドレスの画素は直接比較していない。両スタイルの全ページで「元」、半角カナ、コード、結合文字、罫線、通常行送りを実画像で確認した。文字欠けや明らかな崩れはこの見本では見つからなかった。Windowsでは `FontFace.load()` とページ内の幅検査の成功表示を確認したが、Macで行ったCDPの実使用フォント照会は未実施。収録外文字のフォールバックを完全には除外していない。

Windowsの生画面、全ページ画像、差分、環境情報は[保存したWindowsの証跡](README.md)を参照。撮影時の出力先は `build/proofs/windows-20260923/`。`regular-before-full.png` / `regular-after-full.png` / `regular-diff-full.png` とBoldの対応ファイルはWindows内の同じChromeで作成した。差分には行送りによる配置の変化が含まれ、個々の字形変更のみを表さない。

| 段階 | 判定 | 範囲 |
| --- | --- | --- |
| Parallels CLI接続 | 合格 | VM状態、共有フォルダ、ゲストコマンド、撮影 |
| Windowsブラウザproof | 合格 | Regular/Boldの読込成功表示、代表字形・幅・行送りの実画面 |
| Windows実アプリ | 未検証 | VS Code、Windows Terminal、メモ帳、スタイル切替、#2/#6の受け入れ |

Windows固有のIssue #2/#6が実アプリで解消したとは判断しない。VM内のフォント登録や既存アプリ設定の変更は行っていない。Italic/Bold Italicと4スタイル認識も対象外。
