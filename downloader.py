import urllib
from bs4 import BeautifulSoup
import re
import json


def get_page_urls():
    """Crawls for video urls"""
    
    urls = []
    counter = 1
    
    while True:
        try:
            resp = urllib.request.urlopen(f"https://baltimore.cbslocal.com/category/its-academic/page/{counter}")
            soup = BeautifulSoup(resp, "lxml")
            for link in soup.findAll('a', attrs={'href': re.compile(r'^https://baltimore.cbslocal.com/\d+/\d+/\d+/its-academic')}):
                urls.append(link.get('href'))
            counter += 1
            
        except urllib.error.HTTPError as e:
            break

    return urls


def get_videos(urls):
    """Download videos"""
    
    for url in urls:
        ids = []
        resp = urllib.request.urlopen(url)
        soup = BeautifulSoup(resp, "lxml")
        
        # Collect video ids
        ids = []
        for div in soup.findAll('div', {'id': re.compile(r'^p\d+')}):
            player_data = json.loads(div.next_sibling['data-anvp'])

            # Get video data from api
            if 'video' in player_data:
                ids.append(player_data['video'])
            elif 'playlist' in player_data:
                ids += player_data['playlist']

        ids = list(set(ids))
        print(ids)

        # Download videos
        for video_id in ids:
            try:
                with urllib.request.urlopen(f"https://tkx2-prod.anvato.net/rest/v2/mcp/video/{video_id}?anvack=DVzl9QRzox3ZZsP9bNu5Li3X7obQOnqP") as video_data_resp:
                    video_data = json.loads(video_data_resp.read()[22:-1].decode('utf-8'))

                    # Find downloadable url
                    for url_data in video_data['published_urls']:
                        if url_data['format'] == 'mp4':

                            # TMP: Print for now
                            # urllib.request.urlretrieve(url_data['embed_url'], f"./videos/{video_data['def_title']}.mp4")
                            print(video_data['def_title'])
                            break
            except urllib.error.HTTPError as e:
                print("Could not retrieve video")
        print("---")


if __name__ == "__main__":
    get_videos(get_page_urls())
