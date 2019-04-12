#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
import requests
import os
import os.path
import shutil
import sys
from urllib.parse import urljoin

class m3u8_downloader:  
    '''
    m3u8_url: http://xxxxx/groupbuy/9e0b98dc1baf12444eb86051a7453aec/s.m3u8?v=20190322
    file_name: 第4节：才艺展示狂欢节
    dest_dir: /tmp/
    '''
    def __init__(self, m3u8_url, file_name, dest_dir):          
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        }
        self.m3u8_url = m3u8_url
        self.file_name = file_name
        self.dest_dir = dest_dir

        #init 
        self.get_m3u8_text()
        self.get_temp_dir()

        self.get_url_list()

    def get_m3u8_text(self):
        res = requests.get(self.m3u8_url, headers = self.headers)
        self.body = res.text

    def get_temp_dir(self):
        uid = self.m3u8_url.split('/')[-2]
        self.tmp_dir = os.path.join(self.dest_dir, uid)
        #check tmp dir if exists
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

    def get_url_list(self):
        lines = self.body.split('\n')
        self.ts_files = {}
        for line in lines:
            if not line.startswith('#') and line != '' and line.endswith('.ts'):
                if line.startswith('http'):
                    file_path = os.path.join(self.tmp_dir, line.split('/')[-1])
                    self.ts_files[file_path] = line
                else:
                    file_path = os.path.join(self.tmp_dir, line.split('/')[-1])
                    self.ts_files[file_path] = urljoin(self.m3u8_url, line)

    def merge_file(self):
        output_file_path = os.path.join(self.dest_dir, self.file_name) + ".mp4"
        #check file exists
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        #print("merge ts files ...")
        merge_flag = True
        with open(output_file_path, 'wb') as output:
            for file_path, _ in self.ts_files.items():
                #print(file_path)
                #check ts file exists
                if not os.path.exists(file_path):
                    merge_flag = False
                    print("merge file failed, lost the ts file:", file_path)
                    break
                with open(file_path, 'rb') as f:
                    output.write(f.read())
        
        #check if merge success
        #if success , clear tmp folder.  if failed , remove the output file
        if merge_flag:
            shutil.rmtree(self.tmp_dir)
        else:
            os.remove(output_file_path)

    def download(self):
        print(self.m3u8_url, "downloading...")
        total_num = len(self.ts_files)
        for index, (file_path, file_url)  in enumerate(self.ts_files.items()):
            #download percent start
            sys.stdout.write('\r[{0:50}] {1}/{2}'.format('='*(index * 50 // total_num), index, total_num))
            sys.stdout.flush()
            #download percent end
            
            if file_url is None:
                continue
            #check ts file if exists
            if os.path.exists(file_path):
                print(file_path, "exists...")
                continue
            res = requests.get(file_url, headers = self.headers)
            if res.status_code != requests.codes.ok:
                print(file_url, "download failed!")
                continue
            with open(file_path, 'wb') as f:
                f.write(res.content)
        #stop download precet
        print()
        #merge ts files
        self.merge_file()
        
if __name__ == "__main__":
    args = sys.argv
    if len(args) > 3:
        downloader = m3u8_downloader(args[1], args[2], args[3])
        downloader.download()
    else:
        print('Fail, params error, try:')
        print('python', args[0], 'your_m3u8_url', 'you_file_name','your_local_dir\n')