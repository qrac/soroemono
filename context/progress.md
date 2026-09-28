# SOROEMONOの進捗

更新: 2026-09-28

## 現在の状態

- 2026-09-27に検証運用を変更した。Mac側で開発・共通文書更新、Windows内のCodexでWindows検証を行い、独立したcloneから同じ `v2` ブランチで受け渡す。過去の検証記録・証跡を含めて `context/artifacts/<run-id>/mac/` と `win/` に分離した。画像とmanifestの内容は維持し、旧文書パスには移動先への案内を残した。MacからVMを操作するプロジェクトSkillは削除し、[Windows検証・Git受け渡し手順](windows-verification.ja.md)へ切り替えた。Windows側Codexの設置・ローカルビルド・新方式での初回受け渡しは未確認。
- 公開v1.0.0のRegular/Boldを比較基準として固定した。新しい生成工程は正式名義 `SOROEMONO` のRegular/Bold/Italic/Bold Italicを生成・数値検査し、同一入力から再現可能なv2.0.0 ZIPに梱包できる。[正式ビルドの記録](artifacts/v2-formal-build-2026-09-26/mac/report.md)を参照。
- メモ帳の日本語送り回帰に対し、4スタイルの `OS/2.xAvgCharWidth` を合成後の1115から半角セル600へ設定する修正候補を実装した。等幅フラグは `post.isFixedPitch=1` / `panose.bProportion=9` を維持し、3項目の生成TTF検査と回帰テストを追加した。UDEV Gothic v2.2.0の実装・配布TTFを照合した互換性修正であり、Windowsでの解消は未確認。ユーザー指定により今回のWindowsテストは別のWindows側ChatGPTで行う。[調査・Mac検証・引き継ぎ](artifacts/notepad-metrics-2026-09-28/mac/report.md)を参照。
- macOSとWindows 11 VMのChromeで、Regular/Boldのブラウザproofを撮影・確認した。[Macの検証結果](artifacts/verification-2026-09-23/mac/report.md)と[Windowsの検証結果](artifacts/verification-2026-09-23/win/report.md)をOS別の画像・環境情報とともに保存済み。
- v2から旧FontForge用の `build.py` / `build.ini` と、未使用のNoto Sans JP／LINE Seed JP入力を除外した。旧実装はGit履歴に残る。v2が使うJetBrains Mono／BIZ UDGothicの入力とOFLは保持する。[削除前後の生成・画像検証](artifacts/v2-cleanup-2026-09-26/mac/report.md)ではTTFとブラウザ画像が一致した。
- 2026-09-26〜27にmacOS Chromeで4スタイルの直接読み込み・幅と描画の比較を実施した。Windows 11 VMでも当時の正式版4スタイルのChrome描画と、GDI・メモ帳での4スタイル列挙を確認した。公開v1.0.0と正式v2.0.0を分けてVMに登録し、OS拡大率200%のWindows Terminal、VS Codeターミナル、メモ帳でIssue #2の行間改善を撮影した。一方、正式v2のメモ帳では日本語の文字送りが公開版の約1.9倍になる回帰を発見した。メタデータ2項目を両方0にした試験版では送りが戻ったが、他アプリへの影響は未検証で採用していない。#2の全体判定は保留。[Windows検証記録](artifacts/windows-v2-2026-09-27/win/report.md)と[証跡](artifacts/windows-v2-2026-09-27/win/README.md)を参照。試験後、VMはスナップショットから元の `paused` 状態へ戻した。
- Issue #6はWindowsヘッドレスChromeで公開版の「元」の欠けと新版の改善を確認したが、OS拡大率200%の対話表示では公開版の欠けを再現できなかった。OS拡大率100%は未検証で、報告条件全体での解消判定は未完了。Issue #5のVS Code等での自動斜体切替、配布公開も未完了。

## 次の検証

- Windows側で独立clone・固定依存関係・復元可能な検証環境を確認し、対象コミットを記録して初回のビルド・検証結果を `context/artifacts/<run-id>/win/report.md` へ保存する。Mac側が受領し、この進捗へ反映する。
- Issue #2は平均文字幅600の修正候補をWindows側へ渡し、メモ帳の日本語送りとWindows Terminal等の等幅認識・行間改善を確認する。具体的な比較対象と手順は[今回の引き継ぎ](artifacts/notepad-metrics-2026-09-28/mac/report.md#windows側への引き継ぎ)を参照。Issue #6に着手するときは公開版の欠けを報告条件どおり再現し、正式版と同条件で比較する。#5に着手するときはVS Code等での自動Italic/Bold Italic切替を撮影する。検証方法と環境記録は[Windows検証・Git受け渡し手順](windows-verification.ja.md)に従う。
- 通常の合格条件は[再設計計画の第6節](rebuild-plan.ja.md)に従い、自動検査とMac・Windowsのブラウザproofで判定する。OTS/FontBakeryの独立検査、CI上の実行、他OSの追加確認は未実施で、一律の公開条件にはしない。未解決Issueと未検証範囲を明示したうえで公開を判断する。正式配布公開は未実施。

実行コマンドは[開発・検証手順](development.ja.md)、設計上の基準は[再設計計画](rebuild-plan.ja.md)と[現行字形の基準](font-baseline.ja.md)を参照する。
