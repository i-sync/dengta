#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
import requests
import json
import os
import time
import sys, getopt
m3u8_download = __import__("m3u8-download")
import subprocess

class Downloader():
    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "Authorization": "sdfkjhaskdfh12459384",
            "osType": "Android",
            "appVersion": "1.8.3",
            "appVersionCode": "10055",
            "deviceId": "30c92de0647a3199",
            "osVersion": "5.1.1",
            "channelId": "hw",
            "tourist": "0",
            "pushType": "xinge",
            "User-Agent": "okhttp/3.11.0"
        }


    def get_json_data(self, course_id, force):
        json_file_name = f"{os.path.dirname(os.path.abspath(__file__))}/json/{course_id}.json"
        if force and os.path.exists(json_file_name):
            os.remove(json_file_name)
        elif os.path.exists(json_file_name):
            with open(json_file_name, 'r', encoding='utf-8') as f:
                return json.load(f)

        base_url = f"http://wx-1.dengtacourse.com/dengta/app/getSectionListNewV2.json?courseId={course_id}"
        if course_id is None:
            return None
        res = requests.post(base_url, headers=self.headers)
        if res.status_code != requests.codes.ok:
            print(res.json())
            return res.json()

        res = res.json()
        with open(json_file_name, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(res, ensure_ascii=False))
            
        return res

    def download_file(self, url):
        headers = {
            "User-Agent":"Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.149 Mobile Safari/537.36 MMWEBID/6018 MicroMessenger/7.0.12.1601(0x27000C41) Process/tools NetType/WIFI Language/zh_CN ABI/arm64 GPVersion/1"
        }
        #base_url = "http://mediadengta.61info.cn/groupbuy/{}"
        if url is None:
            return url
            
        res = requests.get(url, headers=headers)
        if res.status_code != requests.codes.ok:
            return None
        return res.content
        
    def write_file(self, file_name, file_content):
        if os.path.exists(file_name):
            os.remove(file_name)
        with open(file_name, 'wb') as f:
            f.write(file_content)

    '''
    def get_json_data(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return json_data
    '''

def get_argv(argv):
    start = 0
    end = 0
    p = False
    force = False
    try:
        opts, args = getopt.getopt(argv,"hs:e:n:pf",["start=","end=","num=","print", "force"])
    except getopt.GetoptError:
      print('simple-download.py -s <start course id> -e <end course id> -n <single course id num> -p <only print>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('simple-download.py -s <start course id> -e <end course id> -n <single course id num> -p <only print>')
         sys.exit()
      elif opt in ("-s", "--start"):
         start = arg
      elif opt in ("-e", "--end"):
         end = arg
      elif opt in ("-n", "--num"):
         start = end = arg
      elif opt in ("-p", "--print"):
          p = True
      elif opt in ("-f", "--force"):
          force = True
    if start == 0 or end == 0:
        print('Error!, start course id or end course id incorrect')
        sys.exit()
    return int(start), int(end), p, force

if __name__ == "__main__":
    start, end, p, force = get_argv(sys.argv[1:])
    #print(start, end, type(start))
    base_path = "/media/Entertainment/dengta"
    downloader = Downloader()
    for course_id in range(start, end + 1):
        json_data = downloader.get_json_data(course_id, force)
        #check if success
        if not json_data["resultCode"]["success"]:
            continue
        seasonlist = json_data["value"]
        course_name = "{}.{}".format(course_id, seasonlist["courserName"])
        for data in seasonlist["sectionList"]:
            file_url = data["videoUrl"]

            if file_url.endswith('NULL'):
                print(f'{data["sectionId"]}.{data["title"]}, URL is: {file_url}')
                continue
            if "?" in file_url:
                file_ext = file_url[file_url.rindex("."): file_url.index("?")]
            else:
                file_ext = file_url[file_url.rindex("."):]
            file_path = "{}/{}".format(base_path, course_name)
            #check file_path, if not exists , create.
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            index = f"{data["sectionId"]:0>2}" if len(seasonlist["sectionList"]) < 100 else f"{data["sectionId"]:0>3}"
            file_name = f"{file_path}/{index}.{data["title"].replace('/', '-').strip()}{".mp4" if file_ext == ".m3u8" else file_ext}"
            print(file_name)
            if p:
                continue
            #check file_name, if exists continue.
            if os.path.exists(file_name):
                print(file_name, "exists, skip...")
                continue

            file_content = downloader.download_file(file_url)
            #check if download success
            if file_content is None:
                print(file_name, "download failed...")
            else:
                downloader.write_file(file_name, file_content)
            time.sleep(20)
            #break
        print(course_name, "....Done.")
        #break
    print("All Done.")