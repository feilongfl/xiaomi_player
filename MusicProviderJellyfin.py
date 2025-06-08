import random
from flask import Flask, send_file, redirect

import urllib.parse
import requests
import random


class JellyfinPlayer:
    def __init__(
        self,
        token: str,
        server: str = "http://feilong-home.lan:8096",
        library: str = "Playlists/Work",
        username: str = "feilong"
    ):
        self.server = server.rstrip("/")
        self.token = token
        self.username = username
        self.headers = {
            "X-Emby-Token": token,
            "Accept": "application/json"
        }
        self.user_id = self._get_user_id()
        self.playlist_id = self._get_playlist_id(library.split("/")[-1])
        self.tracks = self._get_playlist_items()

    def _get_user_id(self):
        r = requests.get(f"{self.server}/Users", headers=self.headers)
        r.raise_for_status()
        for u in r.json():
            if u["Name"] == self.username:
                return u["Id"]
        raise RuntimeError("User not found")

    def _get_playlist_id(self, name):
        r = requests.get(
            f"{self.server}/Users/{self.user_id}/Items?IncludeItemTypes=Playlist&Recursive=true",
            headers=self.headers
        )
        r.raise_for_status()
        for item in r.json().get("Items", []):
            if item["Name"].lower() == name.lower():
                return item["Id"]
        raise RuntimeError("Playlist not found")

    def _get_playlist_items(self):
        r = requests.get(
            f"{self.server}/Playlists/{self.playlist_id}/Items",
            headers=self.headers,
            params={"UserId": self.user_id, "Fields": "Name"}
        )
        r.raise_for_status()
        return r.json().get("Items", [])

    def _get_download_url(self, item_id):
        query = urllib.parse.urlencode({"api_key": self.token, "Static": "true"})
        return f"{self.server}/Items/{item_id}/Download?{query}"

    def list_tracks(self):
        return [t["Name"] for t in self.tracks]

    def _get_transcoded_url(self, item_id):
        query = {
            "UserId": self.user_id,
            "api_key": self.token,
            "DeviceId": "web-feilong",
            "AudioCodec": "mp3",        # 转码为 MP3
            "Container": "mp3",         # 使用 MP3 封装
            "MaxStreamingBitrate": "192000",  # 可选：控制码率
            "Static": "true"            # 返回完整流，适合直接播放或下载
        }
        return f"{self.server}/Audio/{item_id}/universal?" + urllib.parse.urlencode(query)

    def playurl(self, index: int | str):
        index = int(index)
        if index < 0:
            index = random.randint(0, len(self.tracks) - 1)
        track = self.tracks[index]
        url = self._get_transcoded_url(track["Id"])
        print(f"► 播放转码后的音频: {track['Name']}")
        return url


# 示例用法
if __name__ == "__main__":
    player = JellyfinPlayer(
        token="b80a98a8116342e8b75d272761259591",
        server="http://feilong-home.lan:8096",
        library="Playlists/Work"
    )

    print("曲目列表：")
    for i, name in enumerate(player.list_tracks(), 1):
        print(f"{i:02d}. {name}")

    # 播放第一个
    url = player.playurl(0)
    print(url)


class MusicProviderJellyfin(JellyfinPlayer):
    def __init__(
        self,
        token: str,
        server: str = "http://feilong-home.lan:8096",
        library: str = "Playlists/Work",
        username: str = "feilong"
    ):
        super().__init__(
            token=token,
            server=server,
            library=library,
            username=username
        )
        self.index = 0
        self.count = len(self.tracks)

    def play_audio(self, item_id):
       print(f"item={item_id}")
       print(f"self.playurl[item_id]={self.playurl(item_id)}")
       return redirect(self.playurl(item_id))

    def get_next_file(self):
        if self.index < 0:
            return self.index
        self.index = 0 if self.index+1 >= self.count else self.index+1
        return (self.index)

    def get_random_file(self):
        self.index = -1
        return (self.index)

    def get_first_file(self):
        self.index = 0
        return (self.index)
