import requests
import hashlib

with open('local.txt', 'r', encoding='utf-8') as f:
    local = [line.strip('/.*?/\n') for line in f.readlines()]
with open('uploaded.txt', 'r', encoding='utf-8') as f:
    uploaded = [line.strip('/.*?/\n') for line in f.readlines()]

upload = list(set(local) - set(uploaded))

for song in upload:
    # 设置上传的文件路径
    song_hash = hashlib.sha256(song.encode('utf-8')).hexdigest()
    file_local = '.\\songs\\' + song_hash + '.m4a'
    uploaded_file_path = 'uploaded.txt'
    # 设置上传的URL
    url = 'http://192.168.31.62:5000/upload'
    # 构建表单数据
    files = {
        'file': (song, open(file_local, 'rb'), 'audio/m4a'),
    }
    # 发送POST请求
    response = requests.post(url, files=files)
    # 打印响应结果
    print(response.text)

    if response.status_code == 200:
        with open(uploaded_file_path, 'a+', encoding='utf-8') as file:
            file.write(song + '\n')
            file.close()
    else:
        print('Upload failed')
