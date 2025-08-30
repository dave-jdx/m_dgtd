from bs4 import BeautifulSoup
import time,re,urllib.request

def scanpage(urls:list,links:list,n:int,base:str):
    n=n-1
    if(n<0):
        return links
    else:
        for url in urls:
            linksCurrent=[]
            try:
                html=urllib.request.urlopen(url).read()
                soup=BeautifulSoup(html,'html.parser')
                linksCurrent=soup.find_all("a")
            

                for linkT in soup.find_all("a"):
                    curl=str(linkT.get('href'))
                    if(curl!=None):
                        links.append(base+curl)
                        linksCurrent.append(base+curl)
            except Exception as e:
                print("error",url)
        return scanpage(linksCurrent,links,n,base)

urls=["http://attc.com.cn/"]
links=[]
timeStart=time.time()
scanpage(urls,links,3,"http://attc.com.cn")
timeEnd=time.time()
uObj={}
iIndex=0
for url in links:
    if uObj.get(url)==None:
        uObj[url]=1
        iIndex=iIndex+1
        print("found",iIndex,url)

    




print(len(links),iIndex,"耗时: {:.2f}秒".format(timeEnd - timeStart))