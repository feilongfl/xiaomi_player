import random
import shutil
import subprocess
from pathlib import Path
from flask import Flask, send_file, redirect

class MusicProviderLocalFile:
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
        if not self.file_dir.exists() or not self.file_dir.is_dir():
            print(f"ERROR: 请检查目录 {self.file_dir} 是否存在或是否有权限访问")
            exit()

        self.file_list = [
            str(f.relative_to(self.file_dir))
            for f in self.file_dir.rglob('*')
            if f.suffix.lower() in ['.flac', '.mp3', '.wav', '.aac', '.m4a']
            and (not search or search in str(f))
        ]
        
        self.file_list.sort(key=lambda x: Path(self.file_dir, x).stat().st_mtime, reverse=True)
        print(f'{len(self.file_list)} files found')

    def play_audio(self, filename):
        """
        播放音频文件，如果是需要转码的格式，则使用ffmpeg转码为wav格式。
        """
        path = self.file_dir / filename
        if path.is_file():
            if self.ffmpeg_path and path.suffix.lower() not in ['.wav', '.mp3']:
                # 转码操作
                command = f'{self.ffmpeg_path} -i "{path}" 2>&1 | grep Duration'
                duration = subprocess.getoutput(command).split()[1][:-1].split(':')
                duration_in_seconds = float(duration[0]) * 3600 + float(duration[1]) * 60 + float(duration[2])
                # 计算音频大小
                content_length = int(duration_in_seconds * 176400)
                return send_file(
                    subprocess.Popen([self.ffmpeg_path, '-i', str(path), '-f', 'wav', '-'], stdout=subprocess.PIPE),
                    mimetype='audio/wav',
                    as_attachment=True,
                    attachment_filename=path.name,
                    add_etags=False,
                    content_length=content_length
                )
            else:
                # 直接播放
                return send_file(path, mimetype='audio/mpeg')
        else:
            return f"404 Not Found: {path}", 404

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

