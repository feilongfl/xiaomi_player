from flask import Flask, redirect
from pathlib import Path
import fire

from MusicProviderLocalFile import MusicProviderLocalFile
from MusicProviderJellyfin import MusicProviderJellyfin


# 初始化Flask应用
app = Flask(__name__)


@app.route('/next')
def next_play():
    # 返回当前播放文件并跳转到下一个
    return redirect(f'/{app.music_manager.get_next_file()}')


@app.route('/random')
def random_play():
    # 随机播放
    return redirect(f'/{app.music_manager.get_random_file()}')


@app.route('/first')
def first_play():
    # 从头开始播放
    return redirect(f'/{app.music_manager.get_first_file()}')


@app.route('/s/<search_term>')
def search(search_term):
    # 根据搜索关键字进行播放
    app.music_manager.update_file_list(search_term)
    return redirect(f'/{app.music_manager.get_first_file()}')


@app.route('/')
def index():
    return next_play()


@app.route('/<path:filename>')
def play(filename):
    """
    播放指定路径的音频文件
    """
    return app.music_manager.play_audio(filename)


class XiaoMiPlayer:
    def __init__(self, host="0.0.0.0", port=65533):
        self.host = host
        self.port = port
        app.config["HOST"] = host
        app.config["PORT"] = port

    def local(self, path="test/music", ffmpeg="ffmpeg"):
        """
        启动本地音乐播放
        :param path: 音乐文件目录
        :param ffmpeg: ffmpeg路径，用于转码
        """
        music_manager = MusicProviderLocalFile(Path(path).absolute(), ffmpeg)
        app.music_manager = music_manager  # 将music_manager绑定到Flask应用
        app.run(host=self.host, port=self.port)

    def jellyfin(self, username, token, library, server="http://localhost:8096"):
        """
        启动Jellyfin音乐播放
        :param server: Jellyfin服务器地址
        :param token: Jellyfin的API token
        """
        music_manager = MusicProviderJellyfin(
            token=token,
            server=server,
            library=library,
            username=username
        )
        app.music_manager = music_manager  # 将music_manager绑定到Flask应用
        app.run(host=self.host, port=self.port)


if __name__ == '__main__':
    fire.Fire(XiaoMiPlayer)
