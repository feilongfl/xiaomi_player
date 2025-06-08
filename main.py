import os
import random
import shutil
import subprocess
from flask import Flask, send_file, redirect
import fire


# 配置参数
PORT = 65533
FILE_DIR = 'test/music'
FFMPEG_PATH = 'ffmpeg'


class LocalFileMusic:
    def __init__(self, file_dir, ffmpeg_path=None):
        """
        初始化音乐文件管理器
        :param file_dir: 音乐文件夹路径
        :param ffmpeg_path: ffmpeg路径，用于转码
        """
        self.file_dir = file_dir
        self.ffmpeg_path = ffmpeg_path
        self.file_list = []
        self.file_index = 0
        self.update_file_list()

    def update_file_list(self, search=''):
        """
        更新音乐文件列表，支持搜索功能
        """
        try:
            os.chdir(self.file_dir)
        except Exception as e:
            print(e)
            print('ERROR: 请检查目录是否存在或是否有权限访问')
            exit()
        
        self.file_list = [
            os.path.join(path, f)[2:]
            for path, _, files in os.walk('.')
            for f in files if f.lower().split('.')[-1] in ['flac', 'mp3', 'wav', 'aac', 'm4a']
            if not search or search in os.path.join(path, f)[2:]
        ]
        
        self.file_list.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        print(f'{len(self.file_list)} files found')

    def play_audio(self, filename):
        """
        播放音频文件，如果是需要转码的格式，则使用ffmpeg转码为wav格式。
        """
        path = os.path.join(self.file_dir, filename)
        if os.path.isfile(path):
            if self.ffmpeg_path and path.lower().split('.')[-1] not in ['wav', 'mp3']:
                # 转码操作
                command = f'{self.ffmpeg_path} -i "{path}" 2>&1 | grep Duration'
                duration = subprocess.getoutput(command).split()[1][:-1].split(':')
                duration_in_seconds = float(duration[0]) * 3600 + float(duration[1]) * 60 + float(duration[2])
                # 计算音频大小
                content_length = int(duration_in_seconds * 176400)
                return send_file(
                    subprocess.Popen([self.ffmpeg_path, '-i', path, '-f', 'wav', '-'], stdout=subprocess.PIPE),
                    mimetype='audio/wav',
                    as_attachment=True,
                    attachment_filename=path.split('/')[-1],
                    add_etags=False,
                    content_length=content_length
                )
            else:
                # 直接播放
                return send_file(path, mimetype='audio/mpeg')
        else:
            return "404 Not Found", 404

    def get_next_file(self):
        """
        获取下一个文件的路径，循环播放
        """
        self.file_index += 1
        if self.file_index >= len(self.file_list):
            self.file_index = 0
        return self.file_list[self.file_index]

    def get_random_file(self):
        """
        随机播放文件
        """
        random.shuffle(self.file_list)
        return self.file_list[0]

    def get_first_file(self):
        """
        从头开始播放
        """
        return self.file_list[0]


# 初始化Flask应用
app = Flask(__name__)

# 初始化LocalFileMusic类
music_manager = LocalFileMusic(FILE_DIR, FFMPEG_PATH)


@app.route('/')
def index():
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
