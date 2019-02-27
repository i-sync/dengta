#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
import requests
import json
import os
import time


class Downloader():
    
    def download_file(self, url):
        headers = { 
            "Referer": "http://dengta-t-4.61info.cn/wx/groupBuy/sectionContent.html?courseId=25&sectionId=1&openId=oOcXl0a37tf8lNhqCnbHi16p6A0A&channel=54&prePageName=sectionList",
            "Accept-Encoding": "",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
            "Range":"bytes=0-"
        }
        base_url = "http://media6.61info.cn/groupbuy/{}"
        if url is None:
            return url
            
        res = requests.get(base_url.format(url), headers = headers)
        return res.content
        
    def write_file(self, file_name, file_content):
        if os.path.exists(file_name):
            os.remove(file_name)
        with open(file_name, 'wb') as f:
            f.write(file_content)

    def get_json_data(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return json_data


if __name__ == "__main__":
    base_path = "/mnt/files"
    downloader = Downloader()
    data_file = "content.json"
    json_data = downloader.get_json_data(data_file)
    for key in json_data:
        course_file = "json/{}.json".format(key)
        course_name = "{}.{}".format(key, json_data[key])
        print(course_file, course_name)
        course_data = downloader.get_json_data(course_file)
        for data in course_data:
            file_url = data["videoUrl"]
            if "?" in file_url:
                file_ext = file_url[file_url.index("."): file_url.index("?")]
            else:
                file_ext = file_url[file_url.index("."): -1]
            file_path = "{}/{}".format(base_path, course_name)
            #check file_path, if not exists , create.
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            file_name = "{}/{}{}".format(file_path, data["title"], file_ext) 
            print(file_name)
            #check file_name, if exists continue.
            if os.path.exists(file_name):
                print(file_name, "exists, skip...")
                continue
            #file_content = downloader.download_file(file_url)
            #downloader.write_file(file_name, file_content)
            #time.sleep(2)
            #break
        print(course_name, "....Done.")
        #break
    print("All Done.")