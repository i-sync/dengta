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
    def get_json_data(self, course_id):
        headers = { 
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
            "Cookie": "groupBuy_openId_new=oOcXl0a37tf8lNhqCnbHi16p6A0A; openId=oOcXl0a37tf8lNhqCnbHi16p6A0A; Hm_lvt_aca440f4172ea5b39ae32a3daeac7fba=1551065588,1551087508; groupBuy_posterOpenId_new=natureSubPoster; Hm_lpvt_aca440f4172ea5b39ae32a3daeac7fba=1551110811; JSESSIONID=53ABDA93D608A055DE0B9B19E5FE92E0"
        }
        base_url = "http://dengta-t-6.61info.cn/wx/groupBuy/getSectionList.json?courseId={}"
        if course_id is None:
            return None
        res = requests.get(base_url.format(course_id), headers = headers)
        return res.json()

    def download_file(self, url):
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        }
        base_url = "http://media6.61info.cn/groupbuy/{}"
        if url is None:
            return url
            
        res = requests.get(base_url.format(url), headers = headers)
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
    try:
        opts, args = getopt.getopt(argv,"hs:e:n:",["start=","end=","num="])
    except getopt.GetoptError:
      print('simple-download.py -s <start course id> -e <end course id> -n <single course id num>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('simple-download.py -s <start course id> -e <end course id> -n <single course id num>')
         sys.exit()
      elif opt in ("-s", "--start"):
         start = arg
      elif opt in ("-e", "--end"):
         end = arg
      elif opt in ("-n", "--num"):
         start = end = arg
    if start == 0 or end == 0:
        print('Error!, start course id or end course id incorrect')
        sys.exit()
    return int(start), int(end)

if __name__ == "__main__":
    start, end = get_argv(sys.argv[1:])
    #print(start, end, type(start))
    base_path = "/mnt/files"
    downloader = Downloader()
    for course_id in range(start, end + 1):
        json_data = downloader.get_json_data(course_id)
        #check if success
        if not json_data["resultCode"]["success"]:
            continue
        seasonlist = json_data["value"]["allSeasonSectionList"][0]
        course_name = "{}.{}".format(course_id, seasonlist["courseInfo"]["courseName"])
        for data in seasonlist["sectionList"]:
            file_url = data["videoUrl"]
            if "?" in file_url:
                file_ext = file_url[file_url.index("."): file_url.index("?")]
            else:
                file_ext = file_url[file_url.index("."):]
            file_path = "{}/{}".format(base_path, course_name)
            #check file_path, if not exists , create.
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file_name = "{}/{}{}".format(file_path, data["title"], ".mp4" if file_ext == ".m3u8" else file_ext) 
            print(file_name)
            #check file_name, if exists continue.
            if os.path.exists(file_name):
                print(file_name, "exists, skip...")
                continue

            #check file_ext if equal m3u8
            if file_ext == ".m3u8":
                #m3u8_download.m3u8_downloader(data["userVideoUrl"], data["title"], file_path).download()
                #command = "ffmpeg -i '{}' {}{}.mp4".format(data["userVideoUrl"], file_path, data["title"])
                subprocess.call(['ffmpeg', '-i', data["userVideoUrl"], '-vcodec', 'copy', '-acodec', 'copy', '{}/{}.mp4'.format(file_path, data["title"])])
                time.sleep(20)
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