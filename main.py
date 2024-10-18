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

lines = []
if fill_brank:
    tmp = set([l[0] for l in fumens + dx_fumens + utage_fumens])
    lines = [[i, "", "", "", "", "", ""] for i in range(1, max(tmp)) if i not in tmp]

#楽曲のリストをいい感じに結合
marks = {}
fumen_lists = [fumens, dx_fumens, utage_fumens]
for (i, j) in itertools.combinations(range(len(fumen_lists)), 2):
    tmp = set(fumen_lists[j][k][0] for k in range(len(fumen_lists[j])))
    for fumen in fumen_lists[i]:
        if fumen[0] not in marks: marks[fumen[0]] = [fumen, set([i])]
        else: marks[fumen[0]][1].add(i)
        if fumen[0] in tmp: marks[fumen[0]][1].add(j)

#宴譜面名の抽出とか
tmp = [fumen[0] for fumen in utage_fumens]
for fumen in marks.values():
    normal_exists, dx_exists, utage_exists = 0 in fumen[1], 1 in fumen[1], 2 in fumen[1]
    lines.append(fumen[0]+["×" if not normal_exists else "〇",
"×" if not dx_exists else "〇",
"×" if not utage_exists else "〇",
", ".join(map(lambda x: utage_fumens[x][1], [i for i in range(len(tmp)) if tmp[i] == fumen[0][0]])) if utage_exists else ""])

lines.sort(key=lambda x: x[0])
#CSVファイルに書き込む(存在する場合は上書き)
try:
    with open(sys.argv[1] if len(sys.argv) == 2 else "Music.csv", "w", newline="", encoding="utf-16") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Song ID", "タイトル", "アーティスト名", "ST", "DX", "宴", "宴譜面名"])
        for l in lines: writer.writerow(l)
except PermissionError:
    print("ファイルが開けませんでした。ファイルを閉じてから再度実行してください。")
    exit()
