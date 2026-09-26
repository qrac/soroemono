# v2.0.0正式ビルドの実装・検証

記録日: 2026-09-26。これはローカルの正式名義ビルドと配布ZIP生成の記録であり、GitHub Releasesへの公開またはWindows実アプリでの受け入れ完了を示すものではない。

## 実装した内容

- JetBrains Mono 2.304のItalic/Bold Italic静的TTFを公式配布アーカイブから追加した。アーカイブSHA-256は `6f6376c6ed2960ea8a963cd7387ec9d76e3f629125bc33d1fdcd7eb7012f7bbf`。既存Regular/Boldも同アーカイブのTTFとハッシュが一致した。全入力は `sources.lock.json` で固定し、通常ビルドでは取得しない。
- 4スタイルを `SOROEMONO` ファミリーとして生成する。Italic系の英数字・OpenType機能・ヒントはJetBrains MonoのItalic入力を保持し、BIZ由来の字形を9度傾ける。字形変換後のBIZヒントは削除する。両元フォントのOFLと著作権情報を含める。
- `soroemono release` は4スタイルを各2回生成してTTFのバイト一致を確認し、数値・シェーピング検査後に決まったZIP時刻・順序で `dist/SOROEMONO_v2.0.0.zip` を作る。ZIPにはTTF、両OFL、入力情報、ビルド・検査結果、ファイル別SHA-256、導入説明を含める。

## 数値と再現性

| スタイル | TTF SHA-256 | Unicode文字 | IVS | 文字送り0 / 600 / 1200 |
| --- | --- | ---: | ---: | --- |
| Regular | `56f46b6042efc0911317895aa7dbcd281af3f4ba129925316d8422f96e6b1ea1` | 12,442 | 10,160 | 47 / 1,518 / 10,877 |
| Bold | `bce5467676cdddfc10a054b56f2ccc8ad75be053489ca4e0e9c51965cd9c1a13` | 12,442 | 10,160 | 47 / 1,518 / 10,877 |
| Italic | `846a900fef548abc964941475e800f6a44ed1fba5486a21724d6a8f2becb2ab6` | 12,442 | 10,160 | 47 / 1,518 / 10,877 |
| Bold Italic | `847568ee0f4daf922a3d3cea9a71f60ce8b4d7a9886bcc56e01102f62787ad43` | 12,442 | 10,160 | 47 / 1,518 / 10,877 |

全スタイルで `hhea` / Typo行メトリクスは `1020/-300/0`、Winクリッピング範囲は `1120/400`。名前、ウェイト、Bold/Italicフラグ、Italic角度を検査した。HarfBuzz検査はJetBrains Monoのラテンシェーピング保持、半角カナ、結合濁点、IVS等を対象にした。単位テスト6件が合格した。ZIPは別出力先で2回生成し、バイト一致を確認した。ZIPのSHA-256は `603ed8c7197a20ef3827191253bcdf65b8f3f3fa3d821abfc62af401ee0c918c`。`unzip -t` も合格し、ZIP内TTFと個別生成TTFのハッシュが一致した。

## 実画像と環境

macOS 26.6.2 / arm64、Chrome 154.0.8037.57のヘッドレス表示。1200×1100 CSS px、deviceScaleFactor 1、ブラウザ倍率1、ブラウザ既定のラスタライズ。OSの物理DPIは未取得。proofには14/16/20pxと、`line-height: normal` の16px見本を含めた。Chromeの実使用フォント照会で各TTFのカスタムフォント利用を確認し、フォールバックを検出しなかった。100pxでの実測は旧版 `A=60、日=120、ｱ=50px`、新版は4スタイルとも `A=60、日=120、ｱ=60px`。通常行送りの4行見本は旧版64px、新版84px。

| スタイル | 比較一覧 | 変更前 | 変更後 | 差分 | 環境・TTFハッシュ |
| --- | --- | --- | --- | --- | --- |
| Regular | [画像](artifacts/v2-formal-build-2026-09-26/regular/overview.png) | [画像](artifacts/v2-formal-build-2026-09-26/regular/before.png) | [画像](artifacts/v2-formal-build-2026-09-26/regular/after.png) | [画像](artifacts/v2-formal-build-2026-09-26/regular/diff.png) | [manifest](artifacts/v2-formal-build-2026-09-26/regular/manifest.json) |
| Bold | [画像](artifacts/v2-formal-build-2026-09-26/bold/overview.png) | [画像](artifacts/v2-formal-build-2026-09-26/bold/before.png) | [画像](artifacts/v2-formal-build-2026-09-26/bold/after.png) | [画像](artifacts/v2-formal-build-2026-09-26/bold/diff.png) | [manifest](artifacts/v2-formal-build-2026-09-26/bold/manifest.json) |
| Italic | [画像](artifacts/v2-formal-build-2026-09-26/italic/overview.png) | [画像](artifacts/v2-formal-build-2026-09-26/italic/before.png) | [画像](artifacts/v2-formal-build-2026-09-26/italic/after.png) | [画像](artifacts/v2-formal-build-2026-09-26/italic/diff.png) | [manifest](artifacts/v2-formal-build-2026-09-26/italic/manifest.json) |
| Bold Italic | [画像](artifacts/v2-formal-build-2026-09-26/bold-italic/overview.png) | [画像](artifacts/v2-formal-build-2026-09-26/bold-italic/before.png) | [画像](artifacts/v2-formal-build-2026-09-26/bold-italic/after.png) | [画像](artifacts/v2-formal-build-2026-09-26/bold-italic/diff.png) | [manifest](artifacts/v2-formal-build-2026-09-26/bold-italic/manifest.json) |

一覧画像と差分画像を目視した。Regular/Boldは旧版の日本語字面を概ね維持し、半角カナの位置と幅、行間に意図した差が出た。Italic系では英数字と日本語の傾きが確認でき、見本の欠字や明白なクリッピングは見られなかった。旧版にはItalic系がないため、変更前はそれぞれ公開Regular/Boldの直立字形であり、斜体同士の比較ではない。差分画像の画素差は行メトリクス変更によるベースライン移動、半角幅修正、Italic字形を含むため、画素一致を合格条件にしていない。

## 残る受け入れ

- Windows 11 VMは確認時点で一時停止中で、復元用スナップショットがなかった。フォント登録を伴うVS Code、Windows Terminal、メモ帳の4スタイル認識、Issue #2/#6の描画確認は未実施。既存のWindowsブラウザ試作検証を正式版の実アプリ合格と扱わない。
- OTS/FontBakeryの独立検査、GitHub Actionsの実行、他OSの最終確認、GitHub Releasesへの公開は未実施。ZIPを生成できることと、公開の受け入れ完了は別に扱う。
