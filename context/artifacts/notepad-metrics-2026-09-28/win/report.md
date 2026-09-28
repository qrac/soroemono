# メモ帳の文字送り修正候補: Windows 側の再検証準備結果

記録日: 2026-09-28。対象コミット: `43a1a92bb8b44962ebba8dfa9f26788144d2b05a`（`v2`）。開始時の作業ツリーはクリーン。これは[Mac 側の修正・検証記録](../mac/report.md)を受けた Windows 側の実行結果であり、**メモ帳での解消判定ではない**。

## 確認できたこと

- 修正コミット `824915f` は `OS/2.xAvgCharWidth=600`、`panose.bProportion=9` を生成時に設定し、3項目の検査と回帰テストを追加している。`824915f..43a1a92` で `src/`、`tests/`、`resource/`、`pyproject.toml`、`uv.lock`、`sources.lock.json` に差分はない。
- Git に記録されたソース・ロックの SHA-256 は[Mac 側の数値比較](../mac/metrics-comparison.json)の値と一致した。Windows の作業ファイルは改行コードが CRLF なので、`git show HEAD:<path>` の生バイトをハッシュした。

| Git 内のファイル | SHA-256 |
| --- | --- |
| `src/soroemono/builder.py` | `a214ca05f3f34a058a395c1ddd9ca325364eb345bcbc1fe5a27b774621c389d8` |
| `src/soroemono/validation.py` | `a41891a5418b5c208af4d5bf88a1eff3703a70a0f416219f41784678f18dd6d0` |
| `tests/test_build.py` | `82e1fc961077baf90eca6026e3c5d3381f9e9d55c2ad3c65e1cf1d6dc1279de3` |
| `uv.lock` | `90767254d510f20230978563ca00c1158225b6c3c336398e48f615c4c3bd318c` |
| `sources.lock.json` | `8e397ccf2251e80ca72e55eff74402bdbf208624ce673a60a819ab6d5f6d448d` |

## 実行できなかった検証

検証端末は通常使用の Windows（`Windows NT 10.0.26200.0`、ARM64）で、ユーザーに復元可能な検証用 VM ではないことを確認した。`WindowsSandbox.exe` も見つからなかった。プロジェクト方針に従い、この端末へ試験フォントを登録・削除していない。

| 操作 | 結果 |
| --- | --- |
| `uv sync --locked --extra proof` | `uv` コマンドが存在せず、開始できなかった。指定の Python 3.14.6 / `.venv` もない。 |
| 同梱 Python 3.12.14 で `python -m unittest discover -s tests -v` | `ModuleNotFoundError: No module named 'fontTools'`。テスト本体は実行されていない。 |
| `pip download --dest build/wheels uv==0.9.20` | PyPI への接続が `WinError 10013` で失敗した。権限を上げた再試行は実行ポリシーの `sandbox_approval: false` により拒否された。 |
| 新しい v2 TTF の生成・SHA-256 照合、Windows ブラウザ proof | 未実施。生成に必要な固定依存関係がない。 |
| メモ帳、Windows Terminal、VS Code での修正前後の実アプリ比較 | 未実施。復元可能な隔離環境と新しい TTF がない。 |

今回生成した TTF・ZIP・スクリーンショットはない。[Mac 側で生成した修正後 TTF のハッシュと画像](../mac/report.md#macでの検証結果)を Windows で再確認したものとは扱わない。公開 v1.0.0 と修正前 v2 の[過去の Windows 証跡](../../windows-v2-2026-09-27/win/report.md)も、今回の修正後 v2 の表示証拠にはならない。

## 判定と再開条件

Issue #2 の行間改善は過去の Windows 証跡で確認済みだが、**平均文字幅600の修正でメモ帳の日本語送りが正常に戻るかは未判定**。解消を宣言しない。

再開には、固定版 Python / uv / 依存関係を導入できる Windows 環境と、スナップショットから復元できる検証専用 Windows VM が必要。対象コミットから TTF を生成して SHA-256 を[Mac 側の値](../mac/report.md)と照合し、修正前 v2 と修正後 v2 を別々の復元サイクルで登録する。その後、同条件のメモ帳、Windows Terminal、VS Code の前・後・差分画像と環境情報を新しい `win/` 記録に保存する。
