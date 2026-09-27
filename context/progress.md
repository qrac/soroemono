# SOROEMONOの進捗

更新: 2026-09-27

## 現在の状態

- 公開v1.0.0のRegular/Boldを比較基準として固定した。新しい生成工程は正式名義 `SOROEMONO` のRegular/Bold/Italic/Bold Italicを生成・数値検査し、同一入力から再現可能なv2.0.0 ZIPに梱包できる。[正式ビルドの記録](verification-v2-formal-build-2026-09-26.ja.md)を参照。
- macOSとWindows 11 VMのChromeで、Regular/Boldのブラウザproofを撮影・確認した。[検証結果](verification-2.0.0a1-2026-09-23.ja.md)と[画像・環境情報](artifacts/verification-2026-09-23/README.md)を保存済み。
- v2から旧FontForge用の `build.py` / `build.ini` と、未使用のNoto Sans JP／LINE Seed JP入力を除外した。旧実装はGit履歴に残る。v2が使うJetBrains Mono／BIZ UDGothicの入力とOFLは保持する。[削除前後の生成・画像検証](verification-v2-cleanup-2026-09-26.ja.md)ではTTFとブラウザ画像が一致した。
- macOS Chromeで4スタイルの直接読み込み・幅と描画の比較を実施した。Windows 11 VMでも正式版4スタイルのChrome描画と、GDI・メモ帳での4スタイル列挙を確認した。公開v1.0.0と正式v2.0.0を分けてVMに登録し、OS拡大率200%のWindows Terminal、VS Codeターミナル、メモ帳でIssue #2の行間改善を撮影した。一方、正式v2のメモ帳では日本語の文字送りが公開版の約1.9倍になる回帰を発見した。メタデータ2項目を両方変えた試験版では送りが戻るが、他アプリへの影響は未検証で、正式版は変更していない。#2の全体判定は保留。[Windows検証記録](verification-v2-windows-2026-09-27.ja.md)と[証跡](artifacts/windows-v2-2026-09-27/README.md)を参照。試験後、VMはスナップショットから元の `paused` 状態へ戻した。
- Issue #6はWindowsヘッドレスChromeで公開版の「元」の欠けと新版の改善を確認したが、OS拡大率200%の対話表示では公開版の欠けを再現できなかった。OS拡大率100%は未検証で、報告条件全体での解消判定は未完了。Issue #5のVS Code等での自動斜体切替、配布公開も未完了。

## 次の検証

- Windows 11 VMでIssue #2のメモ帳における日本語の送り拡大を修正し、Windows Terminal等での等幅認識と行間改善が維持されるか確かめる。Issue #6の公開版の欠けを報告条件どおり再現し、正式版と同条件で比較する。特にOS拡大率100%を確認する。#5のVS Code等での自動Italic/Bold Italic切替も撮影する。検証方法と環境記録は[Windows検証手順](windows-parallels.ja.md)に従う。
- OTS/FontBakeryの独立検査、CI上の実行、他OSでのリリース前確認は未実施。これらの受け入れ後に公開を判断する。

実行コマンドは[開発・検証手順](development.ja.md)、設計上の基準は[再設計計画](rebuild-plan.ja.md)と[現行字形の基準](font-baseline.ja.md)を参照する。
