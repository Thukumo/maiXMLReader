import os, csv, xml.etree.ElementTree, sys, re

fill_brank = True #ここがTrueの場合、データのなかったIDを空欄で埋める(Falseで埋めない)
fill_all_status = False #存在しなかった譜面の欄に×を表示するかどうか
deleted_path = "deleted.txt" #削除譜面リストのパス
unused_path = "unused.txt" #未使用譜面リストのパス

def files(path, name):
    for path, _, files in os.walk(path):
        for file in files:
            if file == name: yield os.path.join(path, file)

def read_text(path):
    ids = set()
    nf = False
    def read(file):
        lis = []
        with open(file, "r") as f:
            for line in f:
                try:
                    song_id = line.strip()
                    if song_id == "": continue
                    num =  0 if len(song_id) < 5 else len(song_id)-3 -1
                    lis.append(int(song_id[num:]))
                except ValueError:
                    print("譜面IDを読み取れませんでした: "+line.strip())
        return lis
    try:
        ids.add(*read(path))
    except FileNotFoundError:
        print(f"{os.path.basename(path)}が見つかりませんでした。\nカレントディレクトリから探索します。")
        nf = True
        for file in files(".", os.path.basename(path)):
            ids.add(*read(file))
            nf = False
    return nf, ids

(del_nf, deleted_id), (unu_nf, unused_id) = read_text(deleted_path), read_text(unused_path)
if del_nf or unu_nf: print("")
if del_nf: print("削除譜面リストが見つかりませんでした。")
if unu_nf: print("未使用譜面リストが見つかりませんでした。")
if del_nf or unu_nf:
    print("")
    if input("↑のデータを使わずに続行しますか? (y/n): ").lower() != "y": exit()
fumen_lists = [[], [], [], []] #ST, DX, 宴, 未使用 or 削除譜面
#カレントディレクトリ以下のファイル名がMusic.xmlであるすべてのファイルを取得し、そのデータを読む
for file in files(".", "Music.xml"):
    root = xml.etree.ElementTree.parse(file).getroot()
    song_id = root.find("name").find("id").text
    num =  0 if len(song_id) < 5 else len(song_id)-3 -1
    if any(notes.find("isEnable").text == "true" for notes in root.find("notesData").findall("Notes")):
        fumen_lists[num].append([int(song_id[num:]), root.find("name").find("str").text, root.find("artistName").find("str").text, num+3])
    else:
        fumen_lists[3].append([int(song_id[num:]), root.find("name").find("str").text, root.find("artistName").find("str").text, 6])

#データの集計
used_id = {l[0] for list in fumen_lists for l in list}
lines = [[i+1, None, "", "", "", "", [], ""] for i in range(max(used_id))]
for lis in fumen_lists:
    if len(lis) != 0: n = lis[0][3]
    for fumen in lis:
        if lines[ind := fumen[0]-1][1] is None:
            lines[ind][1:3] = fumen[1:3]
            #宴譜面しか譜面がない場合に曲名先頭の"[(漢字1文字)]"を消すための処理 (公開前 and 宴譜面しかない)楽曲かつ変な曲名だと曲名が欠ける(公開前の宴譜面の楽曲名には[(漢字)]がつかないため)
            if n == 5 and bool(re.fullmatch(r"^\[[\u4E00-\u9FFF]\]", fumen[1][:3])): lines[ind][1] = lines[ind][1][3:]
        if n == 5: lines[ind][6].append(fumen[1])
        if n != 6: lines[ind][n] = "〇"
#しあげ
if fill_all_status:
    for i in used_id: lines[i-1][2:5] = ["〇" if lines[i-1][j] == "〇" else "×" for j in range(2, 5)]
if not fill_brank: lines = [line for i, line in enumerate(lines) if i+1 in used_id]
for i in range(len(lines)):
    if lines[i][1] is None: lines[i][1] = ""
    lines[i][6] = ", ".join(lines[i][6])
    if i+1 in deleted_id: lines[i][7] = "削除曲"
    elif i+1 in unused_id: lines[i][7] = "未使用"
    if i+1 in deleted_id and i+1 in unused_id:
        print(f"楽曲ID{i+1}は削除曲・未使用曲リストの両方に登録されています")
        lines[i][7] = "削除曲・未使用"

#CSVファイルに書き込む(存在する場合は上書き)
try:
    with open(sys.argv[1] if len(sys.argv) == 2 else "maimai.csv", "w", newline="", encoding="utf-16") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Song ID", "タイトル", "アーティスト名", "ST", "DX", "宴", "宴譜面名", "備考"])
        for l in lines: writer.writerow(l)
except PermissionError:
    print("指定されたCSVファイルが開けませんでした。ファイルを閉じてから再度実行してください。")
    exit()
