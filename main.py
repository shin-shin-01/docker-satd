import pandas as pd
import re, os
import subprocess
from tqdm import tqdm

'''
main.py
    1. データ取得 ./result/
filename_modiify.ipynb
    1. rename処理を行い、row["file"], row["diff"]のファイル全てを最新版に。
    2. diff で目的のファイルネーム取得
analysis.ipynb
    1. diff-filename をもとにワンホットエンコーディング
'''



## 変更点に関してコメントが含まれるかどうか判定する
## 最初の段階では、全てのコメントが一度にそのまま追加されると想定する
def CheckKeyWords(log, comments):
    for comment in comments:
        if comment in log:
            return True
    return False



def main(debt, other=False):
    # 最強データ読み込み
    df = pd.read_csv('saikyo-data.csv', index_col=0)
    ## クラス分類でソートしておく
    df = df.sort_values('class')

    if other: ## 分類作業を行なっていないプロジェクト達
        df.fillna({"class":0}, inplace=True)
        df = df[df["class"] == 0]

    elif debt:## SATDであるものを対象とする
        ## クラス分類が存在しないものを削除
        df.dropna(subset=['class'], inplace=True)
        ## クラスが non-debt は削除
        df = df[df["class"] != "non-debt"]
    else:## non-debt を対象とする
        ## クラスが non-debt のみ利用
        df = df[df["class"] == "non-debt"]
    

    ## 結果格納ディレクトリの中身
    result_dir = os.listdir(path='./result')

    for index, row in tqdm(df.iterrows()):
        print('--------------> ', str(index))

        # プロジェクトを git clone 
        ## クローン先ディレクトリ
        cwd = "./tmp"
        project = row["project"] # ex) '31z4/storm-docker'

        project_name = project.split('/')[1]
        index = str(index)

        ## filename
        if other:
            output_filename = f'{index}_{project_name}_Uncategorized.csv'
        elif debt:
            output_filename = f'{index}_{project_name}.csv'
        else:
            output_filename = f'{index}_{project_name}_nondebt.csv'

        ## 既に存在しているものはPASS (修正時にはコメントアウト)
        if output_filename in result_dir:
            continue

        giturl = f'https://github.com/{project}'
        foldername = "_".join(project.split('/'))
        cmd = f'git clone {giturl} {foldername}'
        ## git clone
        print('> Start_clone')

        clone = subprocess.run(list(cmd.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE)

        # プロジェクト単位で git log を取得
        ## 対象の最新リビジョンを指定
        startRevision = row["revision"]
        ## 対象コメントを指定  (行単位で分割)
        comments = row["comment"]
        comments = comments.splitlines()
        ## コマンド/実行ディレクトリ を指定
        cwd = './tmp/' + foldername
        cmd = f'git log -p'

        print('> Start_log')
        ## utf-8 エラーをignoreしてる
        logs = subprocess.run(list(cmd.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore")
        logs = re.split(r'\ncommit\s|\n\s{4}commit\s', logs.stdout)

        ## 指定のリビジョンを発見すると開始する
        startFLG = False
        ## 結果
        results = {"commitid":[], "date":[], "file":[], "diff":[], "rename": []}

        for num, log in enumerate(logs):
            if num == 0:
                commitid = log[7:47]
            else:
                commitid = log[0:40]
            
            if commitid == startRevision:
                startFLG = True
            if startFLG:
                ## コミット日
                date = re.findall(r'\nDate:\s*([^\n]*)\n|\n\s{4}Date:\s*([^\n]*)\n', log)

                results["commitid"].append(commitid)
                results["date"].append(date)

                discover = CheckKeyWords(log, comments)

                changefile = re.findall(r'diff\s--git\s([^\n]*)\n', log)
                renamefile = re.findall(r'rename\sfrom\s([^\n]*)\nrename\sto\s([^\n]*)\n', log)
                results["rename"].append(renamefile)
                results["file"].append(changefile)

                if discover:
                    results["diff"].append(log)
                else:
                    results["diff"].append(None)
                
            else:
                pass
        
        ## 結果格納
        result = pd.DataFrame.from_dict(results)
        result.to_csv("./result/"+output_filename)


if __name__ == "__main__":
    # main(debt=True)
    # main(debt=False)
    main(debt=False, other=True)