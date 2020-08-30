import pandas as pd
import re, os, sys
import subprocess
from tqdm import tqdm


# 変更点に関してコメントが含まれるかどうか判定する
# コメントが１つでも含まれると True
# 追加コメントであるかは　後で判断する
def CheckKeyWords(log, comments):
    for comment in comments:
        if comment in log:
            return True
    return False


def main(debt):
    # 最強データ読み込み
    df = pd.read_csv('saikyo-data.csv', index_col=0)
    ## クラス分類でソートしておく
    df = df.sort_values('class')

    if debt:## SATDであるものを対象とする
        ## クラス分類が存在しないものを削除
        df.dropna(subset=['class'], inplace=True)
        df = df[df["class"] != "non-debt"]
    else:## non-debt を対象とする
        df = df[df["class"] == "non-debt"]
    

    ## 結果格納ディレクトリの中身
    result_dir = os.listdir(path='./1-git_log')

    for index, row in tqdm(df.iterrows()):
        print('--------------> ', str(index))

        # プロジェクトを git clone 
        ## クローン先ディレクトリ
        cwd = "./0-clone-repository"
        project = row["project"] # ex) '31z4/storm-docker'

        project_name = project.split('/')[1]
        index = str(index)

        ## filename
        if debt:
            output_filename = f'{index}_{project_name}.csv'
        else:
            output_filename = f'{index}_{project_name}_nondebt.csv'

        ## 既に存在しているものはPASS (修正時にはコメントアウト)
        if output_filename in result_dir:
            continue

        ##  === git clone ===========
        print('> Start_clone')

        giturl = f'https://github.com/{project}'
        foldername = "_".join(project.split('/'))
        cmd = f'git clone {giturl} {foldername}'

        clone = subprocess.run(list(cmd.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE)

        ##  === プロジェクト単位で git log を取得 =====
        print('> Start_log')

        startRevision = row["revision"] # 対象の最新リビジョンを指定
        comments = row["comment"] # 対象コメントを指定  (行単位で分割)
        comments = comments.splitlines()
        cwd = './0-clone-repository/' + foldername # コマンド/実行ディレクトリを指定
        cmd = f'git log -p'

        ## utf-8 エラーをignoreしてる
        logs = subprocess.run(list(cmd.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore")
        #TODO: インデントが深いコミットを発見したため処理（さらに深いインデントは未調査）
        logs = re.split(r'\ncommit\s|\n\s{4}commit\s', logs.stdout)

        ## 指定のリビジョンを発見すると開始する
        startFLG = False
        ## 結果
        results = {"commitid":[], "date":[], "file":[], "diff":[], "rename": []}

        for num, log in enumerate(logs):
            if num == 0: ## '\ncommit\s'のため初期ログは例外処理
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
        result.to_csv("./1-git_log/"+output_filename)


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print("コマンド引数にて debt/non-debt を指定してください")
    elif args[1] == 'debt':
        main(debt=True)
    elif args[1] == 'non-debt':
        main(debt=False)
    else:
        print("正しい引数を与えてください debt/non-debt")