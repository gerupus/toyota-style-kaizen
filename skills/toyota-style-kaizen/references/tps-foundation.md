# 根拠と応用の境界

このスキルはGitHub公開を想定した非公式の独自実装。「Toyota」「トヨタ」名称と方法論を説明上参照するが、提携、公式監修、認証、本人による指導は一切主張しない。企業ロゴと固有のブランド意匠を使わない。

## 公式資料が裏付ける骨格

- トヨタ自動車: トヨタ生産方式の目的は、働く人を働きやすく楽にすることを前提に、良い品質の品を安くタイムリーに届けるため、ムダを減らしリードタイムを短縮すること。2本柱は自働化とジャスト・イン・タイム。
  https://global.toyota/jp/company/vision-and-philosophy/production-system/
- トヨタ自動車: 自働化では異常を検知して止め、不良品を流さず「品質を工程でつくり込む」。単純な無人自動化と区別される。
  https://global.toyota/jp/company/vision-and-philosophy/production-system/
- Toyota Europe: The Toyota Way 2020 は現地現物、継続改善、人への敬意を掲げている。
  https://www.toyota-europe.com/about-us/toyota-vision-and-philosophy/the-toyota-way.html
- Toyota Europe: 問題の根本原因を探る手法として「ask why five times」を紹介。
  https://www.toyota-europe.com/about-us/toyota-quality

## 参考知見 / 5回固定にしない理由

- Lean Enterprise Institute の解説: 5 Whys は回数をちょうど5回にする儀式ではなく、実際の因果と操作可能な根本原因に到達するための反復。場合により2回やそれ以上でもよい。現場観察なしの推測だけで進めない。
  https://www.lean.org/the-lean-post/articles/how-many-whys-should-i-ask/
- 1つの原因鎖だけに見える問題でも多原因の可能性がある。原理を超えて「必ず単一の真因」を強要しない。
  https://www.lean.org/the-lean-post/articles/five-whys/

## このスキル独自の適用

- 「現場」 = 現物のコード、原稿、CMS画面、ログ、作業手順、ユーザーフロー等。AIは物理現場を訪問できるわけではない。
- 「アンドン」 = ユーザーへの異常報告と当該出力・変更の停止判断。実際のトヨタのアンドン設備とは無関係。
- 「JIT」 = 必要な時だけ必要な分析とツール呼び出しを使うという比喩。正しい在庫管理プロセスを再現しているわけではない。
- 「標準作業」 = 再現可能なテンプレート、lint、CI、チェックリストのようなガードレール。思考や創造性の固定化ではない。
- 「ポカヨケ」 = 起こりやすいミスを入口で検出する入力バリデーション、フォーム設計、テストのような比喩。

> 厳密なTPS教育を求められた場合は、このデジタル応用例と実務のTPSを明確に分け、一次資料を再確認する。
