from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from bs4 import BeautifulSoup as soup
import requests
import urllib3
from threading import Thread

app = FastAPI()
messages = ["You are a good Boy","You are a Gay","You are a Bisexual","You are a good Girl","You are a person with one of the gender from LGBTQ+"]

origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    # "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

urllib3.disable_warnings()
data = []
ndata = []
async def multiThread(url,x): 
    pageSoup = await soup(requests.post(url, {"mbstatus" : "SEARCH", "htno" : x}, verify = False, allow_redirects = True).text, "html.parser")
    try:
        if(pageSoup.findAll("h1")[0].text == "HTTP Status 500 – Internal Server Error"):
            ndata.append(x)
            return False
        if pageSoup.find("div", {"id":"main-message"}).findAll("span")[0].text == "Your connection was interrupted":
            ndata.append(x)
            return False
    except:
        pass
    try:
        check = pageSoup.find("table",{"id":"AutoNumber1"})
        if check == None:
            ndata.append(x)
            return False
        
        if check.findAll("b")[1].text == "Personal Details":
            container2 = pageSoup.find("table",{"id":"AutoNumber4"})
            Results1 = []
            for i in container2.findAll("tr")[2:]:
                Marks1 = []
                temp = i.findAll("td")
                Marks1.append(temp[0].text.strip())
                Marks1.append(temp[1].text.strip())
                Marks1.append(temp[2].text.strip())
                Marks1.append(temp[3].text.strip())
                Marks1.append(temp[4].text.strip())
                Results1.append(Marks1)
            container3 = pageSoup.find("table",{"id":"AutoNumber5"})
            Results2 = []
            for i in container3.findAll("tr")[2:]:
                Marks2 = []
                Deat = i.findAll("td")
                Marks2.append(Deat[0].text.strip())
                Marks2.append(Deat[1].text.strip())
                Marks2.append(Deat[2].text.strip())
                Results2.append(Marks2)
            for roti in sorted(Results1):
                temp={}
                temp["Roll Number"] = str(x)
                if len(Results2[0])==3:
                    temp["CGPA"] = Results2[0][2]
                temp["Sub Code"] = roti[0]
                temp["Subject Name"] = roti[1]
                temp["Credits"] = roti[2]
                temp["Grade Points"] = roti[3]
                temp["Grade Secured"] = roti[4]
                for roties in sorted(Results2):
                    if roti[0][0] == roties[0] :
                        temp["SGPA"] = roties[1]
                        break
                data.append(temp)
        elif "The Hall Ticket Number" == pageSoup.find("table",{"id":"AutoNumber1"}).findAll("b")[1].text[9:31]:
            return True
        else:
            ndata.append(x)
            return False
        return True
    except Exception as e:
        ndata.append(x)
        return False

def multiThreadCall(Url,st,en):
    try:
        threads_k = []
        for i in range(st,en+1):
            t = Thread(target = multiThread, args=(Url,i,))
            threads_k.append(t)
            t.start()
        for t in threads_k:
            t.join()
    except Exception as e:
        print(e)
        print("Intiating Threads Again!!!")
        Thread(target = multiThreadCall, args=(st,en)).start()


@app.get("/")
async def sample():
    return {"message" : random.choice(messages)}


@app.post("/download")
async def download_xlsx(url: str, range: str):
    
    for i in range.split(","):
        r=str(i).split("-")
        x=int(r[0])
        y=int(r[1])
        if(len(r)>2):
            return {"custome_error":"Input format or range is wrong."}
        if(x<=y):
            multiThreadCall(url,x,y)
        else:
            return {"custome_error":"Input format or range is wrong."}
    
    return {"found_data":sorted(data,key=lambda x: (str(x["Roll Number"])+x["Sub Code"])),"not_found_data":set(ndata)}
