import pdfplumber,requests,datetime,os
from io import BytesIO
from bs4 import BeautifulSoup
from deta import Deta
from onepush import notify
devmode=False
DATA_KEY="csic_menu1"
def dp(url):#傳入PDF解碼後的list
    prefix=['A', 'B', '晚']
    pdf=pdfplumber.open(BytesIO(requests.get(url).content)).pages[0].extract_table()
    c=-1
    temp=''
    data=list()
    for i in pdf:#處理原數據
        b=0
        for j in i:#處理每餐內容
            if b>2:break#截取數據至餐名
            if type(j)==str:
                if len(j)>0:
                    j=j.replace('炸物日','').replace('()','').replace('(補課)','').split('(')[0]
                    j=u"{0}".format(j)
                    if b!=2: j=j.replace('\n','')#替換換行字元以便format

                    if b==2:#只截取餐名，捨棄配菜名
                        j=j.split('\n')[0]
                        a=j.split(' ')
                        j=a[0]
                        if a[0]=="NEW": j+='-'+a[1]
                            
                    else:j=j.replace(' ','')

                    if j[0:1].isdigit():
                        a=j.split('星')
                        j=datetime.datetime.strptime(a[0],'%m/%d').strftime('%m/%d')+'星'+a[1]
                        data.append({'date':j,'data':{}})
                        c+=1

                    else:
                        if j[0] in prefix: temp=j[0]
                        elif temp in prefix:
                            data[c]['data'][temp]=j
                            temp=''
            b+=1
    return data

def update():
    a=requests.get('http://www2.csic.khc.edu.tw/store/index.asp')
    a.encoding = 'utf-8'
    a=BeautifulSoup(a.text,features="lxml").body.p.text.replace(' ','').replace('\n','').replace('\r','')
    return a

def dpd(j):
    a=''
    prefix={'A':'Ａ', 'B':'Ｂ', '晚':'晚'}
    for i in j:
        b=0
        for k in i['data'].keys():
            for l in prefix.keys():
                if k==l:
                    if b==0:
                        a=a+f'{i["date"]} {prefix[k]}餐 {i["data"][k]}\n'
                    else:
                        a=a+f'            {prefix[k]}餐 {i["data"][k]}\n'
            b+=1
    return a[:-1]

def message(content,webhook=None):
    notify('discord',
        webhook=webhook,
        title='菜單更新',
        content=f"```{content}```",
        username="蘿莉廚師")

def default():
    a=''
    manufacturers=['','向陽','正園','芳味香']
    for i in range(1,4):
        a+=manufacturers[i]+'\n'+dpd(dp(f'http://www2.csic.khc.edu.tw/store/data/{i}.pdf'))+'\n\n'
    return a[:-2]

def main():
    webhook=os.getenv('webhook')
    if webhook==None:
        print('webhook配置錯誤')
        return
    if devmode!=True:
        menutime=update()
        data=Deta().Base('simple_db')
        datatime=data.get(DATA_KEY)
        print(datatime)
        if datatime!=None:
            if datatime['date']==menutime: print('菜單未更新')
            else:
                text=default()
                print(f'菜單已更新\n\n{text}')
                message(text,webhook=webhook)
                print(data.put({"date":menutime,"key":DATA_KEY}))
        else:
            text=default()
            print(f'第一次執行\n\n{text}')
            message(text,webhook=webhook)
            print(data.put({"date":menutime,"key":DATA_KEY}))

    else:
        text=default()
        message(text,webhook=webhook)



if __name__ == '__main__':
    main()