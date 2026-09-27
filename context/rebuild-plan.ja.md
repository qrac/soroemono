# SOROEMONO 再設計計画

調査日: 2026-09-22。対象: ローカルの `fb1378e`、GitHub Issues #1–#6、そのコメント、公開リリース `1.0.0`、同梱の元フォント。以下は再設計の全体計画。Regular試作とブラウザ比較の初回実装・実測結果は [試作時の開発記録](development-preview-2026-09-23.ja.md) に記録した。2026-09-23にBold試作とMac/Windowsブラウザ表示を追加確認した（[Macの検証記録](artifacts/verification-2026-09-23/mac/report.md)、[Windowsの検証記録](artifacts/verification-2026-09-23/win/report.md)）。Windows実アプリでの不具合解消は未確認。

**推奨は、JetBrains Monoを基準にした、Python + fontTools中心のビルドへの刷新。** JetBrains Monoの英数字の輪郭・幅・字形切り替え・描画命令を維持し、BIZ UDGothicから採用する文字だけを加工して追加する。フォントを単に合成するスクリプトから、出典と幅の仕様を検証してフォントを生成する仕組みに変える。

2026-09-22の追加方針: 現在のSOROEMONOの見た目を出発点にする。まず公開v1.0.0を比較基準として字形・配置を再現し、不具合修正とデザイン変更を分ける。ユーザーの日常環境でのフォント差し替えを前提にせず、ブラウザへの直接読み込みと仮想環境で検証し、スクリーンショットを提出する。寸法は [現行字形の基準](font-baseline.ja.md)、検証環境は [フォント検証計画](font-testing.ja.md) を参照する。プロジェクトの計画・調査・仕様は `context/` に置く。

2026-09-27の運用変更: Mac側は開発・修正、Windows内のCodexはWindows検証を担当し、独立cloneと同じ `v2` ブランチで受け渡す。報告は `context/artifacts/<run-id>/mac/` と `win/` に分け、共通文書はMac側で更新する。MacからのVM遠隔操作用Skillを廃止し、[Windows検証・Git受け渡し手順](windows-verification.ja.md)を現行手順とする。新運用の初回実行は未確認。

