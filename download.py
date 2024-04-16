import requests
import execjs
import json
import re
import os
import hashlib


url = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token='
list_url = 'https://music.163.com/playlist?id=9791125298'
header = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'Referer':
        'https://music.163.com/',
    'Cookie':
        'NMTID=00O4tGpdpR8kDMQvUlNlkW4zWRBCFEAAAGM7RbMMg; _iuqxldmzr_=32; _ntes_nnid=6258a4ebc0e2cdc6ab64299ffd4fb63b,1704784746109; _ntes_nuid=6258a4ebc0e2cdc6ab64299ffd4fb63b; WEVNSM=1.0.0; WNMCID=qlcfdv.1704784749071.01.0; WM_TID=44bs24S%2FMRNARUBUBRbE8L2iAnjtPI%2BA; ntes_utid=tid._.xap57pTv0ohBU1UUFEbVsbn2EyzqSHov._.0; sDeviceId=YD-qE7SX02OpwxBBxBFAQKRtG8RuONA52ko; __snaker__id=s73INAmdQ3vsX8MY; ntes_kaola_ad=1; __remember_me=true; MUSIC_U=00E76F1B776FAC086B46F91AE07EFD28C4F57A3AC7272A2AD7B1D606E78B99F4BD736A83CE7BB7C9C3F2DD9FA739FC0EAE79E0DD388AF6A263A8729121E22E06B87A0A4BD9A28AD5ADF7CE9346FC56D4E1058B5D7A0DC6AB9D3B4042E974C424DC208168819CD87375D7072B79BDECAAD946EBA5643300A9A0456F09DC94818DC0CC49D96390AAC3218D4E74907E231367C78DD98AE1A970407825D681A7E69BCA00F22E069A566E3436B4DD4E6A0C3BEBBDD52487A8D1D0E4710CA372DB5EE308FEAFED01E926CA91FD83B6F7531D56379C790E7B5AE055EFA4B3BCC4FE96BB87C5EC517ABC17F1DD9EAAEB2D15120044500CEC76F45F01EE69C58B70D24A5DB54B9AA5CA749695838198DA30A945E7D3FD4B8D7AAC1160DCA305D0AF90DD2BD119868C6FED7FC77EC659DFCB64C68A2F1E8AFAAE23983C445BFF60C26E7538485F6E296588A1780C26B8DE8658ABDBCB55948368BF20974427F5E5237D47BCA4; vinfo_n_f_l_n3=17f295ed979e0c92.1.0.1712345706269.0.1712345739208; __csrf=019bd2b451b8e93dc30166eb1f25a975; __csrf=019bd2b451b8e93dc30166eb1f25a975; WM_NI=BOwUGOPPOx%2BlVtQoDs3ScfM0Vz3tq43j7uuTv1IP1W3MqR10f%2F7GDtJcCAryL24%2BqctAAQafvEk9AfkMCqCCZHERZrREeLb6s2w0wUruy3oGfMpygcf3fhQXRSZTnP6lNjc%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb2b572b58c9983ed7bb49e8aa2d85f878b8badd47aa7bfa7dab5418abefeb8d32af0fea7c3b92a8291b9b6c64594908199aa6896ac9f90c779f18dad87d03c96a6fd95f440f1b6f996f860b6ef87b1b45df193bfb3b43ca6f1f9a8c7808abd8da2f17390eefcccf469b89f8fb2e46eb69ba5dac46ea9938d92c2499a988bb3d97a929babade13eb1eeb9d1f65fb2abb7d4ee4da693c09ae669a6edaa89d454928d96b5ed5cf6b4828be237e2a3; playerid=67520211; JSESSIONID-WYYY=XX5jIeBmXB03f3vU2QDKUvKOTuOsb9IfuiJYqECjKv6WcniXO0xZH3BDq%2Fqjhnc5bOGzlwwdAhPzXeTTD5fqlp4uzwC7t1i7wcuaFKUIgMIvmr2qWt3nl8yweI8%5Cb40Odl3UqF%2BPwaZX5lu1w1xeEhmIkzxl4qNphM6qU%2FO3Bs7wsri%2F%3A1713127429500',

}
name_file = "local.txt"


response = requests.get(url=list_url, headers=header)
html_text = response.text


song_id = re.findall(r'<li><a href="/song\?id=(.*?)">(.*?)</a></li>', html_text)
print(song_id)
song_dict = {}
for id in song_id:
    file_hash = hashlib.sha256(id[1].encode('utf-8')).hexdigest()
    song_dict[id[1]] = file_hash
    file_path = f".\\songs\\{file_hash}.m4a"
    if os.path.exists(file_path):
        print(f'{id[1]} Exists')
        continue
    else:
        file = open('m.js', 'r').read()
        m_js = execjs.compile(file)
        key = m_js.call('asrseaDict', id[0])
        data = {
            'params': key['encText'],
            'encSecKey': key['encSecKey']
        }
        text = requests.post(url, data=data, headers=header).text
        json_text = json.loads(text)
        song_url = json_text['data'][0]['url']
        song = requests.get(song_url, headers=header).content
        with open(file_path, 'wb') as f:
            f.write(song)
            f.close()
            print(f'{id[1]} Downloaded')


song_json = json.dumps(song_dict, ensure_ascii=False, indent=4)
with open('song.json', 'w+', encoding='utf-8') as f:
    f.write(song_json)
    f.close()


with open('song.json', 'r', encoding='utf-8') as f:
    dict1 = json.load(f)
    f.close()
with open('uploaded.json', 'r', encoding='utf-8') as f:
    dict2 = json.load(f)
    f.close()


upload_keys = set(dict1.keys()) - set(dict2.keys())
upload_dict = {key: dict1[key] for key in upload_keys}


for key in upload_dict.keys():
    song_hash = upload_dict[key]
    file_local = os.path.join('songs', song_hash + '.m4a')
    uploaded_file_path = 'uploaded.txt'
    url = 'http://192.168.31.62:5000/upload'
    files = {
        'file': (song_hash + '.m4a', open(file_local, 'rb'), 'audio/m4a'),
    }
    print('Uploading ' + key + ' ...')
    response = requests.post(url, files=files)
    # 打印响应结果
    print(response)
    if response.status_code == 200:
        dict2[key] = song_hash
    else:
        print('Upload failed')
        break


uploaded_json = json.dumps(dict2, ensure_ascii=False, indent=4)
with open('uploaded.json', 'w+', encoding='utf-8') as f:
    f.write(uploaded_json)
    f.close()
print('Upload completed')
