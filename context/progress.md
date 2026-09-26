# SOROEMONOの進捗

更新: 2026-09-26

## 現在の状態

- 公開v1.0.0のRegular/Boldを比較基準として固定した。新しい生成工程は正式名義 `SOROEMONO` のRegular/Bold/Italic/Bold Italicを生成・数値検査し、同一入力から再現可能なv2.0.0 ZIPに梱包できる。[正式ビルドの記録](verification-v2-formal-build-2026-09-26.ja.md)を参照。
- macOSとWindows 11 VMのChromeで、Regular/Boldのブラウザproofを撮影・確認した。[検証結果](verification-2.0.0a1-2026-09-23.ja.md)と[画像・環境情報](artifacts/verification-2026-09-23/README.md)を保存済み。
- v2から旧FontForge用の `build.py` / `build.ini` と、未使用のNoto Sans JP／LINE Seed JP入力を除外した。旧実装はGit履歴に残る。v2が使うJetBrains Mono／BIZ UDGothicの入力とOFLは保持する。[削除前後の生成・画像検証](verification-v2-cleanup-2026-09-26.ja.md)ではTTFとブラウザ画像が一致した。
- macOS Chromeで4スタイルの直接読み込み・幅と描画の比較を実施した。Windows 11実アプリでの表示、Issue #2/#6の解消、4スタイル選択、配布公開は未完了。Windows VMには復元用スナップショットがないため、実アプリへのフォント登録は実施していない。ブラウザ表示の確認を実アプリでの合格と扱わない。

## 次の検証

- Windows 11 VMのVS Code、Windows Terminal、メモ帳でRegular/Boldの幅・行間・字形・スタイル切替を確認する。検証方法と環境記録は[Windows検証手順](windows-parallels.ja.md)に従う。
- 復元可能なWindows 11 VMで4スタイル選択とIssue #2/#6を実アプリで確認する。OTS/FontBakeryの独立検査、CI上の実行、他OSでのリリース前確認も未実施。これらの受け入れ後に公開を判断する。

実行コマンドは[開発・検証手順](development.ja.md)、設計上の基準は[再設計計画](rebuild-plan.ja.md)と[現行字形の基準](font-baseline.ja.md)を参照する。
