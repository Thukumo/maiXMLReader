import os, csv, xml.etree.ElementTree, sys, re

def files(path):
    for path, _, files in os.walk(path):
        for file in files: yield path, file

fumen_lists = [[], [], []] #ST, DX, 宴
#カレントディレクトリ以下のすべてのファイルから、ファイル名がMusic.xmlのものを取得し、そのデータを読む
for path, file in files("."):
    if file == "Music.xml":
        root = xml.etree.ElementTree.parse(os.path.join(path, file)).getroot()
        song_id = root.find("name").find("id").text
        num = 0 if len(song_id) < 5 else len(song_id)-3 -1
        fumen_lists[num].append([int(song_id[num:]), root.find("name").find("str").text, root.find("artistName").find("str").text, num+3])

fill_brank = True #ここがTrueの場合、データのなかったIDを空欄で埋める(Falseで埋めない)
fill_all_status = False #存在しなかった譜面の欄に×を表示するかどうか

#データの集計
used_id = {l[0] for fumen_list in fumen_lists for l in fumen_list}
lines = [[i+1, None, "", "", "", "", []] for i in range(max(used_id))]
for lis in fumen_lists:
    try: n = lis[0][3]
    except IndexError: pass #宴譜面の前例があった
    for fumen in lis:
        ind = fumen[0]-1
        if n == 5: lines[ind][6].append(fumen[1])
        if lines[ind][1] is None:
            lines[ind][1:3] = fumen[1:3]
            #宴譜面しか譜面がない場合に曲名先頭の"[(漢字1文字)]"を消すための処理 (公開前 and 宴譜面しかない)楽曲かつ変な曲名だと曲名が欠ける(公開前の宴譜面の楽曲名には[(漢字)]がつかないため)
            if n == 5 and bool(re.fullmatch(r"^\[[\u4E00-\u9FFF]\]", fumen[1][:3])): lines[ind][1] = lines[ind][1][3:]
        lines[ind][n] = "〇"

if fill_all_status:
    for i in used_id: lines[i-1][2:5] = ["〇" if lines[i-1][j] == "〇" else "×" for j in range(2, 5)]
if not fill_brank: lines = [line for i, line in enumerate(lines) if i+1 in used_id]
for i in range(len(lines)):
    if fill_brank and lines[i][1] is None: lines[i][1] = ""
    lines[i][6] = ", ".join(lines[i][6])

#CSVファイルに書き込む(存在する場合は上書き)
try:
    with open(sys.argv[1] if len(sys.argv) == 2 else "maimai.csv", "w", newline="", encoding="utf-16") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Song ID", "タイトル", "アーティスト名", "ST", "DX", "宴", "宴譜面名"])
        for l in lines: writer.writerow(l)
except PermissionError:
    print("ファイルが開けませんでした。ファイルを閉じてから再度実行してください。")
    exit()
