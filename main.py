import os, csv, xml.etree.ElementTree, sys, itertools

def files(path):
    for path, _, files in os.walk(path):
        for file in files: yield path, file

if sys.version_info.major != 3 or sys.version_info.minor < 10:
    print("このメッセージが出たら伝えてください\n修正します")
    exit()
fumens = []
dx_fumens = []
utage_fumens = []
#カレントディレクトリ以下のすべてのファイルから、ファイル名がMusic.xmlのものを取得し、そのデータを読む
for path, file in files("."):
    if file == "Music.xml":
        root = xml.etree.ElementTree.parse(os.path.join(path, file)).getroot()
        song_id, song_name = root.find("name").find("id").text, root.find("name").find("str").text
        artist_name = root.find("artistName").find("str").text
        match(len(song_id)):
            case 1 | 2 | 3 | 4:
                fumens.append([int(song_id), song_name, artist_name])
            case 5: #1nnnn がでらっくす譜面らしい
                dx_fumens.append([int(song_id[1:]), song_name, artist_name])
            case 6: #1nnnnn が宴譜面らしい
                utage_fumens.append([int(song_id[2:]), song_name, artist_name])
            case _:
                print(f"IDから譜面のタイプを識別できませんでした: {song_id=}")

fill_brank = True #ここがTrueの場合、データのなかったIDを空欄で埋める(Falseで埋めない)

#データの集計
used_id = set(l[0] for l in fumens + dx_fumens + utage_fumens)
lines = [[i+1, "", "", "×", "×", "×", []] for i in range(max(used_id))]
fumen_lists = [fumens, dx_fumens]
for i in range(len(fumen_lists)):
    for fumen in fumen_lists[i]:
        lines[fumen[0]-1][1:3] = fumen[1:3]
        lines[fumen[0]-1][3+i] = "〇"
for fumen in utage_fumens:
    lines[fumen[0]-1][5] = "〇"
    lines[fumen[0]-1][6].append(fumen[1])
for line in lines: line[6] = ", ".join(line[6])
if fill_brank:
    for i in range(1, len(lines)+1):
        if i not in used_id: lines[i-1] = [i, "", "", "", "", "", ""]
else: lines = [lines[i] for i in range(len(lines)) if i+1 in used_id]

#CSVファイルに書き込む(存在する場合は上書き)
try:
    with open(sys.argv[1] if len(sys.argv) == 2 else "maimai.csv", "w", newline="", encoding="utf-16") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Song ID", "タイトル", "アーティスト名", "ST", "DX", "宴", "宴譜面名"])
        for l in lines: writer.writerow(l)
except PermissionError:
    print("ファイルが開けませんでした。ファイルを閉じてから再度実行してください。")
    exit()
