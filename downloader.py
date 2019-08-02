import urllib
from bs4 import BeautifulSoup
import re
import json
import os

import utils

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


def get_content(urls, output_path, is_get_video=True, is_get_audio=True, is_get_captions=True):
    """Download videos"""
    
    output_paths = []
    
    for url in urls:
        ids = []
        resp = urllib.request.urlopen(url)
        soup = BeautifulSoup(resp, "lxml")
        
        page_title = soup.title.get_text()
        print(page_title)

        file_prefix = url.split('/')[-2]
        target_dir = os.path.join(output_path, file_prefix)
        output_paths.append(target_dir)
        try:
            os.mkdir(target_dir)
        except FileExistsError:
            pass
        
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

        # Get video data
        for video_id in ids:
            try:
                with urllib.request.urlopen(f"https://tkx2-prod.anvato.net/rest/v2/mcp/video/{video_id}?anvack=DVzl9QRzox3ZZsP9bNu5Li3X7obQOnqP") as video_data_resp:
                    video_data = json.loads(video_data_resp.read()[22:-1].decode('utf-8'))
                    print(video_data['def_title'])

                    # Download video
                    if is_get_video:
                        for url_data in video_data['published_urls']:
                            if url_data['format'] == 'mp4':
                                urllib.request.urlretrieve(url_data['embed_url'], os.path.join(target_dir, f"{utils.removeDisallowedFilenameChars(video_data['def_title'])}.mp4"))
                                break

                    # Download audio
                    if is_get_audio:
                        for url_data in video_data['published_urls']:
                            if url_data['format'] == 'mp3':
                                urllib.request.urlretrieve(url_data['embed_url'], os.path.join(target_dir, f"{utils.removeDisallowedFilenameChars(video_data['def_title'])}.mp3"))
                                break
                    
                    # Download captions
                    if is_get_captions:
                        base_url = 'https://cbslocal-uploads.storage.googleapis.com/anv-captionupl/'
                        caption_url_matcher = re.compile(r'[0-9A-F]+/[0-9A-F]+/[0-9A-F]+\.vtt')
                        
                        for caption_data in video_data['captions']:
                            caption_url = caption_url_matcher.findall(caption_data['url'])
                            if caption_url:
                                urllib.request.urlretrieve(
                                    os.path.join(base_url, caption_url[0]),
                                    os.path.join(target_dir, f"{utils.removeDisallowedFilenameChars(video_data['def_title'])}.vtt")
                                )
                    
            except urllib.error.HTTPError as e:
                print("Could not retrieve video")
        print("---")

    return output_paths
