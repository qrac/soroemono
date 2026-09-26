---
name: soroemono-windows-check
description: Parallels Desktop の Windows 11 VM で SOROEMONO のブラウザproofや実アプリ表示を確認し、比較画像と環境記録を残すときに使う。
---

# SOROEMONO の Windows 確認

macOS上のこのリポジトリから、Parallels DesktopのCLIでWindows 11 VMを操作する。最初に [Windows検証の手順と接続調査](../../../context/windows-parallels.ja.md) と [フォント検証計画](../../../context/font-testing.ja.md) を読む。汎用のParallels Skillは任意であり、このSkillは `prlctl` が使えることを前提とする。Skillの追加だけでCLI権限は増えない。

1. `prlctl list --all` と選択したVMの `prlctl list -i` で対象、状態、Parallels Tools、共有フォルダ、`Pause idle` を確認する。VM名・共有パスを固定しない。コマンド構文はインストール済みの `prlctl <command> --help` で確かめる。サンドボックスでCLIが拒否されたら、そのコマンドの適切な権限で再実行する。初期状態と変更したVM設定は記録し、作業後に戻す。ゲストコマンドが待ち続けたら中断し、VM状態を確認して、停止中なら再開して一度だけ再試行する。
2. 現行の [開発・検証手順](../../../context/development.ja.md) に従い、Mac側で対象スタイルの `uv run --locked soroemono build`、`check`、`fetch-baseline`、`proof` を必要に応じて実行する。Regular以外は各コマンドに `--style` を付ける。公開v1.0.0を比較基準にし、旧 `build.py` は実行しない。`report.html` と両TTFのSHA-256を確認する。
3. Windowsゲストから検証済みの共有パスにある `build/proofs/<style>/report.html` を開く。HTML内包TTFのブラウザproofなのでOSへのフォント登録は不要。`?mode=overview`、`before`、`after` を同じWindows表示設定で確認し、ページの読み込み・幅検査の成功表示と文字を目視する。Italic系の変更前は公開v1.0.0の直立スタイルである。ブラウザを開けたことだけでフォント読み込み成功とは判定しない。`prlctl exec --current-user` を使わないと別セッションでブラウザが開き、VM画面に出ない場合がある。
4. VMが動作中でページが各モードに更新されたことを確かめ、`prlctl capture` で元画面を `build/proofs/windows-<run-id>/` に保存し、同一領域の比較・差分画像を作る。WindowsのOSビルド、ブラウザ版、解像度、拡大率、TTFハッシュ、VM設定、撮影条件を併記する。フォールバックを確認できない撮影はその限界を記録する。Mac/Linuxで作った画像や一時停止中の古い画面をWindows proofの証拠に流用しない。
5. VS Code、Windows Terminal、メモ帳での受け入れ確認が必要なら、先に破棄可能なVMまたは復元可能な隔離状態を確認する。そのVM内でのみ4スタイルの試験フォントを登録し、使い捨てのアプリ設定で表示する。隔離状態を確保できなければ実アプリ段階を未検証として残す。

結果は「CLI接続」「Windowsブラウザproof」「Windows実アプリ」を別々に合格・不合格・未検証で報告する。画像を実際に確認し、意図しない差を調査する。Issue #2/#6の解消はWindows 11の実アプリ比較を終えるまで断定しない。
