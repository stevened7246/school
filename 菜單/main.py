import requests
from bs4 import BeautifulSoup
import hashlib
import time
import os
import json
from onepush import notify
import sys


webhook1=os.getenv('webhook')

def hash_sha(url):
    a=requests.get(url)
    a.encoding='utf-8'
    a=hashlib.sha3_256(a.text.encode('utf-8')).hexdigest()

    c=url[-5]

    if   c=='1':b='向陽  '
    elif c=='2':b='正園  '
    elif c=='3':b='芳味香'

    log(b+':'+a)
    return a

def log(str='',logfile='./log.txt'):
    if str!='':print(str)
    
    logfile=open(logfile,'a',encoding='utf8')
    logfile.write(str+'\n')
    logfile.close()

def main():
    log()
    log(time.strftime("%Y{}%m{}%d{} %H{}%M{}%S{}").format("年","月","日","时","分","秒")+'\n')

    a=requests.get('http://www2.csic.khc.edu.tw/store/index.asp')
    a.encoding = 'utf-8'
    c=BeautifulSoup(a.text,features="lxml").body.p.text.replace(' ','').replace('\n','')
    log(c)
    print()

    data1=hash_sha('http://www2.csic.khc.edu.tw/store/data/1.pdf')
    data2=hash_sha('http://www2.csic.khc.edu.tw/store/data/2.pdf')
    data3=hash_sha('http://www2.csic.khc.edu.tw/store/data/3.pdf')
    
    data=dict()
    data['data']=c
    data['data1']=data1
    data['data2']=data2
    data['data3']=data3


    jsonfilestatus=False
    if os.path.isfile('data.json'):
        jsonfilesize=os.path.getsize('./data.json')
        print(jsonfilesize)
        if jsonfilesize>0:
            jsonfilestatus=True
            jsonfile=open('data.json','r',encoding='utf8')
            jsondata=json.loads(jsonfile.read())
            jsonfile.close()
            print(jsondata)
 


    if jsonfilestatus:
        if 'date'and'data1'and'data2'and'data3'in jsondata.keys():
            if data['data']==jsondata['data'] and data['data1']==jsondata['data1'] and data['data2']==jsondata['data2'] and data['data3']==jsondata['data3']:
                print('ok')
            else:
                print(1111111)
                notify('discord',
                webhook=webhook1,
                title='OnePush'+'菜單提醒',
                content='菜單數據異動，請檢查',
                username="菜單更新小幫手")
    


    jsonfile=open('data.json','w+',encoding='utf8')
    v=json.dumps(data)
    jsonfile.write(v)
    # jsondata=jsonfile.read()
    jsonfile.close()



if __name__ == '__main__':
    main()