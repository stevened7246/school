import requests
import hashlib
import time
import os
import json
from onepush import notify



def hash_sha(url,header):#哈希與分辨函數
    a=requests.get(url,headers=header)
    a.encoding='utf-8'
    a=hashlib.sha3_256(a.text.encode('utf-8')).hexdigest()

    c=url[-6]

    if   c=='n':b='獎懲'
    elif c=='c':b='缺曠'

    log(b+':'+a)
    return a

def log(str1='',logfile='./log.txt'):
    if str1!='':print(str1)
    else:print()
    
    logfile=open(logfile,'a',encoding='utf8')
    logfile.write(str1+'\n')
    logfile.close()

def getdata(username,password):
    a=requests.get('https://www.csic.khc.edu.tw/abc/sb/LOGIN.ASP')

    headers1 = dict()
    print(a.headers['Set-Cookie'].split(';')[0])
    headers1["cookie"]=a.headers['Set-Cookie'].split(';')[0]

    
    params={'txtSnum':username,'txtPassword':password,'tctChk':'Y'}

    a=requests.post('https://www.csic.khc.edu.tw/abc/sb/login_chk.ASP',params=params,headers=headers1)
    print(a.headers.keys())
    headers1['referer']='https://www.csic.khc.edu.tw/abc/sb/LOGIN.ASP'
    a.encoding='utf-8'

    print(a)
    return a.text.replace('http://www.csic.khc.edu.tw/into/student/photoup/ssn/S125815656.JPG','https://www.csic.khc.edu.tw/into/student/photoup/ssn/S125815656.JPG').replace('<meta http-equiv="refresh" content="5;url=index.html">','').replace('<!--','//<!--')

def main():
    
    log(time.strftime("%Y{}%m{}%d{} %H{}%M{}%S{}").format("年","月","日","时","分","秒")+'\n')
    
    try:
        webhook1=os.getenv('webhook')
        username=os.getenv('username')
        password=os.getenv('password')
    except:
        log('環境變量有問題，請檢查')
        exit()
    
    log('實時數據')

    data=getdata(username,password)

    jsonfilestatus=False
    if os.path.isfile('index.html'):
        jsonfilesize=os.path.getsize('./index.html')
        log("json大小："+str(jsonfilesize))

        jsonfilesize=0

        if jsonfilesize>0:#json內部有數據
            jsonfilestatus=True
            jsonfile=open('index.html','r',encoding='utf8')
            jsondata=json.loads(jsonfile.read())
            jsonfile.close()

            log()
            log('上次數據')
            log(str(jsondata).replace(' ','').replace(',',',\n').replace('{','').replace('}','').replace(',','').replace("'",'').replace('data:','').replace('data1','缺曠').replace('data2','獎懲'))
 


    if jsonfilestatus:
        if 'data1'and'data2' in jsondata.keys():
            if data['data1']==jsondata['data1'] and data['data2']==jsondata['data2']:
                log('缺曠獎懲無變化')
            else:
                log('缺曠獎懲數據異動')
                notify('discord',
                webhook=webhook1,
                title='缺曠獎懲提醒',
                content='缺曠獎懲已更新',
                username="sb bot")
    else:
        log('第一次運行')
    


    jsonfile=open('index.html','w+',encoding='utf8')
    # v=json.dumps(data)
    jsonfile.write(data)
    # jsondata=jsonfile.read()
    jsonfile.close()



if __name__ == '__main__':
    main()