import os
import configparser
import json
import jinja2
import constant 
import subprocess
import threading
from flask import Flask, render_template, request, Response,redirect, url_for
import base64
from functools import wraps
from datetime import datetime
env = jinja2.Environment()

app = Flask(__name__)
config = configparser.ConfigParser()
app.jinja_env.globals.update(zip=zip)
configFile = constant.configFile

config.read(configFile)
conser = config.options('server')
congen = config.options('general')
condev = config.options('device')
congate = config.options('gate')
conadam = config.options('adam')

def ipset():
    config.read(configFile)
    readip = config['device']['ip']
    netmask = config['device']['netmask']
    os.system('sudo ifconfig eth0 {0} netmask {1} up'.format(readip,netmask))
    print('ip eth0: {0}, gw eth0:{1}'.format(readip,netmask))

def gatewayset():
    config.read(configFile)
    readip = config['device']['ip']
    gateway = config['device']['gateway']
    print('gw eth0: %s'% gateway)
    os.system('sudo route del default')
    os.system('sudo route del default')
    #os.system('sudo ip route delete 10.10.214.0/24')
    #os.system('sudo ip route delete 10.10.214.0/24')
    #os.system('sudo ip route delete 169.254.0.0/16')
    os.system('sudo ip route add 10.10.214.0/24 via {}'.format(readip))
    os.system('sudo route add default gw {}'.format(gateway))


import rpyc
import hashlib
import sys

hash = hashlib.md5("halotec".encode('utf-8')).hexdigest()

class RpycClient:
    def __init__(self, host, port, hash):

        channel = rpyc.Channel(rpyc.SocketStream.connect(host, port))
        secure = rpyc.core.brine.dump(hash)

        channel.send( secure )

        response = channel.recv()

        if response == 'AUTH_ERROR':
            raise ValueError('Invalid hash')

        self.conn = rpyc.utils.factory.connect_channel(channel)
    def get_config(self):
        self.conn.root.retrieve_config()
    def get_in(self):
        self.conn.root.get_in()
    def get_boom_open(self):
        self.conn.root.get_boom_open()
    def get_boom_close(self):
        self.conn.root.get_boom_close()
    def get_error(self):
        self.conn.root.get_error()
    def get_out(self):
        self.conn.root.get_out()
    def get_test(self,st):
	self.conn.root.get_test(st)

@app.route('/time_feed')
def time_feed():
    def generate():
        yield datetime.now().strftime("%Y.%m.%d|%H:%M")  # return also will work
    return Response(generate(), mimetype='text') 

def check(authorization_header):
    config.read(configFile)
    username = config.get("general","username")
    password = config.get("general","password")
    encoded_uname_pass = authorization_header.split()[-1]
    if encoded_uname_pass == base64.b64encode(username + ":" + password):
        return True

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and check(authorization_header):
            return f(*args, **kwargs)
        else:
            resp = Response()
            resp.headers['WWW-Authenticate'] = 'Basic'
            return resp, 401
        return f(*args, **kwargs)
    return decorated

@app.route('/gatein', methods=['GET','POST'])
@login_required
def gatein():
    r = RpycClient("localhost", 54321,hash)
    threading.Thread(target=r.get_in).start()
    return redirect(url_for('home'))

@app.route('/error',methods=['POST','GET'])
@login_required
def error():
	r = RpycClient("localhost", 54321,hash)
    	threading.Thread(target=r.get_error).start()
	return redirect(url_for('home'))

@app.route('/boomopen', methods=['GET','POST'])
@login_required
def boomopen():
    r = RpycClient("localhost", 54321,hash)
    threading.Thread(target=r.get_boom_open).start()
    return redirect(url_for('home'))

@app.route('/boomclose',methods=['POST','GET'])
@login_required
def boomclose():
        r = RpycClient("localhost", 54321,hash)
        threading.Thread(target=r.get_boom_close).start()
        return redirect(url_for('home'))

@app.route('/test',methods=['POST','GET'])
@login_required
def test():
        r = RpycClient("localhost", 54321,hash)
	st = request.form['test']
	print st 
	if st=='':
		return redirect(url_for('home'))
        threading.Thread(target=r.get_test,args=(st,)).start()
        return redirect(url_for('home'))


# read and set config.ini
@app.route('/', methods=['POST','GET'])
@login_required
def home():

    if request.method == 'POST':
        # set general
        for i in congen:
            config['general'][i] = request.form['{}'.format(i)]
    	# set device
        for i in condev:
            config['device'][i] = request.form['{}'.format(i)]
        # set server
        for i in conser:
            config['server'][i] = request.form['{}'.format(i)]
        # set gate
        for i in congate:
            config['gate'][i] = request.form['{}'.format(i)]
        # set adam
        for i in conadam:
            config['adam'][i] = request.form['{}'.format(i)]

        with open(configFile,'w') as configfile:
            config.write(configfile)
        
        f = open(configFile)
        if f.mode == 'r':
            response = f.read()
        f.close()
	print 'set ip'
	ipset()
	gatewayset()
        return redirect(request.url)
    else:
        # load general
        formgen = config.options('general')
        genval = [config.get('general', '{}'.format(i)) for i in formgen]
        # load device
        formdev = config.options('device')
        deval = [config.get('device','{}'.format(i)) for i in formdev]
	# load server
        formser = config.options('server')
        serval = [config.get('server', '{}'.format(i)) for i in formser]
        # load gate
        formgate = config.options('gate')
        gateval = [config.get('gate', '{}'.format(i)) for i in formgate]
	# load adam
        formadam = config.options('adam')
        adamval = [config.get('adam', '{}'.format(i)) for i in formadam]
	date = datetime.now().strftime("%Y.%m.%d|%H:%M")
        gatename = config.get('device','name')
	gateip = config.get('device','ip')
	return render_template('home.html',gatename=gatename,gateip=gateip,date=date,serval=serval, formser=formser, 
				gateval=gateval, formgate=formgate,
				formadam=formadam,adamval=adamval, 
				formgen=formgen, genval=genval,
				formdev=formdev, deval=deval)


@app.route('/front', methods=['GET','POST'])
def front():
    result = congen
    if request.method == 'POST':
        view = []
        for i in result:
            value = request.form.get(i)
            if value:
                view.append(value)
        return render_template('home.html',formgen=view,genval=view)

    return render_template('index.html', result=result)


if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port='3000')
