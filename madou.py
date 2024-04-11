import hashlib
import requests
import time
import execjs
import json
from urllib import parse
import base64
import os


def get_md5(uri: str):
    uri_str = "&".join(sorted(uri.split("&")))
    md5 = hashlib.md5((uri_str + "&m}q%ea6:LDcmS?aK)CeF287bPvd99@E,9Up^").encode()).hexdigest()
    return md5


def get_madou_video(page, channel):
    """
    获取视频信息
    :param page: 页码
    :param channel: 类型
    :return:
    """

    url = "https://api.nzp1ve.com/video/listcache"

    data = {
        "page": page,
        "channel": channel,
        "list_row": 100,
        "type": 2,
        "timestamp": round(time.time() * 1000)
    }

    return __Madou_post(url, data, False)


def get_madou_channel():
    """
    获取视频类型
    :return:
    """
    url = "https://api.nzp1ve.com/video/channel"

    data = {
        "timestamp": round(time.time() * 1000)
    }

    return __Madou_post(url, data, True)


def to_m3u8():
    """
    转m3u文件，tvbox可用
    :return:
    """
    res = get_madou_channel()
    json_data = json.loads(base64.b64decode(res).decode("utf-8"))
    m3u_path = os.path.join(os.path.abspath(""), "Adult.m3u")
    if os.path.exists(m3u_path):
        os.remove(m3u_path)
    with open(m3u_path, "a", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        i = 0
        for video_channel in json_data:
            i += 1
            total = video_channel["total"]
            image = video_channel["image"]
            name = video_channel["name"]
            num = int(total / 100) if total % 100 == 0 else int(total / 100) + 1 if total > 100 else 1
            for page in range(1, num + 1):
                print(f"正在获取{name}下的第{page},共有{num}页,总数{total},进度:{round(i/len(json_data)*100)}%")
                video_data = json.loads(
                    base64.b64decode(get_madou_video(page=page, channel=video_channel["id"])).decode("utf-8"))
                time.sleep(0.6)
                for video_info in video_data:
                    f.write(
                        f'#EXTINF:-1 tvg-logo="{image}" group-title="{name}",{video_info["title"]}\n{video_info["video_url"]}\n')


def __Madou_post(url: str, data: dict, s: bool):
    data["encode_sign"] = get_md5(parse.urlencode(data))
    with open("madou.js", "r", encoding="utf-8") as f:
        js = f.read()
        suffix = execjs.compile(js).call("get_suffix", 6)

        headers = {
            "Host": "api.nzp1ve.com",
            "Connection": "keep-alive",
            "Content-Length": "188",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "sec-ch-ua-mobile": "?0",
            "suffix": suffix,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://madou.tv",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        post_data = execjs.compile(js).call("post_encrypt", json.dumps(data, separators=(",", ":")), suffix)
        res = requests.post(url, data=json.dumps({"post-data": post_data}), headers=headers).json()
        # print(res)
        re = execjs.compile(js).call("post_decrypt", res["data"], res["suffix"], s)
        # if s:
        #     for i in json.loads(base64.b64decode(re).decode("utf-8")):
        #         print(i['name'], i['id'])
        # else:
        #     for i in json.loads(base64.b64decode(re).decode("utf-8")):
        #         print(i['title'], "vip资源" if i['vip'] == 1 else "普通", i['video_url'])
        return re


if __name__ == '__main__':
    to_m3u8()
