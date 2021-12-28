import os
import argparse
import re
import pandas as pd
from urllib.request import urlopen
from json import load
import requests
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler 



def treatLine(line):
    lineformat = re.compile(r"""(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - (?P<userName>.*) \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(http\/1\.[1|0]")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) (["](?P<refferer>(\-)|(.+))["]) (["](?P<useragent>.+)["])""", re.IGNORECASE)
    data = re.search(lineformat, line)
    if data:
        datadict = data.groupdict()
        ip = datadict["ipaddress"]
        url = datadict["url"]
        status = datadict["statuscode"]
        method = data.group(7)
        if(method == 'GET'):
            flask_url = 'http://127.0.0.1:5000/newLog'
            filename, file_extension = os.path.splitext(url)
            if(file_extension.strip() == '.html' or file_extension.strip() == '.pdf'):
                requests.post(flask_url, json={'type':'errors','data':{'error_type': status}})
                if(status == "404"):
                    requests.post(flask_url, json={'type':'notFound','data':{'ressource': url}})
                m = re.search('/~denis/ade/(.*).html', url.strip())
                
                if(m):
                    requests.post(flask_url, json={'type':'ade','data':{'emplois_du_temps': m.group(1)}})
                m = re.search('/~([^/]*)/index.html', url.strip())
                if(m):
                    requests.post(flask_url, json={'type':'perso','data':{'page_perso': m.group(1)}})
                m = re.search('/~denis/docs/SLIDES/([^/]*([^2]))/.*', url.strip())
                requests.post(flask_url, json={'type':'ip','data':{'ip_address': ip}})

'''
def graph_countries(ipDf=None):
    ipDf = ipDf.groupby(['ip_address']).size().reset_index(name='counts')
    for index, row in ipDf.iterrows():
        url = 'https://ipinfo.io/' + row['ip_address'] + '/json?token=d1e8801329c23c'
        res = urlopen(url)
        #response from url(if res==None then check connection)
        data = load(res)
        for attr in data.keys():
            ipDf.loc[ipDf.index[index], attr] = data[attr]
    print(ipDf)
    ipDf.to_csv('ip_info.csv') 
    ipDf = pd.read_csv('ip_info.csv')
    fig = plt.figure(figsize=(10,10))
    sns.barplot(x="country",y="counts",data=ipDf.groupby(['country']).size().reset_index(name='counts'))
    fig.savefig('outputCat4.png')
    print(ipDf)'''
    


def main():
    with open('/var/log/apache2/wp.access.log', 'r') as f:
        f.seek(0,2)
        event_handler = MyHandler(f)
        observer = Observer()
        observer.schedule(event_handler,  path='/var/log/apache2/wp.access.log',  recursive=False)
        observer.start()

        try:
            while  True:
                time.sleep(1)
        except  KeyboardInterrupt:
            observer.stop()
        observer.join()


class  MyHandler(FileSystemEventHandler):
    def __init__(self, file_pointer):
        self.f = file_pointer
    
    def  on_modified(self,  event):
        for line in self.f.readlines():
            treatLine(line)
            
            print(line)
    def  on_created(self,  event):
         print(f'event type: {event.event_type} path : {event.src_path}')
    def  on_deleted(self,  event):
         print(f'event type: {event.event_type} path : {event.src_path}')


import fileinput

if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("--file_path", required=False,
    help="Input file path")

    args = vars(ap.parse_args())
    file_path = args["file_path"]

    #watch_file()
    #graph_countries()
    main()