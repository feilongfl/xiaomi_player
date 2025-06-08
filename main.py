
from flask import Flask, send_file, redirect
from pathlib import Path
import fire

from MusicProviderLocalFile import MusicProviderLocalFile


# 配置参数
PORT = 65533
FILE_DIR = Path('test/music').absolute()  # 使用pathlib.Path
FFMPEG_PATH = 'ffmpeg'

# 初始化Flask应用
app = Flask(__name__)

# 初始化LocalFileMusic类
music_manager = MusicProviderLocalFile(FILE_DIR, FFMPEG_PATH)

@app.route('/next')
def next_play():
    # 返回当前播放文件并跳转到下一个
    return redirect(f'/{music_manager.get_next_file()}')

@app.route('/random')
def random_play():
    # 随机播放
    return redirect(f'/{music_manager.get_random_file()}')

@app.route('/first')
def first_play():
    # 从头开始播放
    return redirect(f'/{music_manager.get_first_file()}')

@app.route('/s/<search_term>')
def search(search_term):
    # 根据搜索关键字进行播放
    music_manager.update_file_list(search_term)
    return redirect(f'/{music_manager.get_first_file()}')

@app.route('/')
def index():
    return next_play()

@app.route('/<path:filename>')
def play(filename):
    """
    播放指定路径的音频文件
    """
    return music_manager.play_audio(filename)


def main():
    fire.Fire(lambda: app.run(host="0.0.0.0", port=PORT))


if __name__ == '__main__':
    main()
