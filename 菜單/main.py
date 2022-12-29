import requests
from bs4 import BeautifulSoup
import time
import os
from onepush import notify
import pdfplumber
from io import BytesIO

devmode=0

def pdfget(url):#pdf获取與解析
    data=requests.get(url)
    data.encoding='utf-8'
    
    d=pdfplumber.open(BytesIO(data.content)).pages[0].extract_table()
    a=0
    for i in d:
        a1=0
        for i1 in i:
            if type(i1)==str:
                d[a][a1]=i1.replace('\n','')
            a1+=1
        a+=1 

    return d

def getdata():
    a=requests.get('http://www2.csic.khc.edu.tw/store/index.asp')
    a.encoding = 'utf-8'
    c=BeautifulSoup(a.text,features="lxml").body.p.text.replace(' ','').replace('\n','').replace('\r','')
    
    data1=pdfget('http://www2.csic.khc.edu.tw/store/data/1.pdf')
    data2=pdfget('http://www2.csic.khc.edu.tw/store/data/2.pdf')
    data3=pdfget('http://www2.csic.khc.edu.tw/store/data/3.pdf')
    
    data=dict()
    data['data']=c
    data['data1']=data1
    data['data2']=data2
    data['data3']=data3
    return data

def log(str1='',logfile='./log.txt'):
    if str1!='':print(str1)
    else:print()
    
    logfile=open(logfile,'a',encoding='utf8')
    logfile.write(str1+'\n')
    logfile.close()

def main():
    log(time.strftime("%Y{}%m{}%d{} %H{}%M{}%S{}").format("年","月","日","时","分","秒")+'\n')
    
    webhook1=os.getenv('webhook')
    if webhook1==None:
        log('環境變量有問題，請檢查')
        exit()
    
    log('實時數據')

    data=getdata()
    #分解列表
    out=''
    for i in data:
        
        if i=='data1':
            out+='向陽'
        if i=='data2':
            out+='正園\n'
        if i=='data3':
            out+='芳味香\n'
        datas=data[i]
        #標題處理
        if i=='data':
            print(data[i]+'\n')
            continue
        #芳味香標題處理
        if i=='data3':
            del datas[0]
        
        del datas[0]#統一處理標題
        
        for i1 in  datas:#處理每餐資料
            
            temp=''
            del i1[3:]
            a=0

            for i2 in i1:
                
                if type(i2)==str:
                    if a==0:
                        i2=str(i2).replace(' ','').replace('炸物日','').replace('()','').replace('A','Ａ').replace('B','Ｂ')+' '
                    if a==1:
                        i2=str(i2).replace(' ','').replace('55元','')+' '
                    if a==2:
                        i2=i2.split(' ', 1)[0].replace('*','x')
                    temp+=i2

                if i2==None:
                    temp+='            '
                
                a+=1

            out=out+temp+'\n'
            # print(temp)
        out+='\n'

    print(out)

    if len(data['data'])==26:
        datatime=str(eval(data['data'][5:8])+1911)+data['data'][8:15]
    else:
        datatime=str(eval(data['data'][5:8])+1911)+'年0'+data['data'][9:14].replace('～','')
    print(datatime)
    if (time.strptime(datatime,'%Y年%m月%d日')<time.localtime()) and devmode==0:
        log('菜單數據無變化')
    else:
        log('菜單數據異動')
        notify('discord',
        webhook=webhook1,
        title='菜單更新',
        content=f"```{out}```",
        username="ben don bot")
    





if __name__ == '__main__':
    main()