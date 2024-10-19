import os, csv, xml.etree.ElementTree, sys

def files(path):
    for path, _, files in os.walk(path):
        for file in files: yield path, file

fumen_lists = [[], [], []] #ST, DX, 宴
#カレントディレクトリ以下のすべてのファイルから、ファイル名がMusic.xmlのものを取得し、そのデータを読む
for path, file in files("."):
    if file == "Music.xml":
        root = xml.etree.ElementTree.parse(os.path.join(path, file)).getroot()
        song_id, song_name = root.find("name").find("id").text, root.find("name").find("str").text
        artist_name = root.find("artistName").find("str").text
        num = 0 if len(song_id) < 5 else len(song_id)-3 -1
        fumen_lists[num].append([int(song_id[num:]), song_name, artist_name, num+3])

fill_brank = True #ここがTrueの場合、データのなかったIDを空欄で埋める(Falseで埋めない)

#データの集計
used_id = {l[0] for fumen_list in fumen_lists for l in fumen_list}
lines = [[i+1, "", "", "×", "×", "×", []] for i in range(max(used_id))]
for i in range(len(fumen_lists)):
    n = fumen_lists[i][0][3] #要素が0であることはないと思うからこれで
    for fumen in fumen_lists[i]:
        if n == 5: lines[fumen[0]-1][6].append(fumen[1])
        else: lines[fumen[0]-1][1:3] = fumen[1:3]
        lines[fumen[0]-1][n] = "〇"
lines = [line if i+1 in used_id else [i+1, "", "", "", "", "", ""] for i, line in enumerate(lines)] if fill_brank else [line for i, line in enumerate(lines) if i+1 in used_id]
for line in lines: line[6] = ", ".join(line[6])

#CSVファイルに書き込む(存在する場合は上書き)
try:
    with open(sys.argv[1] if len(sys.argv) == 2 else "maimai.csv", "w", newline="", encoding="utf-16") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Song ID", "タイトル", "アーティスト名", "ST", "DX", "宴", "宴譜面名"])
        for l in lines: writer.writerow(l)
except PermissionError:
    print("ファイルが開けませんでした。ファイルを閉じてから再度実行してください。")
    exit()
