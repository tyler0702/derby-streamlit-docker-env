
import requests
import urllib.parse
import os
from bs4 import BeautifulSoup
import json

def generate_wikipedia(artist_name):
    # 現在のファイルのディレクトリを取得
    base_dir = os.path.dirname(__file__)
    # 'src/api' から 'src/data' に移動するための相対パスを使用
    file_path = os.path.join(base_dir, '..', 'data', 'artist.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        jsondata = json.load(file)
        mappings = jsondata.get("change", {})

    # アーティスト名に対応するエントリがあればそれを使用し、なければ通常の名前をURLエンコードする
    wiki_title = mappings.get(artist_name, artist_name)
    encoded_name = urllib.parse.quote(wiki_title)
    url = f"https://ja.wikipedia.org/wiki/{encoded_name}"
    
    start_heading = '概要'

    response = requests.get(url)
    # response.raise_for_status()  # ステータスコードが200以外の場合はエラーを発生させる
 
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # `<sup>` タグを除去
    for sup_tag in soup.find_all('sup'):
        sup_tag.extract()

    # セクションのタイトルに対応するh2タグを見つける
    for header in soup.find_all('span', class_='mw-headline'):
        if header.text == start_heading:
            # 見つかったタイトルの次の要素を取得
            current = header.parent
            content = []
            # 次のh2タグが見つかるまで内容を収集
            while True:
                current = current.next_sibling
                if current is None or (current.name == 'h2' and current.find('span', class_='mw-headline')):
                    break
                if current.name in ['p', 'ul', 'ol', 'dl']:
                    content.append(current.text)
            return '\n'.join(content)
    return f"ごめんなさいなかったよー"