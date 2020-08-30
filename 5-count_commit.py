import pandas as pd
import os, re
from tqdm import tqdm
from datetime import datetime

"""
pandas.DataFrame
index={0:"追加後 commit 回数", 1:"SATD 追加 commit", 2:"初回コミット日時", 3:"最新リビジョンまでの日数"}
"""


def main():
    saikyo = pd.read_csv('./saikyo-data.csv')
    inputs = os.listdir('./4-onehot_encoding/')
    outputs = os.listdir("./5-count_commit/")
    error = {"IndexError":[]}

    for i, filename in enumerate(inputs):

        ## ファイル拡張子が違うものは除外
        if filename[-4:] != '.csv':
            continue

        ## 実行済みのものは ignore
        if filename in outputs:
            continue
            
        df = pd.read_csv(f'./4-onehot_encoding/{filename}', index_col=0)
        id = int(filename.split('_')[0])
        target_saikyo = saikyo[ saikyo["id"]==id ]
                
        print(f'\n\n========== {i}/{len(inputs)}')
        print(filename)
        print(f'satd-type : {target_saikyo["class"].values[0]}')
        
        project = target_saikyo["project"].values[0]
        target_file = target_saikyo["path"].values[0].replace(project, '').splitlines()
        print('targetfile : ', target_file)
        print('-'*10)
        
        ## ATTENTION: 追加前コミットをignoreすることを注意する
        ## debt/nont-debt コメント が追加されてからのコミット回数を知りたい
        ## よって debt/nont-debt コメント 追加前の変更コミット(diff==0, and file==1 ) を ignore 
        for col in df.columns.tolist()[3:]:
            try:
                idx = df[(df["diff"]==1) & (df[col]==1)].index.tolist()[-1]
                ## SATD追加時以前のコミットを０カウント
                df.loc[idx+1:][col] = 0
            except IndexError:
                ## SATD追加ファイルではないもの達
                error["IndexError"].append(f'{filename}__{col}')
                df.drop([col], axis=1, inplace=True)
        
        ## 初期コミットの日付を確認
        columnslist = df.columns.tolist()[3:]
        olddates = {}
        elapseddates = {}
        
        for col in columnslist:
            old = datetime.strptime(df[(df[col]==1)&(df["diff"]==1)]["date"].values.tolist()[-1][:-6], '%Y-%m-%d %H:%M:%S')
            now = datetime.strptime(df["date"].values.tolist()[0][:-6], '%Y-%m-%d %H:%M:%S')
            olddates[col] = str(old)
            elapseddates[col] = str(now-old)
            
        ## satd追加日時  
        olddates = pd.Series(olddates)
        ## 経過日数
        elapseddates = pd.Series(elapseddates)
        
        ## 変更があった時のコミット回数
        diff_df = df[df["diff"] == 1].sum()[3:]
        ## 変更がなかった時のコミット回数
        not_diff_df = df[df["diff"] == 0].sum()[3:]
        
        df = pd.DataFrame([not_diff_df, diff_df, olddates, elapseddates]).rename(index={0:"commit 回数", 1:"SATD 追加 commit", 2:"初回コミット日時", 3:"最新リビジョンまでの経過日数"})

        df.to_csv(f'./5-count_commit/{filename}')


if __name__ == "__main__":
    main()