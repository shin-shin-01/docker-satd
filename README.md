# 概要
東さんが検出してくださった "Dockerfile中のコメント（分類作業済みのもの）" に対して、<br>
追加時期やリビジョン数などを調査する<br>

今後の研究としてSATDの分析を行なっていく予定であるが 「SATDを含むDockerfileは、どの程度開発作業が行われているのか」を調査する．<br>
それにより、DockerfileのSATDを調査する必要性があるのか？また何かしらの特徴が存在するのかを明確にする

## Requirements
Run this command

`pip install -r requirements.txt`

## How to Use


### 1-git_clone_git_log_tocsv.py
目的：ログを取得し、コミットID/日時などCSVに保存する（対象コメントを含むものは詳細も）<br>
対象データ：最強データの分類済みコメント (未分類は含めない)<br>
結果：`./1-get_log`にCSVファイルを保存

1. コマンド引数から `debt/non-debt` を与えて実行する
2. 最強データを元に対象データを取得
3. リポジトリを`clone`して`git log -p`を実行する
4. 対象リビジョン（最強データ上のリビジョン）以降で
`"commitid":"date":"file":"diff":"rename"` を取得<br>
→ 対象コメントが含まれている場合に"diff"にログを保存．ファイル名の変更がある場合に"rename"に保存


### 2-get_targetfile.py
目的：対象コメントの変更点（debtの追加）があったファイルがどのファイルか？判断する．<br>
対象データ：`./1-get_log`内の全てのCSVファイル<br>
結果：`target_files`のカラムを増やし、`./2-get_targetfile`にCSVファイルを保存

1. `diff`について、対象コメントが追加(+)されているファイルを探す
2. `target_files`カラムに目的のファイルを記載し、関係のないファイルは`file`に保存したままにしておく

※ 対象コメントの起源まで遡るわけではない...
> 例）
> - 対象コメント：#todo: update version 2019 cuz hidden error
> - 判断できるもの：2018 -> 2019　など、上記コメントが + #todo: update version 2019 cuz hidden error として表現される場合
> - 判断できないもの：2017 -> 2018 など、上記コメント自体が発生する前のコミット

しかし上記が複数行で成り立っており、
> #todo:<br>
#update version 2019 cuz hidden error

のような構造なら、#todoが追加された時点まで遡ることは可能


### 3-rename-files.py
目的：過去のファイル名を最新版のファイル名に変更する<br>
対象データ：`./2-get_targetfile`内の全てのCSVファイル<br>
結果：`./3-renamed_files`にCSVファイルを保存

1. `rename`（ファイル名の変更）について過去全てを遡り、変更前(配列)→変更後 としてまとめる処理
→ 処理が重いため、`Docker/docker`を含むファイルのみ変更する
2. 実際にファイル名を変更する．


### 4-onehot_encoding.py
目的：コミットに対して、目的ファイルの変更を含むかどうかワンホットエンコーディングを行う<br>
対象データ：`./3-renamed_files`内の全てのCSVファイル<br>
結果：`./4-onehot_encoding`にCSVファイルを保存

1. `target_files`から目的のファイル名を取得
2. それぞれのコミットの変更ファイルに、1で取得したファイルが含まれるかワンホットエンコーディング処理を行う
3. 日付を`pandas.to_datetime`で変換する

※ 通常コミット or debt/non-debtコメントを含んだコミットを区別しておく



### 5-count_commit.py
目的：対象コメントが追加されたからのコミット回数/追加されてから最新リビジョン（最強データ指定）までの経過日数取得<br>
対象データ：`./4-onehot_encoding`内の全てのCSVファイル<br>
結果：`./5-count_commit`にCSVファイルを保存

1. 0:"commit 回数", 1:"SATD 追加 commit", 2:"初回コミット日時", 3:"最新リビジョンまでの経過日数" に基づいてデータを処理

※ 最強データに記載されていないファイルにもdebtが発生している可能性がある
※ TODO: ファイル削除を扱えていない...


### create_dateranges_graph.ipynb
対象コメント追加後からの経過日数に関するグラフ作成

### create_revision_graph.uptnb
対象プロジェクト/Dockerfileのリビジョン数に関するグラフ作成

### other ipynb file
filename_modify.ipynb など
コード作成のための確認テストを実行するためのファイル


# TODO
* ファイル削除情報を取得する