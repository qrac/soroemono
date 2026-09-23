# 2026-09-23の検証証跡

[検証記録](../../verification-2.0.0a1-2026-09-23.ja.md)に対応する、撮影済み画像と環境情報の保存版。元の出力はGit管理外の `build/proofs/` にある。保存したファイルは撮影時の出力とSHA-256が一致する。画像を作り直したり基準を更新したりしていない。

| 環境・目的 | 比較画像 | 元・新版・差分 | 環境情報 |
| --- | --- | --- | --- |
| macOS Chrome / Regular | [overview](regular-20260923/overview.png) | [before](regular-20260923/before.png)・[after](regular-20260923/after.png)・[diff](regular-20260923/diff.png) | [manifest](regular-20260923/manifest.json) |
| macOS Chrome / Bold | [overview](bold-20260923/overview.png) | [before](bold-20260923/before.png)・[after](bold-20260923/after.png)・[diff](bold-20260923/diff.png) | [manifest](bold-20260923/manifest.json) |
| Windows 11 Chrome / Regular | [対話画面](windows-20260923/regular-overview.png) | [before](windows-20260923/regular-before-full.png)・[after](windows-20260923/regular-after-full.png)・[diff](windows-20260923/regular-diff-full.png) | [manifest](windows-20260923/manifest.json) |
| Windows 11 Chrome / Bold | [対話画面](windows-20260923/bold-overview.png) | [before](windows-20260923/bold-before-full.png)・[after](windows-20260923/bold-after-full.png)・[diff](windows-20260923/bold-diff-full.png) | [manifest](windows-20260923/manifest.json) |
| Python 3.14.6の再生成確認 | [overview](python-3.14-verify/overview.png) | [before](python-3.14-verify/before.png)・[after](python-3.14-verify/after.png)・[diff](python-3.14-verify/diff.png)・[Python版間の差分](python-3.14-verify/python-version-diff.png) | [manifest](python-3.14-verify/manifest.json) |

Mac・Pythonの各ディレクトリには元の詳細画像も保存した。Windowsの対話画面と全ページ画像は撮影条件が異なるため、直接の画素比較には使わない。撮影前のデスクトップ `initial.png`、TTFを内包する `report.html`、生成TTF、撮影補助スクリプトはこの保存版に含めない。元のWindows manifestには `initial.png` のハッシュも記録されている。比較ページは[開発・検証手順](../../development.ja.md)に従って `build/` に生成する。
