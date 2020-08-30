import pandas as pd
import os, re
from tqdm import tqdm

def colname_modify(col):
    if col[:2] == "a/":
        col = col.split(' ')[0][2:]
    return col


def main():
    saikyo = pd.read_csv('./saikyo-data.csv')
    inputs = os.listdir('./3-renamed_files/') # target-csv-files
    outputs = os.listdir('./4-onehot_encoding/')


    for i, filename in enumerate(inputs):
        
        ## ファイル拡張子が違うものは除外
        if filename[-4:] != '.csv':
            continue

        ## 実行済みのものは ignore
        if filename in outputs:
            continue
            
        df = pd.read_csv(f'./3-renamed_files/{filename}', index_col=0)
        print(f'\n============= {i}/{len(inputs)}')
        print(filename)

        ## コメントが付与された行取得
        last_check = df.copy(deep=True)
        last_check = last_check[ last_check["diff"] != str(0)]
        
        ## コメントが付与されたファイル名取得
        files = last_check["target_files"].values
        # a/以降の名前のみ取得
        files = re.findall(r'\'([^\s]*)\s[a/|b/][^\']*\'', str(files))
        files = list(set(files)) ##重複削除

        ## 日付の形式を変更
        df = df[df["date"] != "[]"] ##TODO: ここ日付がない時ってあったっけ
        df["date"] = pd.to_datetime(df["date"].apply(lambda dt: re.findall(r'\D{3}\s\D{3}\s\d*\s\d{2}:\d{2}:\d{2}\s\d{4}\s[-|+]\d{4}', dt)[0]))

        ## ワンホットエンコーディング的なもの
        count = {"commitid": [], "date": [], "diff": []}
        for file in files:
            count[str(file)] = []
        
        for index, row in df.iterrows():
            ## ======= 通常用  ==========
            count["commitid"].append(row["commitid"])
            count["date"].append(row["date"])
            count["diff"].append(0)
            
            for file in files:
                if file in row["file"]:
                    count[str(file)].append(1)          
                else:
                    count[str(file)].append(0)
            
            ## ======= Diff用  ==========
            if row["diff"] != "0":
                count["commitid"].append(row["commitid"])
                count["date"].append(row["date"])
                count["diff"].append(1)
                
                for file in files:
                    if file in row["target_files"]:
                        count[str(file)].append(1)          
                    else:
                        count[str(file)].append(0)
            
        df = pd.DataFrame.from_dict(count)
        df.columns = list(map(lambda col: colname_modify(col), df.columns))
        
        try: ## Diffは存在していたけどSATD追加ではなかったときに [] が表示されてしまう
            df.drop(columns="[]", inplace=True)
        except KeyError:
            pass

        df.to_csv(f'./4-onehot_encoding/{filename}')


if __name__ == "__main__":
    main()