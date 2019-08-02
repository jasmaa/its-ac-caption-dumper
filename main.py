import downloader
import parsing
import os

if __name__ == '__main__':
    try:
        os.mkdir('data')
    except FileExistsError:
        pass

    print("Downloading...")
    output_paths = downloader.get_content(
        downloader.get_page_urls(),
        'data',
        is_get_video=False, is_get_audio=False, is_get_captions=True
    )
    
    for path in output_paths:
        content = parsing.parse_captions(path)
        with open(os.path.join(path, "transcription.txt"), "w") as f:
            f.write(content)
            print(f"Transcribed {path}")
