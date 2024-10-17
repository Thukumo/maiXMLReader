import os, csv, xml.etree.ElementTree, sys

def files(path):
    for path, _, files in os.walk(path):
        for file in files: yield path, file

lines = []
#カレントディレクトリ以下のすべてのファイルから、ファイル名がMusic.xmlのものを取得し、そのデータを読む
for path, file in files("."):
    if file == "Music.xml":
        root = xml.etree.ElementTree.parse(os.path.join(path, file)).getroot()
        song_id, song_name = root.find("name").find("id").text, root.find("name").find("str").text
        artist_name = root.find("artistName").find("str").text
        lines.append([int(song_id), song_name, artist_name])
        #print(f"Song ID: {song_id}\nSong Name: {song_name}\nArtist Name: {artist_name}")

if True: #ここがTrueの場合、データのなかったIDを空欄で埋める(Falseで埋めない)
    memo = set(l[0] for l in lines)
    for i in range(1, max(memo)):
        if i not in memo: lines.append([i, "", ""])

lines.sort(key=lambda x: x[0])
#CSVファイルに書き込む(存在する場合は上書き)
with open(sys.argv[1] if len(sys.argv) == 2 else "Music.csv", "w", newline="", encoding="utf-16") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["Song ID", "Song Name", "Artist Name"])
    for l in lines: writer.writerow(l)
