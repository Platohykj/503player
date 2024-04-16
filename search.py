import re


def fuzzy_search(search_term, song_text):
    pattern = re.compile('.*{}.*'.format(search_term), re.IGNORECASE)
    songs = re.findall(r'/(.*?)/', song_text)
    matching_songs = [song for song in songs if re.match(pattern, song)]
    return matching_songs


def read_song_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        song_text = file.read()
    return song_text


def main():
    file_path = "uploaded.txt"
    song_text = read_song_text_from_file(file_path)
    search_term = input("请输入搜索词：")
    matching_songs = fuzzy_search(search_term, song_text)
    if matching_songs:
        print("搜索结果：")
        for song in matching_songs:
            print(song + ".m4a")
    else:
        print("没有找到匹配的歌曲。")


if __name__ == "__main__":
    main()
