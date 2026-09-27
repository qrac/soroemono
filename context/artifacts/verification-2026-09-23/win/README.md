# 2026-09-23 Windows検証の証跡

[検証記録](report.md)に対応する保存画像と環境情報。画像は再生成していない。

| 環境・目的 | 比較画像 | 元・新版・差分 | 環境情報 |
| --- | --- | --- | --- |
| Windows 11 Chrome / Regular | [対話画面](windows-20260923/regular-overview.png) | [before](windows-20260923/regular-before-full.png)・[after](windows-20260923/regular-after-full.png)・[diff](windows-20260923/regular-diff-full.png) | [manifest](windows-20260923/manifest.json) |
| Windows 11 Chrome / Bold | [対話画面](windows-20260923/bold-overview.png) | [before](windows-20260923/bold-before-full.png)・[after](windows-20260923/bold-after-full.png)・[diff](windows-20260923/bold-diff-full.png) | [manifest](windows-20260923/manifest.json) |

Windowsの対話画面とヘッドレス全ページ画像は撮影条件が異なるため、直接の画素比較には使わない。撮影前の `initial.png` は保存版に含めず、元のWindows manifestにはそのハッシュも記録されている。
