#-*- coding:utf-8 -*-

import urllib.request
import urllib.parse
import os
import re
import time
import random
import json
import shutil


class helper:
    def __init__(self, pwd):
        print("Starting Collector")
        self.pwd = pwd
        self.list = os.listdir(self.pwd)
        self.questions = [[],[],[]]
        self.fix_list = []

        if 'README.md' in self.list:
            self.list.remove('README.md')

        if '.DS_Store' in self.list:
            self.list.remove('.DS_Store')

        for i in range(0, len(self.list)):
            self.list[i] = self.pwd + '/' + self.list[i]
            self.questions[i] +=  os.listdir(self.list[i])

            if '.DS_Store' in self.questions[i]:
                self.questions[i].remove('.DS_Store')

            for j in range(0, len(self.questions[i])):
                self.questions[i][j] = { 'dir' : self.list[i] + '/' + self.questions[i][j] }
        print("Parsing Directory Done")
        
    def get_rank(self):
        print("Get Rank")

        for i in range(0, len(self.list)):
            for j in range(0, len(self.questions[i])):
                data = open(str(self.questions[i][j]['dir']) + '/README.md', 'rt', encoding='UTF8')
                data = data.read()

                tier_info = re.findall('(\S[가-힣]{1,3} [0-9])', str(data))
                url = re.findall('https:\/\/www.acmicpc.net\/problem\/([0-9]{0,5})', str(data))
                
                if len(tier_info) == 0:
                    return

                if len(url) == 0:
                    return

                tier_info = tier_info[0]
                url = url[0]

                self.questions[i][j] = { 'dir' : self.questions[i][j]['dir'], 'tier' : tier_info, 'url' : url }
        print("Get Rank info Done")

    def diff_checker(self, current_tier, org_tier):
        calc_list = {'브론즈' : 0, '실버' : 5, '골드' : 10, '플레티넘' : 15, '다이아' : 20}
        calc_num_list = [5,4,3,2,1]

        org_tier = org_tier.split()
        calc_tier = calc_list[org_tier[0]] + calc_num_list[int(org_tier[1])-1]

        if current_tier == calc_tier:
            return True
        else:
            return False
    
    def search_rank(self):
        print("Search Rank")

        for i in range(1, 2):
            for j in range(0, len(self.questions[i])):
                time.sleep(random.uniform(1,2))
                url = urllib.request.Request("https://api.solved.ac/v2/problems/show.json?id="+str(self.questions[i][j]['url']))
                url.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko")
                data = urllib.request.urlopen(url)
                data = data.read()
                data = json.loads(data.decode('utf-8'))

                result = helper.diff_checker(self, data['result']['problems'][0]['level'], self.questions[i][j]['tier'])
                
                if result == False:
                    self.fix_list.append({
                        'dir' : self.questions[i][j]['dir'],
                        'org' : self.questions[i][j]['tier'],
                        'current' : data['result']['problems'][0]['level']
                    })
        print("Search Rank Done")

    def tier_converter(self):
        calc_list = {'0' : '브론즈', '1' : '실버', '2' : '골드', '3' : '플레티넘', '4' : '다이아'}
        calc_num_list = [5,4,3,2,1]
        
        for i in range(0, len(self.fix_list)):
            # 0.1은 5/5 같은 경우의 계산을 예외처리 해주기 위해 임의로 뺌
            tier = int(self.fix_list[i]['current'] / 5 - 0.1)
            level = self.fix_list[i]['current'] % 5
            self.fix_list[i]['current'] = calc_list[str(tier)] + ' ' + str(calc_num_list[level-1])
        
        print("Converting Done")

    def rank_fixer(self):
        print("Rank Fixer Start")
        helper.tier_converter(self)

        calc_list = {'브론즈' : 'bronze', '실버' : 'silver', '골드' : 'gold', '플레티넘' : 'platinum', '다이아' : 'diamond'}
        for i in range(0, len(self.fix_list)):
            print("Move [",self.fix_list[i]['dir'],"],[", self.fix_list[i]['org'], "] to [", self.fix_list[i]['current'], "]")
            move_dir = calc_list[(self.fix_list[i][ 'current'].split())[0]]

            # 티어 수정
            f = open(str(self.fix_list[i]['dir']) + '/README.md', 'rt', encoding='UTF8')
            data = f.read()
            data = re.sub(pattern=self.fix_list[i]['org'], repl=self.fix_list[i]['current'], count=1, string=data)
            f = open(str(self.fix_list[i]['dir']) + '/README.md', 'w')
            f.write(data)
            f.close()

            for i in range(0, len(self.list)):
                if move_dir in self.list[i] and (self.fix_list[i]['org'].split())[0] != (self.fix_list[i]['current'].split())[0]:
                    shutil.move(self.fix_list[i]['dir'], self.list[i])
        print("Rank Fixer DONE!")


def main():
    pwd = input("INPUT LOACTION OF FOLDER : ")
    gogo = helper(pwd)
    gogo.get_rank()
    gogo.search_rank()
    gogo.rank_fixer()

if __name__ == "__main__":
    main()