1. **現在の問題と、確認できた事実**

   | 対象 | 確認結果 | 設計への反映 |
   | --- | --- | --- |
   | v1の `build.py`（Git履歴） | 合成後、幅600の全グリフを1200に変更する。関数を保存処理なしで実行すると `A: 600 → 1200`、`元: 600 → 1200`、`ｱ: 500 → 500` になった | 出典を失った状態で、幅だけを条件に加工しない |
   | 公開v1.0.0 | `A=600`、`元=1200`、`ｱ=500`。現在のコードの処理結果とは一致しない | 配布物、入力、コード、ツールを対応づけて記録する |
   | 公開v1.0.0の幅 | Unicodeマッピングを数えると、1200が10,875件、600が1,339件、500が204件、0が24件 | 半角カナだけでなく、BIZ由来の追加欧文等も全件検査する |
   | 行間 | JetBrains Monoは `hhea` / Typo系が `1020 / -300 / 0`。SOROEMONOは `880 / -120 / 0`。Win系も `880 / 120` | UPM、字面の大きさ、行間を別の値として扱う |
   | ヒンティング | 公開TTFの `fpgm` / `prep` / `cvt ` はBIZ UDGothicと同一。`A`のグリフ命令はJetBrains Monoと同一。加工済みの「元」にも元のBIZの命令が残っている | 異なるフォントの描画命令と共有テーブルを混在させない。加工する日本語の旧命令を除去する |
   | 文字の収録 | 公開Regularの通常cmapには両元フォントのコードポイントがすべて存在する。BIZのcmap format 14も、8セレクタ・合計10,160エントリを維持している | 「既存版はIVS未対応」とは扱わない。現在ある対応を維持し、対応先・実描画も検査する |
   | ライセンス情報 | 公開ZIPはTTF 2個のみ。公開TTFのname ID 0はBIZ側の著作権表示のみ | 出典両方の表示とOFL本文を配布物に含める |

   [#2](https://github.com/qrac/soroemono/issues/2) の行間問題には数値上の根拠がある。[#6](https://github.com/qrac/soroemono/issues/6) の「元」については、2025年のコメントに `gasp` 削除で改善したとの報告がある。ただし、その操作では再生成も行われているので、`gasp` だけが根本原因とは断定しない。ヒンティング情報の不整合は今回のバイナリ調査から得た有力な原因候補であり、Windowsでの比較検証を残す。

   元フォントの同梱版はJetBrains Mono 2.304、BIZ UDGothic 1.051。調査時点の公式latest releaseもそれぞれ同じ版だった。まず改善すべきなのは合成工程で、入力の版を新しくするだけでは解決しない。[JetBrains Mono](https://github.com/JetBrains/JetBrainsMono/releases/tag/v2.304)、[BIZ UDGothic](https://github.com/googlefonts/morisawa-biz-ud-gothic/releases/tag/v1.051)

   公開TTFのSHA-256はRegularが `83994897f9a4ee58cab502861f47718b4638b1836e379e1479035b4a664ea8d3`、Boldが `320f342c6517885d5358251f231b4c0bf09049095caf35f46bcacf604c950f84`。ローカル `dist` と完全一致はしないが、上表の主要メトリクスと幅分布は一致した。

2. **製品として守る仕様を先に決める**

   「1:2」は輪郭の外接矩形ではなく、文字送り幅（advance width）の比率とする。JetBrains MonoのUPM 1000と通常文字送り600を基準に、1セル600、2セル1200とする。

   | 文字・機能 | 標準方針 |
   | --- | --- |
   | ASCII、通常の欧文、プログラミング記号 | JetBrains Monoの輪郭・幅・配置を保持 |
   | 漢字、かな、全角英数字、和文句読点、全角スペース | BIZ UDGothicを使い1200に統一 |
   | 半角カナと半角濁点・半濁点 | 600に統一。`ﾞ`・`ﾟ` はそれぞれ1セルの文字 |
   | 結合文字、異体字セレクタ | 単独の全角文字として処理しない。組み合わせ後の幅と位置を保証 |
   | 東アジア曖昧幅の記号 | 原則1セル。JetBrains Monoの既存記号を優先し、BIZから補う記号の例外も表にする |
   | リガチャ、`ss`、`cv`、`zero` | JetBrains Monoの機能を保持。標準のコード表示では置換前後の総セル幅を維持 |
   | IVS | BIZ UDGothicが持つ対応を維持。全Unicode・全IVSへの対応を新たに約束しない |
   | 絵文字、フォールバック | OSやアプリ側の表示を含むため、フォント単体の幅保証とは分ける |

   ただし、JetBrains Mono 2.304自身が `｛` U+FF5B、`｝` U+FF5D、`﹢` U+FE62、`⚡` U+26A1を600幅で収録している。この4文字は、UnicodeのWide/Fullwidth分類と元フォントの幅が衝突する。

   推奨する例外は、全角の `｛｝` をBIZの1200幅へ切り替え、`﹢` はJetBrains Monoの輪郭を拡大せず1200セル内へ配置すること。`⚡` はテキスト表示と絵文字表示を含めて比較し、標準のテキスト字形を2セルへ配置する案を検証する。位置や幅を変える例外は専用グリフへ複製し、そのグリフの旧ヒントを除去して、元グリフを参照する他の機能へ影響させない。これらは意図した例外として設定と変更履歴に記録する。欧文・ASCIIを保持する仕様と、全収録文字が無条件に元のままという仕様を混同しない。

   Prettierとの整合は、版を固定したPrettierで実際に整形したMarkdownをテストする。「あらゆる文字が常に揃う」という表現は避け、サポートする文字列・設定を示す。UnicodeのEast Asian Widthだけでは現代のターミナルの幅規則を完全に表現できないため、文字幅表と実アプリの両方を使う。[Unicode UAX #11](https://www.unicode.org/reports/tr11/)

3. **採用する技術と、採用理由**

   | 選択肢 | 評価 |
   | --- | --- |
   | 現行FontForgeスクリプトを局所修正 | 短期的な修正は可能。ただし描画命令、文字対応、再現性の検証を結局追加する必要がある |
   | UDEV Gothicをそのまま基盤にする | 試験項目や実装の参考になる。ただし1:2版はJetBrains Monoを縮小するため、本プロジェクトの優先順位とは異なる |
   | Python + fontToolsで入力TTFを直接加工・合成 | 採用。JetBrains Monoの不要な輪郭変換を避け、テーブル単位で検査・制御できる |
   | UFO等へ全面変換して再コンパイル | 元字形を直接編集する制作には有用だが、今回の目的には工程が多く、既存の描画命令や機能を失うリスクが増える |
   | フォントフォールバックのみ | 任意の複数ファミリーを扱えない環境や、行間・スタイル選択の問題が残るため、主配布方式にはしない |

   ビルドはPython、fontTools、uvのロックファイルを中心にする。検査はpytest、HarfBuzz、OpenType Sanitizer、FontBakery。NodeとPrettierはMarkdownの互換性検証用に限定する。FontForgeは標準の合成工程から外し、必要なら手動調査用に残す。

   `fontTools.merge` はOpenTypeレイアウトの合成に対応するが、同じUnicodeの異なるグリフがあると `locl` による切り替えを追加するため、無設定で一度呼ぶだけにはしない。入力のUPM統一と、重複コードポイントの採用方針を先に解決する。[fontTools merge](https://fonttools.readthedocs.io/en/latest/merge.html)

   UDEV GothicもFontForgeとfontToolsを組み合わせている。今回の目的はツールの新旧による優劣ではなく、JetBrains Monoへの変更を抑えて原因を追える工程にすること。[UDEV Gothic](https://github.com/yuru7/udev-gothic)

4. **生成工程**

   ```text
   入力バージョン・SHA-256の検証
       ↓
   元フォントのcmap・IVS・機能・描画情報を監査
       ↓
   コードポイントごとの出典・セル幅・例外を確定
       ↓
   BIZ由来の文字と依存グリフを抽出・加工
       ↓
   JetBrains Monoを先頭・基準として合成
       ↓
   行間・命名・スタイル・著作権情報を設定
       ↓
   幅・字形・シェーピング・バイナリ・描画の検証
       ↓
   TTF・OFL・説明・入力情報・ハッシュを梱包
   ```

   **入力と文字選択。** 公式配布の静的TTFを使用し、Regular/Boldに加えて必要なItalic/Bold Italicを固定した版から取得する。`sources.lock.json` に取得URL、リリースタグまたはコミット、アーカイブとTTFのSHA-256を記録する。通常ビルドでlatestを自動追跡しない。

   出典はコードポイントごとに決め、BIZ側の重複するcmapエントリを外す。グリフそのものの削除は、複数Unicodeからの参照、合成グリフ、GSUB、IVSを調査してから行う。必要な参照先まで閉じた集合を保持する。既存の「日」の欠損報告も回帰テストへ入れる。[初期開発メモ](https://github.com/qrac/soroemono/issues/1)

   **日本語のサイズ。** 現行の公開v1.0.0の字形・配置を基準にする。追加調査で、現在の全角字形はBIZのUPM 2048を1000へ正規化し、横方向のみ約1.08倍にした設計セル1080に左右60を加え、文字送り1200とした形に相当すると確認した。まずこの値とベースラインを維持する。1000+左右100、1100+左右50等の別デザインを初期作業の必須比較にしない。1080は各字形の外接幅ではなく、元の余白を含む設計セルの変換幅である。

   現行の全角変換は概念的には `x' ≈ x × 1080 / 2048 + 60`、`y' ≈ y × 1000 / 2048`。旧工程には段階的な丸めや輪郭再生成があるため、これを一度丸めるだけで全点が完全一致するとは限らない。公開版の実輪郭と比較し、点数・座標・表示の差を記録する。基準画像のために現行スクリプトで公開版を再生成しない。

   半角カナの現行字形は横幅500の設計セルである。まず輪郭の大きさを維持し、左右50を追加して文字送りを600へ直す案を採用する。横幅540への拡大は、必要になった場合の別のデザイン変更とする。結合文字や特殊な配置の文字にはこの余白追加を一律適用しない。元の句読点を外接矩形で一律中央寄せせず、かなと漢字の大きさの違いも維持する。

   結合文字、全角罫線、合成グリフ、GSUB専用グリフは通常文字の変換から分ける。罫線は接続部分に余白を入れない。合成グリフは参照元・参照先を二重に変換しない。変換は一度で適用して整数へ丸め、輪郭・side bearing・bboxを再計算する。結合文字は幅を0にするだけで済ませず、アンカーまたは配置情報まで含めて調整する。

   **描画命令。** 基本案はJetBrains Monoの `fpgm` / `prep` / `cvt ` とグリフ命令を保持し、加工するBIZ側のTrueTypeヒンティングを除去する。全体への再ヒンティングは、JetBrains Monoの小サイズ描画を変えてしまうので初期案にしない。調査に使ったfontTools 4.64.0のMergerも、先頭フォントの共有ヒントテーブルを採用し、2番目以降のグリフ命令を落とす実装である。採用版を固定し、その挙動をテストする。[fontTools実装](https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/merge/tables.py)

   `gasp` は全体の描画方針なので、JetBrains Mono由来を第一候補にし、Windowsで描画比較する。削除だけを恒久修正にはしない。日本語を無ヒンティングにした場合の低解像度での読みやすさが不十分なら、日本語の描画改善を独立した検証課題として扱う。相互に異なるヒントプログラムをそのまま足し合わせない。[gasp仕様](https://learn.microsoft.com/en-us/typography/opentype/spec/gasp)

   **OpenType機能。** JetBrains MonoのGSUB/GPOS/GDEFと非Unicodeグリフを保持する。BIZの異体字・必要な文字合成も保持する一方、日本語の比例幅・半角化等の機能は編集用の標準表示に影響させない。保持・除外する機能とスクリプトを一覧化する。IVSはcmap format 14の有無だけでなく、各対応先と1200幅の維持を検査する。横書きのエディタ用を対象とし、縦書き用テーブルや機能を標準成果物に残すかは整合性を含めて明示的に決める。初期版は縦書き対応を保証しない。

   **行間。** `head.unitsPerEm` を1000とすることと、ascender/descenderの合計を1000にすることは別問題。`hhea` と `OS/2.sTypo*` はJetBrains Monoの `1020 / -300 / 0` を出発点にし、`USE_TYPO_METRICS` を適切に設定する。全スタイルで同じ行送りを使う。

   `usWinAscent/Descent` はクリッピング領域として別途計算する。JetBrains Monoの元数値を無条件にコピーしない。現行Regularのbboxは上端1120・下端-400で、1020/300より外側に出るためである。合成後の収録字形・スタイル・代表的な結合表示を測定して確定する。Win系を行送りに使うアプリは余白が広くなる可能性があるため、単に全テーブルを同じ数値にするのではなく、対象アプリで決める。[OS/2仕様](https://learn.microsoft.com/en-us/typography/opentype/spec/os2)

   **メタデータ。** family/subfamily、typographic family、PostScript名、バージョン、Regular/Bold/Italicのスタイルリンクを整合させる。`post.isFixedPitch`、PANOSE、Unicode/codepage rangeも検査対象にする。CJKの2幅を含むため、フラグを立てれば等幅として正しく扱われるとは決めつけず、アプリ上の認識と実際の文字送りを確認する。古いDSIGなど、加工後に成立しない情報は持ち越さない。

5. **スタイルと既存Issuesの優先順位**

   | 順位 | 内容 | 完了条件 |
   | --- | --- | --- |
   | P0 | 600/1200の幅、コードと配布物の一致 | 通常文字、半角カナ、結合表示の検証を自動化。再ビルドのハッシュ一致 |
   | P0 | [#2 行間](https://github.com/qrac/soroemono/issues/2) | Windows Terminal、メモ帳、VS Codeターミナルで、詰まり・欠け・スタイル変更時の行高変化がない |
   | P0 | [#6 「元」](https://github.com/qrac/soroemono/issues/6) | Windowsの100%/200%で元の報告を再現し、新版で解消を確認。125%/150%も追加 |
   | P1 | [#5 イタリック](https://github.com/qrac/soroemono/issues/5) | 実物のJetBrains Mono Italic/Bold Italicを使い、4スタイルとして認識される |
   | P2 | [#3 全角スペース可視化](https://github.com/qrac/soroemono/issues/3) | 必要なら追加。標準は不可視、任意の未使用ss/cvで切り替え、幅は1200を維持 |
   | P2 | [#4 Nerd Fonts](https://github.com/qrac/soroemono/issues/4) | コア版安定後、別ファミリーとして追加し、字形・幅・IVS・メタデータの回帰を検証 |

   2.0の範囲はコアのRegular/Bold/Italic/Bold Italicを基本とする。まずRegularで工程を成立させ、Bold、その後Italic系へ進む。BIZ UDGothicには入力のItalicがないため、日本語は約9度の機械的な斜体を試作する。これは専用設計のイタリックではないことを明記し、直立日本語との比較見本で読みやすさ・はみ出しを判断する。ラテン文字は単純に傾けず、必ず元のItalicを使う。

   全角スペース可視化は過去の作者コメントでも採用が未定なので、バグ修正と同時に必須機能へ昇格させない。追加する場合も既存のJetBrains Monoのss/cvと衝突しない固定タグを予約し、元フォント更新時には衝突を検出して停止する。

   Nerd Fontsは名称、ライセンス、PUAの割り当て、セル幅、IVSを独立して管理する。最終TTF全体を別ツールで無検査に再生成する経路を作らない。アイコンだけを取り出して追加する方法も含め、JetBrains Mono側の保持検査を通す。Variable Font、多数の合成ウェイト、日本語文書専用版、WOFF2等のWeb配布は初期スコープに含めない。

6. **テストとリリース合格条件**

   テストの中心は実装内部の関数ではなく、生成されたTTFと文字列の表示結果にする。

   | 層 | 検証内容 |
   | --- | --- |
   | 入力 | 入力TTF・ツール・Unicodeデータの版とハッシュ一致。変化を黙って受け入れない |
   | 文字対応 | 通常cmap、別名コードポイント、補助平面、IVS、GSUB依存グリフの欠落と参照切れを検出 |
   | 幅 | 通常の1/2セル文字は600/1200。結合文字と特殊文字は明示した別規則。GSUB専用グリフや複数セルのリガチャに一律の制限を適用しない |
   | 元の欧文保持 | 例外を除くJetBrains Mono由来の輪郭、hmtx、グリフ命令、共有ヒントテーブルを比較。GIDやバイナリ全体の一致とは区別する |
   | 文字列 | HarfBuzzでNFC/NFD、濁点・半濁点、IVS、リガチャON/OFF、ss/cv/zero、混植の総送りと配置を検査 |
   | ファイル健全性 | OpenType Sanitizer、FontBakeryの適切なプロファイル。既知の例外には理由を記録し、Google Fonts専用の要求を無条件に採用しない |
   | エディタ互換性 | Prettierで整形したMarkdownテーブル、カーソル・選択範囲、罫線、折り返し、太字・斜体切り替えを確認 |
   | 視覚 | 旧版・新版・元JetBrains Monoを同条件で比較。フォントのフォールバックで偶然直って見えていないか確認 |
   | 再現性 | 正式ビルド環境の2回のクリーンビルドでTTF・ZIPのSHA-256が一致 |

   試験文字列には、ASCII全体、`元日国語`、ひらがな・カタカナ、`ｱｲｳｶﾞﾊﾟ`、`が / か + U+3099`、合成できない基底文字と結合濁点、全角括弧、円記号とバックスラッシュ、曖昧幅記号、罫線、Powerline、アクセント付き欧文、対応する補助平面漢字、既存のIVSを含める。合成済みの「が」だけのテストでは結合濁点の問題を検出できない。

   Windows 11のDirectWrite系アプリを最優先とし、VS Code本文・統合ターミナル、Windows Terminal、メモ帳、Chrome、Firefoxを検証する。macOSはVS Code、TerminalまたはiTerm2、JetBrains IDEを確認し、LinuxはFreeType/fontconfig系と実ターミナルを確認する。代表サイズ12/14/16/20pxとWindows拡大率100/125/150/200%を用いる。すべての組み合わせを毎PRの手作業にはせず、自動proofとリリース前の重点確認に分ける。

   HarfBuzzは整形、OTSはファイルの健全性を検証する道具であり、Windowsのラスタライズ不具合が直った証明にはならない。#2/#6は実アプリの記録をリリース条件にする。[HarfBuzz](https://harfbuzz.github.io/utilities.html)、[OTS](https://github.com/khaledhosny/ots)、[FontBakery](https://github.com/fonttools/fontbakery)

   ユーザーによるインストール・差し替え・スクリーンショット採取を通常の検証手順にしない。日常の比較はTTFを直接読むHTML proofとPlaywrightを使い、Windows固有の確認は隔離したWindows 11 VM内のCodexが担当する。エージェントは実際の変更前・変更後・差分PNGと検証環境情報をOS別の報告先へ保存し、Gitで受け渡す。Linuxコンテナの結果をWindows確認済みと扱わない。実行できていない環境は未検証と明記する。詳細は [フォント検証計画](font-testing.ja.md) に記載する。

7. **リポジトリと配布の構成案**

   ```text
   AGENTS.md
   pyproject.toml
   uv.lock
   sources.lock.json
   config/
     font.toml                 # UPM、幅、横倍率、行間、スタイル
     character-policy.toml     # 出典、幅、例外
   src/soroemono/
     sources.py
     audit.py
     selection.py
     transform.py
     merge.py
     metadata.py
     validate.py
     cli.py
   tests/
     fixtures/                 # 文字列、期待する対応、Markdown
     test_metrics.py
     test_source_preservation.py
     test_shaping.py
     test_metadata.py
   proofs/                     # 見本生成用のHTMLと文字列
   context/
     README.md                 # 資料の索引、実装済み
     progress.md               # 現在の状態、実装済み
     artifacts/                # 確定した検証証跡、Git管理
     rebuild-plan.ja.md
     font-baseline.ja.md
     font-testing.ja.md
     specification.ja.md
     testing.ja.md
   licenses/
   .github/workflows/
     ci.yml
     release.yml
   OFL.txt
   README.md
   CHANGELOG.md
   .cache/                     # 取得した元フォント、Git管理外
   build/                      # 中間成果物・スクリーンショット、Git管理外
   dist/                       # 配布物、Git管理外
   ```

   入口は `uv sync --locked --extra proof`、`uv run --locked soroemono build`、`uv run --locked soroemono check`、`uv run --locked soroemono proof`。Regular試作では実装済み。上記の詳細なモジュール分割や全スタイル向け設定は今後の構成案。

   入力のダウンロードとビルドを分離し、取得済みキャッシュがあればオフラインで生成できるようにする。まずLinuxの固定環境を正式なリリース生成元とし、OS間では構造・機能の一致を検査する。タイムスタンプ、グリフ順序、ファイル順序、ZIPの時刻等を固定し、同じ入力から同じ成果物を得る。

   PRでは生成TTF、検査結果、比較proofを成果物として保存する。タグからは同じ工程を通し、合格したものだけを配布する。ZIPにはTTF、インストール説明、OFL本文、両元フォントの著作権表示、ソース版情報、チェックサムを含める。[OFL公式本文](https://openfontlicense.org/open-font-license-official-text/)

   旧リリースとGit履歴は保持する。未使用のNoto Sans JP/LINE Seed JPや旧FontForge用 `build.py` / `build.ini` は2026-09-26にv2の作業ツリーから削除した。v2で使うJetBrains Mono/BIZ UDGothicの固定入力とOFLは維持する。リポジトリの全面刷新のために、履歴を書き換えたり新しいリポジトリへ移したりする必要はない。

8. **実装の順序と判断の区切り**

   | 段階 | 作るもの | 次へ進む条件 |
   | --- | --- | --- |
   | 1. 仕様・回帰例の固定 | 入力ロック、出典・文字幅ポリシー、旧版の監査レポート、インストール不要の基準proof、#2/#6の再現手順 | 現行の字形・配置を記録し、保持する挙動と直す挙動を区別できる |
   | 2. Regularの最小試作 | fontTools中心の生成、ヒンティング整理、600/1200の保証、cmap/IVS維持 | 欧文保持・文字幅・シェーピング検査を通過し、Windowsで主要不具合の改善を確認 |
   | 3. 現行の見た目を維持した修正確認 | 同じ字形・配置を基準に、行間・描画・半角幅の修正前後スクリーンショット | 意図しない字面変更がなく、不具合修正による差を説明できる |
   | 4. 4スタイルへ展開 | Bold/Italic/Bold Italic、名前とスタイルリンク | 太字・斜体への切り替えでセル幅と行高が変わらず、擬似欧文イタリックを使っていない |
   | 5. 2.0プレビュー配布の準備 | CI、再現可能なZIP、移行説明、各OSの検査記録 | #2/#6の受け入れ条件と互換性試験を満たす |
   | 6. 2.0正式版・拡張検討 | コアを正式化し、必要に応じて全角スペース可視化・NFを追加 | 拡張してもコアの検査が退行しない |

   プレビューには既存版と区別できる一時ファミリー名を使い、フォントキャッシュの混同を避ける。正式版はSOROEMONOの名称を継続し、旧版の削除・置き換え方法を説明する。最初の判断点は、Regularの小さな試作で「JetBrains Monoを保ったまま、半角カナ・日本語・Windowsの描画を正常化できるか」を証明すること。その確認後に全スタイルと配布基盤へ投資する。

   初回実装ではRegularの生成、数値・シェーピング検査、ブラウザproof、macOSでの旧版・新版・差分撮影まで実施した。2026-09-23にBoldの生成・検査とMac/WindowsでのRegular/Boldブラウザ比較を追加した。2026-09-26に4スタイルと正式名義のZIP生成を実装し、macOS Chromeで直接読み込みの比較を行った。CI設定は更新したがGitHub上での実行は未確認。Windows実アプリの受け入れと公開は未完了。詳細は [開発・検証手順](development.ja.md) と[正式ビルド検証記録](artifacts/v2-formal-build-2026-09-26/mac/report.md)を参照する。
