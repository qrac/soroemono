# Parallels DesktopによるWindows検証

調査日: 2026-09-23。これはWindows 11 VMでSOROEMONOを検証するための操作設計と初回の接続調査。後続のRegular/Boldブラウザ表示結果は[検証記録](verification-2.0.0a1-2026-09-23.ja.md)に記載。既存Issueの実アプリ受け入れ結果ではない。実行入口は [プロジェクトSkill](../.agents/skills/soroemono-windows-check/SKILL.md)。全体の判定基準は [フォント検証計画](font-testing.ja.md) に従う。

## 接続調査の結果

| 項目 | 確認した事実 |
| --- | --- |
| ホストCLI | `prlctl` / `prlsrvctl` があり、`prlctl` は27.0.2 (58673) |
| VM | `Windows 11` を検出。Windowsの `ver` は10.0.26200.9457 |
| ゲスト操作 | `prlctl exec` による `ver` と共有フォルダの `dir` が成功。Parallels Toolsは27.0.2-58673 |
| 画面取得 | `prlctl capture` でデスクトップのPNGを取得し、画像を確認した |
| 共有フォルダ | ホストの `~/github` が `github` として共有済み。ゲストの `\\Mac\github\soroemono` からリポジトリを読めた。参照会話にある `\\Mac\soroemono` は存在しなかった |
| VM状態 | 調査中に `paused` へ移行。設定は `Pause idle: on`。停止中のゲストコマンドが待ち続けた原因候補だが、因果は未確定 |
| 後続のWindowsブラウザproof | Regular/Boldの表示、`FontFace.load()`、幅確認を実施。結果と画像は[検証記録](verification-2.0.0a1-2026-09-23.ja.md)に保存。CDPによる実使用フォント照会は未実施 |
| 引き続き未確認 | VS Code CLI、実アプリ描画、Issue #2/#6の改善 |

この接続では通常のサンドボックスから `prlctl` がmacOSのプロセス情報を読めず失敗し、適切な権限での再実行が必要だった。Skillは手順を提供するもので、実行権限やParallels Toolsを追加するものではない。CLIによるゲストコマンド実行と画面取得は [Parallels公式CLI資料](https://download.parallels.com/desktop/v20/docs/en_US/Parallels%20Desktop%20Command-Line%20Reference.pdf) に記載されている。実際のオプションはインストール済みの27.0.2のヘルプを優先する。

## 実行と判定

1. **Macで比較入力を用意する。** [開発・検証手順](development.ja.md) の新工程でRegularの `build`、`check`、公開v1.0.0の `fetch-baseline`、`proof` を行う。Git履歴に残る旧 `build.py` は英数字も拡大し、出力先を削除するため使わない。公開版とPreview版のハッシュを `build/proofs/regular/manifest.json` で確認する。`report.html` はTTFとライセンスを内包するため、ゲストでPythonやFontForgeを実行する必要はない。
2. **VMと入力経路を再発見する。** `prlctl list --all`、`prlctl list -i <VM>` とゲスト内の読み取り専用コマンドで、起動状態、Tools、共有名、HTMLの読取可否を確かめる。上表のVM名と共有パスは調査時の値であり、固定値にはしない。ゲストコマンドが待ち続けたら中断してVM状態を確認し、一時停止中なら再開して一度だけ再試行する。VM設定を変更した場合は初期状態へ戻す。
3. **Windowsブラウザでproofを表示する。** 共有上の `build/proofs/regular/report.html` をWindowsのブラウザで開く。`?mode=overview`、`?mode=before`、`?mode=after` を同じ解像度・拡大率・ブラウザ倍率で表示する。ページの成功表示、実測値、文字欠け、幅、行間、「元」、半角カナ、結合文字を確認する。フォント読込エラーやフォールバックの疑いがあれば合格にしない。可能ならブラウザの使用フォント情報も取得する。
4. **画面と環境を保存する。** VMが動作中で各モードの画面が更新されたことを確認してから、`prlctl capture <VM> --file <PNG>` の元画像を `build/proofs/windows-<run-id>/` に保存する。一時停止中の古い画面をproofに使わない。各モードの全画面画像を残したうえで、同じ範囲に切り出した比較画像と差分を作る。TTFのSHA-256、Gitコミットと未コミット変更、Windowsビルド、ブラウザ版、画面解像度、DPI・Windows拡大率、ブラウザ倍率、描画設定、Parallels/Tools版を対応づける。取得できない値は推測せず未取得と記す。検証記録として確定した画像と環境情報は `context/artifacts/` に複製する。
5. **必要なら実アプリを検証する。** ブラウザproofだけではVS CodeやWindows Terminalのフォント選択、行送り、Windows固有の描画不具合は合格にできない。破棄可能なVMまたは安全に戻せる専用スナップショットを用意した後、VM内だけでRegular試験フォントを登録し、使い捨てプロファイルでアプリを起動する。既存のアプリ設定やホストOSのフォントを変更しない。スナップショット復元時に他の作業を消さないことを確認する。

現在の試作はRegular/Bold。公開版BoldとPreview版Boldのブラウザ比較は実施済み。Italic/Bold Italicと4スタイル認識は今後の実装に属する。Windowsブラウザproofの完了と、Issue #2/#6のWindows 11実アプリ受け入れ完了は別に記録する。各段階を「合格・不合格・未検証」で報告し、後者が未検証なら不具合解消を宣言しない。

## GitHub Actionsの役割

既存の [Regular previewワークフロー](../.github/workflows/preview.yml) はUbuntu 24.04でテスト、数値検査、ビルド、ブラウザproofをpush/PRごとに実行する設計。ParallelsのWindows 11 VMはWindows固有の描画と実アプリの確認に使う。したがって、このWindows受け入れのためにGitHub ActionsのWindowsジョブを必須とはしないが、既存のUbuntu CIは維持する。GitHub上での同ワークフロー実行結果はまだ未確認。

GitHub-hosted runnerのOSはラベルで異なる。一般的なx64 `windows-latest` はWindows Server系で、Windows 11 VMの実アプリ表示と同一条件とは扱わない。Windows 11 Armランナーは利用可能だが、対話デスクトップを要する確認の代替と決めつけない。[GitHubランナー一覧](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)
