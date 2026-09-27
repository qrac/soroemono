# 2.0.0a1 Regular/Bold のMac表示確認

実施日: 2026-09-23。公開v1.0.0の現物を変更前、2.0.0a1の `SOROEMONO Preview` を変更後として比較した。OSへのフォント登録は行っていない。撮影時の出力はGit管理外の `build/proofs/` に置き、画像と環境情報の保存版は[検証証跡](README.md)にGit管理した。

## 入力と検査

| スタイル | 公開v1.0.0 SHA-256 | 2.0.0a1 SHA-256 |
| --- | --- | --- |
| Regular | `83994897f9a4ee58cab502861f47718b4638b1836e379e1479035b4a664ea8d3` | `dbb57d5d8a634ecbb5527832ad52d8df06c5ea7b87be54dddedd9e052c549674` |
| Bold | `320f342c6517885d5358251f231b4c0bf09049095caf35f46bcacf604c950f84` | `f9f7ec6b42daca9969802b73e76ddfc15afd9cbcc8b5f8a464e62990c347237b` |

両入力は `sources.lock.json` で固定した。公開版は同じv1.0.0 ZIPから取り出し、アーカイブと両TTFのハッシュを検証した。Regular/Boldの数値検査はそれぞれ合格。通常cmapは12,442文字、IVSは10,160組、文字送りは0が47、600が1,518、1200が10,877文字。ラテン入力の輪郭・文字送り・ヒント、変形した日本語の古いヒント除去、シェーピングを検査した。Boldのウェイト700、名前、スタイルフラグ、Regularとの行メトリクス一致も確認した。ユニットテストは5件合格した。

## macOS Chrome

macOS 26.6.2 arm64、Chrome 154.0.8037.57、ヘッドレス、1200×1100 CSS px、deviceScaleFactor 1、ブラウザ倍率1、サイズ14/16/20 CSS px、`font-synthesis:none`、`calt` ON。Regular/Boldとも `FontFace.load()` 成功。Chromiumの `CSS.getPlatformFontsForNode` で表示見本にシステムフォントへのフォールバックがないことを確認した。100px実測幅は両スタイルで旧版 `A=60, 日=120, ｱ=50`、新版 `A=60, 日=120, ｱ=60` px。16px・4行の通常行送りの高さは旧版64pxから新版84pxになった。

比較画像・詳細・環境記録: [保存したMac Regular/Boldの証跡](README.md)。撮影時の `screenshots.html` / `manifest.json` は `build/proofs/regular-20260923/` と `build/proofs/bold-20260923/` にある。実画像で「元」、かな、英数字、半角カナ、罫線、結合文字、通常行送りを見た。半角カナのセル幅と行送り以外にも、丸め・描画位置に小さな画素差がある。日本語の意図しない大きな字形変化はこの見本では見つからなかった。IPAの全組合せは未確認。

## 判定

MacブラウザproofはRegular/Boldの読込、実使用フォント、代表字形・幅・行送りについて合格。Mac実アプリの確認はこの検証の対象外。
