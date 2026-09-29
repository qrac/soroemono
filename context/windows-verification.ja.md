# Windows検証・Git受け渡し手順

更新: 2026-09-28。[参照会話「Codex 2箇所運用比較」](chatgpt-conversation://6ab91659-5be0-83ee-954d-a8aad044191b)を受け、Macで開発、Windows内のCodexで検証し、Gitで結果を受け渡す運用にする。Parallels DesktopはWindows 11の実行環境として残す。Macからの `prlctl` や共有フォルダによる遠隔操作を通常手順から外し、専用Skillは削除した。コミット・pushはユーザーから明示的に指示された場合だけ行う。

これは運用方針と実行手順の変更であり、Windows側Codexの設置、Windowsローカルでのビルド、新方式での受け渡し成功を示す記録ではない。従来方式で確認した結果は [2026-09-27のWindows検証記録](artifacts/windows-v2-2026-09-27/win/report.md)、残作業は [進捗](progress.md)、判定基準は [フォント検証計画](font-testing.ja.md) を参照する。

## 担当と保存先

Mac・Windowsにそれぞれ独立したローカルcloneを置き、共通の `v2` ブランチを使う。WindowsではWindows側ディスクの作業ツリーを使う。同じ共有作業ツリー、`.venv`、生成物を両OSから編集しない。

| 担当 | Git管理する変更 | 実行内容 |
| --- | --- | --- |
| Mac | `src/`、`tests/`、依存関係・設定、`AGENTS.md`、`context/` の共通文書、各runの `mac/` | 開発・修正、macOS検証、Windows報告の確認と進捗反映 |
| Windows | 原則 `context/artifacts/<run-id>/win/` のみ | ローカルビルド・数値検査、Windowsブラウザproof、対象Issueに着手したときの実アプリ検証、撮影と報告 |

Windowsで見つかった不具合やビルド失敗は `win/report.md` に再現条件と修正候補を残す。ソース、ロック、共通の `README.md` / `progress.md`、他OSの画像は変更しない。修正案はMac側で作り、Git経由でWindowsへ渡して再検証する。両Codexはそれぞれの環境で作業し、Mac側からWindows側のGUI操作やチャットの起動を指揮することを前提にしない。

新規の確定記録は次の配置にする。`<run-id>` は内容・日付・対象コミット等で区別し、再実行時は別IDを使う。

```text
context/artifacts/<run-id>/
├── mac/
│   ├── report.md
│   ├── manifest.json
│   └── regular/…
└── win/
    ├── report.md
    ├── manifest.json
    ├── regular/…
    └── apps/…
```

`mac/` と `win/` は該当する検証を実施したときに作る。共有するrun直下にはOS別報告への索引だけを置く。作業中の生成物は既存のGit管理外の `build/` / `dist/` に保存し、確定画像・環境情報・報告だけを複製する。TTF、ZIP、TTFを内包するHTMLはコミットしない。2026-09-27以前の記録もOS別に整理した。移動前の混合記録はGit履歴に残し、旧文書パスには移動先への案内を残す。既存画像・manifestの内容は変更せず、再検証では過去の証跡を上書きしない。

## Gitでの受け渡し（ユーザーから指示された場合）

1. Mac側は修正・必要な検査を完了し、Windowsで検証する対象と確認項目を明確にする。Gitでの受け渡しを指示された場合に `v2` へコミット・pushする。
2. Windows側は `git status --short` で未完了作業がないことを確認し、`v2` で `git pull --ff-only` を行う。未保存の変更があれば先に保全し、強制resetで消さない。`git rev-parse HEAD` の値を**検証対象コミット**として、検証開始時のGit状態とともに保存する。
3. 対象コミットからビルド・撮影し、画像を確認して `win/report.md` と環境情報をまとめる。結果のコミットを指示された場合は、確認済みのファイルだけを `git add context/artifacts/<run-id>/win/` で選び、差分を確認してコミットする。`<run-id>` は実際のIDに置き換える。
4. 結果のpushを指示された場合は、未保存の変更がない状態で `git pull --rebase`、`git push` の順に同期する。pushが他方の先行更新で拒否されたら同じ順序で再同期する。競合時は相手の内容を自動的に捨てず、競合箇所を確認する。担当外の変更が必要ならMac側で調整し、force pushはしない。
5. Mac側はWindowsの報告をpullして画像・ハッシュ・対象コミットを確認し、共通の索引と進捗へ反映する。以後の修正も同じ往復で検証する。

結果コミットやrebase後のHEADは、検証対象コミットとは別物として扱う。検証中に `v2` のコードが進んでも報告内の対象コミットは変えず、新しいコードの受け入れには再検証を行う。結果のpushだけでGitHub Releasesへの配布公開を行わない。

## Windows側での実行

Windows内のローカルcloneをカレントディレクトリにし、WindowsのPython・ブラウザで実行する。WSL/Linuxでの描画をWindows描画の結果として扱わない。入力と依存関係は [開発・検証手順](development.ja.md) の固定値を使う。以下はRegularの例であり、Windowsでの実行成功は初回に確認して報告する。

```powershell
uv sync --locked --extra proof
uv run --locked python -m unittest discover -s tests -v
uv run --locked soroemono fetch-baseline
uv run --locked playwright install chromium
uv run --locked soroemono build --style Regular
uv run --locked soroemono check --style Regular
uv run --locked soroemono proof --style Regular
uv run --locked soroemono capture --proof build/proofs/regular
```

基準版とブラウザの取得は初回準備として生成から分ける。固定依存関係やブラウザの導入に失敗した場合は、コマンド・エラー・OS/CPU構成を報告し、未実行の検証を明記する。Regular以外は `--style` とproofパスを合わせる（`Bold` → `bold`、`Italic` → `italic`、`"Bold Italic"` → `bold-italic`）。4スタイルのZIPを検査する場合は `uv run --locked soroemono release` を使う。Mac側と同じ配布候補を試すときは、対象コミットに加えて生成TTFのSHA-256を照合し、不一致なら同一入力として扱わず原因を調べる。

ブラウザproofは公開v1.0.0の実物と新版TTFを直接読み込む。フォント登録は不要。`capture` の読込・幅・実使用フォントの検査結果と画像を確認する。現行 `capture` はヘッドレス・device scale factor 1の撮影であり、WindowsのOS拡大率100%や対話アプリの検証を代替しない。

対象Issueの実アプリ検証が必要なときに、Windows Terminal、VS Code、メモ帳等の該当アプリをWindows側で起動・撮影する。復元可能な専用VM状態を確保したうえで、VM内だけに試験フォントを登録し、使い捨てのアプリ設定を使う。公開版と新版は同名なので、版ごとに隔離状態を戻し、登録先のTTFハッシュを照合してアプリを再起動する。MacのOSや日常用のフォント・アプリ設定は変更しない。自動操作やフォールバック確認ができない項目は未検証・確認限界として記録する。

復元前に証跡と必要な未コミット作業をVM外へ保全し、退避を確認してから検証用状態へ戻す。Gitでの退避を指示された場合に限り、確定した報告・画像・環境情報をpushする。Git管理外のデータや他の作業が失われる状態では復元しない。VMの起動や復元がWindows側だけではできない場合は、その制約を報告し、Mac側の遠隔操作を自動的に再開しない。

## 報告とIssue別の確認項目

`win/report.md` に実行コマンド、合格・不合格・未検証、意図した差と回帰、原因候補、次の確認を記載し、画像と `manifest.json` へ相対リンクする。既存の撮影manifestは保持し、run全体の環境情報で不足分を補う。

- 検証対象コミット、開始時の未コミット変更、Python・uv・依存関係、入力と比較する各TTFのSHA-256、ZIPを使った場合はそのSHA-256。
- Windowsの版・ビルド・CPU構成、アプリ版、文字サイズ・行高・テスト文字列、画面解像度、DPI・OS拡大率・ブラウザ倍率、ClearType等の描画設定、Parallels/Tools・仮想GPU・接続条件。未取得の値は推測しない。
- 同条件の変更前・変更後・差分の原寸画像と詳細画像。撮影条件、切り出し範囲、画像ハッシュ、フォールバック確認の方法と限界を対応づける。

各Issueに着手・解消判定するときの確認項目は、#2のメモ帳の日本語送り回帰と関連アプリの等幅認識・行間、#6の公開版での欠け再現と新版の同条件比較（報告条件のOS拡大率100%/200%、必要に応じて125%/150%）、#5の自動Italic/Bold Italic切替。これらは通常のブラウザ基本合格には含めない。4スタイル列挙やヘッドレスChromeだけで個別Issueの実アプリ検証を完了としない。

GitHub Actionsの設定は2026-09-29に削除した。ローカル環境での検査と証跡保存を続ける。Linux上の検査はWindows 11の対話アプリ表示の代替にしない。OTS/FontBakeryと他OSの追加確認は必要な場合に実施する。正式配布公開は別途未完了として管理する。
