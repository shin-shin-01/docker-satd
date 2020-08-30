import pandas as pd
import os, re
from tqdm import tqdm

# TODO: インデントが深い場合に期待の動作をしない気がする
# for l in lines の後の処理を正規表現で書いたほうがいいかも？はじめに内容を把握しないと．

def main():
    saikyo = pd.read_csv('./saikyo-data.csv')
    inputs = os.listdir('./1-git_log') # target-csv-files
    outputs = os.listdir('./2-get_targetfile/')

    for i, filename in tqdm(enumerate(inputs)):
    
        if filename[-4:] != ".csv":
            continue
            
        ## 一度実行したものは除外
        if filename in outputs:
            continue
        
        id = filename.split('_')[0]
        # 最強データから対象のコメントを取得
        comments = saikyo[saikyo["id"]==int(id)]["comment"].values[0].splitlines()
        # print("\n".join(comments))

        df = pd.read_csv(f'./1-git_log/{filename}', index_col=0)
        # debtの追加（変更点）があったファイルを target_files にまとめる
        df.insert(value=0, loc=len(df.columns)-2, column="target_files")
        df.fillna(0, inplace=True)
        
        # diffが存在するもの（対象コメントが変更点に含まれる）
        idxlist = df[df["diff"] != 0].index.values.tolist()

        for idx in idxlist:
            # git log の中身を１行ずつ for文で回す
            lines = df.loc[idx, "diff"].splitlines()
            files = []
            nottarget_files = []
            
            ## diff で変更点をあげているが
            ## 本当にSATDが追加されたのか？どのファイルに追加されたのか？がわからないため
            ## 追加(+)されたときそのファイル名を保存 それ以外はただの変更コミットとしてファイル名を保存しておく
            for l in lines:
                if l[0:10] == "diff --git":
                    tmpfile = l[11:] # ファイル名を一時的に保存
                    nottarget_files.append(tmpfile) # 全てのファイルを一時的に not で保存

                try:
                    ## どれか一つでも
                    ## コメントが含まれる & 追加された行であること を条件
                    for comment in comments:
                        if ((comment in l) and (l[0] == "+")):
                            files.append(tmpfile)
                            nottarget_files.remove(tmpfile) # ここで除外
                            del tmpfile
                            break
                except NameError: # tmpfile が存在しない
                    continue
            
            try:
                del tmpfile
            except:
                pass
            
            df.loc[idx, "target_files"] = str(files)
            df.loc[idx, "file"] = str(nottarget_files)
            
        df.to_csv(f'./2-get_targetfile/{filename}')


if __name__ == "__main__":
    main()