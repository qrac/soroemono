# SOROEMONO context

作業の状態、設計上の判断、検証記録をまとめる。作業に関係する資料だけを参照する。

| 確認したいこと | 参照先 |
| --- | --- |
| 現在の状態・残作業 | [進捗](progress.md) |
| 再設計の方針と未実装の構成案 | [再設計計画](rebuild-plan.ja.md) |
| 公開v1.0.0の字形・幅 | [現行字形の基準](font-baseline.ja.md) |
| 検証方針と受け入れ範囲 | [フォント検証計画](font-testing.ja.md) |
| v2.0.0のビルド・検査・撮影の実行方法 | [開発・検証手順](development.ja.md) |
| Mac・Windowsの担当範囲、Git受け渡しとWindows検証 | [Windows検証・Git受け渡し手順](windows-verification.ja.md) |
| Regular/Bold試作時の実行方法・初回結果 | [試作時の開発記録](development-preview-2026-09-23.ja.md) |
| 2026-09-23のRegular/Boldブラウザ確認 | [Macの記録](artifacts/verification-2026-09-23/mac/report.md)と[証跡](artifacts/verification-2026-09-23/mac/README.md)、[Windowsの記録](artifacts/verification-2026-09-23/win/report.md)と[証跡](artifacts/verification-2026-09-23/win/README.md) |
| v2の不要ファイル整理と生成結果の確認 | [2026-09-26の検証記録](artifacts/v2-cleanup-2026-09-26/mac/report.md) |
| v2.0.0の正式ビルド実装と検証 | [正式ビルド検証記録](artifacts/v2-formal-build-2026-09-26/mac/report.md) |
| v2.0.0のWindows 11実アプリとIssues #2/#5/#6 | [2026-09-27の検証記録](artifacts/windows-v2-2026-09-27/win/report.md)と[保存した証跡](artifacts/windows-v2-2026-09-27/win/README.md) |

## 更新方針

- `progress.md` は現在の状態と次の作業を示す。古い作業日誌を積み重ねず、状態が変わったら更新する。
- 索引・進捗・共通手順はMac側が更新する。Windows側は `artifacts/<run-id>/win/report.md` に結果をまとめ、Mac側が受領後に進捗へ反映する。
- 計画、実装済みの事実、未検証事項を区別する。詳しい実測値と実行条件は個別の検証記録に残す。
- 日常の生成物は各cloneのGit管理外の `build/` に保存する。確定画像・環境情報・報告は `artifacts/<run-id>/mac/` と `artifacts/<run-id>/win/` に分ける。`<run-id>` は検証内容・日付・対象コミット等で区別し、再検証で以前の証跡を上書きしない。TTF・ZIP・TTF内包HTMLは保存版に含めない。
- 方式変更前の検証記録・証跡もOS別に整理した。画像・manifestの内容は維持し、旧文書パスには移動先への案内を残した。記録内のParallels CLI操作は過去の実行条件であり、現行手順は [Windows検証・Git受け渡し手順](windows-verification.ja.md) を参照する。
