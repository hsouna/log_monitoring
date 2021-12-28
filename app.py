from flask import Flask, Markup, render_template,request,Response
from flask_socketio import SocketIO,send, emit
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re
import pandas as pd
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def get_initial_dataFrames():
    lineformat = re.compile(r"""(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - (?P<userName>.*) \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(http\/1\.[1|0]")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) (["](?P<refferer>(\-)|(.+))["]) (["](?P<useragent>.+)["])""", re.IGNORECASE)

    errorsDf = pd.DataFrame(columns=['error_type','counts'])
    notFoundDf = pd.DataFrame(columns=['ressource','counts'])
    adeDf = pd.DataFrame(columns=['emplois_du_temps','counts'])
    persoDf = pd.DataFrame(columns=['page_perso','counts'])
    ipDf = pd.DataFrame()
    with open('/var/log/apache2/wp.access.log', 'r') as f:
        for line in f.readlines():
            data = re.search(lineformat, line)
            if data:
                datadict = data.groupdict()
                ip = datadict["ipaddress"]
                url = datadict["url"]
                status = datadict["statuscode"]
                method = data.group(7)
                if(method == 'GET'):
                    filename, file_extension = os.path.splitext(url)
                    if(file_extension.strip() == '.html' or file_extension.strip() == '.pdf'):
                        errorsDf = errorsDf.append({'error_type': status}, ignore_index=True)
                        if(status == "404"):
                            notFoundDf = notFoundDf.append({'ressource': url}, ignore_index=True)
                        m = re.search('/~denis/ade/(.*).html', url.strip())
                        if(m):
                            adeDf = adeDf.append({'emplois_du_temps': m.group(1)}, ignore_index=True)
                        m = re.search('/~([^/]*)/index.html', url.strip())
                        if(m):
                            persoDf = persoDf.append({'page_perso': m.group(1)}, ignore_index=True)
                        m = re.search('/~denis/docs/SLIDES/([^/]*([^2]))/.*', url.strip())
                    
                        ipDf = ipDf.append({'ip_address': ip}, ignore_index=True)
    if not errorsDf.empty:
        errorsDf = errorsDf.groupby(['error_type']).size().reset_index(name='counts')
    if not notFoundDf.empty:
        notFoundDf = notFoundDf.groupby(['ressource']).size().reset_index(name='counts')
    if not adeDf.empty:
        adeDf = adeDf.groupby(['emplois_du_temps']).size().reset_index(name='counts').sort_values(by=['counts'])
    if not persoDf.empty:
        persoDf = persoDf.groupby(['page_perso']).size().reset_index(name='counts').sort_values(by=['counts'])


    return {
        'error_type':{
            'x':errorsDf['error_type'].values.tolist(),
            'y':errorsDf['counts'].values.tolist(),
            'title':'Les types d\'erreurs'
        },
        'ressource':{
            'x': notFoundDf['ressource'].values.tolist(),
            'y': notFoundDf['counts'].values.tolist(),
            'title':'Les ressources visées lors des erreurs 404'
        },
        'emplois_du_temps':{
            'x': adeDf['emplois_du_temps'].values.tolist(),
            'y': adeDf['counts'].values.tolist(),
            'title':'Les emplois du temps'

        },
        'page_perso':{
            'x': persoDf['page_perso'].values.tolist(),
            'y': persoDf['counts'].values.tolist(),
            'title':'Les pages personnelles',
        }}



@app.route('/')
def index():
    res = get_initial_dataFrames()
    return render_template('index.html',initial_data=res)


actions = {
    'errors': lambda x: socketio.emit('error_type', x),
    'notFound': lambda x: socketio.emit('ressource', x),
    'ade': lambda x: socketio.emit('emplois_du_temps', x),
    'perso': lambda x: socketio.emit('page_perso', x),
    'ip': lambda x: socketio.emit('ip_address', x),
}


@app.route('/newLog',methods=['POST'])
def newLog():
    actions[request.json['type']](request.json['data'])
    return Response({'state':True}, mimetype='application/json')



if __name__ == '__main__':
    #app.run(host='localhost', port=8080)
    socketio.run(app)
    




