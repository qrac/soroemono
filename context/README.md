# SOROEMONO context

作業の状態、設計上の判断、検証記録をまとめる。作業に関係する資料だけを参照する。

| 確認したいこと | 参照先 |
| --- | --- |
| 現在の状態・残作業 | [進捗](progress.md) |
| 再設計の方針と未実装の構成案 | [再設計計画](rebuild-plan.ja.md) |
| 公開v1.0.0の字形・幅 | [現行字形の基準](font-baseline.ja.md) |
| 検証方針と受け入れ範囲 | [フォント検証計画](font-testing.ja.md) |
| v2.0.0のビルド・検査・撮影の実行方法 | [開発・検証手順](development.ja.md) |
| Regular/Bold試作時の実行方法・初回結果 | [試作時の開発記録](development-preview-2026-09-23.ja.md) |
| Mac・Windowsブラウザでの確認結果 | [2026-09-23の検証記録](verification-2.0.0a1-2026-09-23.ja.md)と[保存した証跡](artifacts/verification-2026-09-23/README.md) |
| v2の不要ファイル整理と生成結果の確認 | [2026-09-26の検証記録](verification-v2-cleanup-2026-09-26.ja.md) |
| v2.0.0の正式ビルド実装と検証 | [正式ビルド検証記録](verification-v2-formal-build-2026-09-26.ja.md) |
| v2.0.0のWindows 11実アプリとIssues #2/#5/#6 | [2026-09-27の検証記録](verification-v2-windows-2026-09-27.ja.md)と[保存した証跡](artifacts/windows-v2-2026-09-27/README.md) |
| Windows VMの操作と次の検証手順 | [Parallels DesktopによるWindows検証](windows-parallels.ja.md) |

## 更新方針

- `progress.md` は現在の状態と次の作業を示す。古い作業日誌を積み重ねず、状態が変わったら更新する。
- 計画、実装済みの事実、未検証事項を区別する。詳しい実測値と実行条件は個別の検証記録に残す。
- 日常の生成物はGit管理外の `build/` に保存する。記録として残す画像・環境情報だけを `artifacts/` に複製し、対応する記録からリンクする。
