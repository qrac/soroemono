# SOROEMONOの進捗

更新: 2026-09-23

## 現在の状態

- 公開v1.0.0のRegular/Boldを比較基準として固定した。新しい生成工程では `SOROEMONO Preview` のRegular/Boldを生成・数値検査できる。
- macOSとWindows 11 VMのChromeで、Regular/Boldのブラウザproofを撮影・確認した。[検証結果](verification-2.0.0a1-2026-09-23.ja.md)と[画像・環境情報](artifacts/verification-2026-09-23/README.md)を保存済み。
- Windows実アプリでの表示、Issue #2/#6の解消、Italic/Bold Italic、4スタイル認識、正式配布は未完了。ブラウザ表示の確認を実アプリでの合格と扱わない。

## 次の検証

- Windows 11 VMのVS Code、Windows Terminal、メモ帳でRegular/Boldの幅・行間・字形・スタイル切替を確認する。検証方法と環境記録は[Windows検証手順](windows-parallels.ja.md)に従う。
- Italic系の生成と検証を行い、4スタイルを揃えてから正式配布の条件を確認する。

実行コマンドは[開発・検証手順](development.ja.md)、設計上の基準は[再設計計画](rebuild-plan.ja.md)と[現行字形の基準](font-baseline.ja.md)を参照する。
