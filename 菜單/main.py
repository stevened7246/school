import requests
from bs4 import BeautifulSoup
import hashlib
import time
import os
import json
from onepush import notify



def hash_sha(url):#哈希與分辨函數
    a=requests.get(url)
    a.encoding='utf-8'
    a=hashlib.sha3_256(a.text.encode('utf-8')).hexdigest()

    c=url[-5]

    if   c=='1':b='向陽  '
    elif c=='2':b='正園  '
    elif c=='3':b='芳味香'

    log(b+':'+a)
    return a

def log(str1='',logfile='./log.txt'):
    if str1!='':print(str1)
    
    logfile=open(logfile,'a',encoding='utf8')
    logfile.write(str1+'\n')
    logfile.close()

def getdata():
    a=requests.get('http://www2.csic.khc.edu.tw/store/index.asp')
    a.encoding = 'utf-8'
    c=BeautifulSoup(a.text,features="lxml").body.p.text.replace(' ','').replace('\n','').replace('\r','')
    log(c)
    print()
    log('實時數據')
    data1=hash_sha('http://www2.csic.khc.edu.tw/store/data/1.pdf')
    data2=hash_sha('http://www2.csic.khc.edu.tw/store/data/2.pdf')
    data3=hash_sha('http://www2.csic.khc.edu.tw/store/data/3.pdf')
    
    data=dict()
    data['data']=c
    data['data1']=data1
    data['data2']=data2
    data['data3']=data3
    return data

def main():
    try:
        webhook1=os.getenv('webhook')
    except:
        log('環境變量有問題，請檢查')
        exit()
    log()
    log(time.strftime("%Y{}%m{}%d{} %H{}%M{}%S{}").format("年","月","日","时","分","秒")+'\n')

    data=getdata()

    jsonfilestatus=False
    if os.path.isfile('data.json'):
        jsonfilesize=os.path.getsize('./data.json')
        print("json大小："+str(jsonfilesize))

        if jsonfilesize>0:#json內部有數據
            jsonfilestatus=True
            jsonfile=open('data.json','r',encoding='utf8')
            jsondata=json.loads(jsonfile.read())
            jsonfile.close()

            print()
            print(jsondata)
 


    if jsonfilestatus:
        if 'date'and'data1'and'data2'and'data3'in jsondata.keys():
            if data['data']==jsondata['data'] and data['data1']==jsondata['data1'] and data['data2']==jsondata['data2'] and data['data3']==jsondata['data3']:
                print('菜單數據無變化')
            else:
                print('菜單數據異動')
                notify('discord',
                webhook=webhook1,
                title='菜單提醒',
                content='菜單已更新',
                username="沙雕bot")
    else:
        print('第一次運行')
    


    jsonfile=open('data.json','w+',encoding='utf8')
    v=json.dumps(data)
    jsonfile.write(v)
    # jsondata=jsonfile.read()
    jsonfile.close()



if __name__ == '__main__':
    main()