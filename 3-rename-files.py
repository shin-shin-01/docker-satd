import pandas as pd
import os, re
from tqdm import tqdm


def main():
    saikyo = pd.read_csv('./saikyo-data.csv')
    inputs = os.listdir('./2-get_targetfile/') # target-csv-files
    outputs = os.listdir('./3-renamed_files/')


    for i, filename in enumerate(inputs):
        
        print(f'============= {i}/{len(inputs)}')
        print(filename)
        
        if filename != "433_mongo.csv":
            continue

        if filename[-4:] != ".csv":
            continue
            
        ## 一度実行したものは除外
        if filename in outputs:
            continue
            
        df = pd.read_csv(f'./3-renamed_files/{filename}', index_col=0)
            
        renamefiles = ','.join(df["rename"].values.tolist())
        renamefiles = re.findall(r'\(\'([^\)]*)\'\)', renamefiles)[::-1] # 歴史を遡るため逆順に．
        
        ## TODO: 辞書に変換するときにエラーが出た
        ## 2433_cntk で以下のrenameが発生したため
        ## "BrainScript/BrainScript--extending the CNTK config language, Frank Seide August 2015.pptx', 'Source/CNTK/BrainScript/Doc/BrainScript--extending the CNTK config language, Frank Seide August 2015.pptx"
        try:
            renamefiles = dict(map(lambda rename: rename.replace('\'', '').split(', '), renamefiles))
        except ValueError:
            renamefiles = list(map(lambda rename: rename.replace('\'', '').split(', '), renamefiles))
            for i in renamefiles:
                if len(i) == 2:
                    pass
                else:## Error: 2つ以上のペアがでたら削除
                    renamefiles.remove(i)
            renamefiles = dict(renamefiles)
            
        renamepairs = {"before":[], "after":[]}
        
        ## before の list を
        ## 同じ indexの after に変換する
        for before, after in renamefiles.items():
            ## 抵抗してみました
            ## Dockerに関する名前が絶対にあるという強い自信
            if "docker" in before:
                pass
            elif "Docker" in before:
                pass
            else:
                continue
                
            try: # 変更前がすでに変更後として rename されていたら
                idx = renamepairs["after"].index(before)
                renamepairs["after"][idx] = after #新しい変更先の名前を指定
                renamepairs["before"][idx].append(before)
            except ValueError:
                renamepairs["after"].append(after)
                renamepairs["before"].append([before]) # beforeは配列

        for num  in range(len(renamepairs["after"])):
            ## rename before -> after
            ## a/b -> a/
            before = '|'.join(renamepairs["before"][num])
            before = f'(a/|b/)({before})'
            after = 'a/'+renamepairs["after"][num]

            df["file"] = df["file"].apply(lambda s: re.sub(before, after, str(s)))
            df["target_files"] = df["target_files"].apply(lambda s: re.sub(before, after, str(s)))

        df.to_csv(f'./3-renamed_files/{filename}')    

if __name__ == "__main__":
    main()