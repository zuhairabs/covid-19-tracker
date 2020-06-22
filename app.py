#!/usr/bin/env python 
from flask import Flask, render_template, request, make_response, session, redirect, url_for, g
from flask_socketio import SocketIO, emit, send
import json # to be able to use and manipulate json files
import time
import requests
############################## Developed By ZUHAIR ABBAS ############################
SERVER_HOST = "localhost"
SERVER_PORT = 5000

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def requestApi():
	try:
		dataWorld = requests.get('https://corona.lmao.ninja/v2/all')
		dataWorld = dataWorld.json()
	except Exception as e:
		dataWorld = []
	try:
		dataCountry = requests.get('https://corona.lmao.ninja/v2/countries')
		dataCountry = dataCountry.json()
	except Exception as e:
		dataCountry = []
	try:
		dataIndia = requests.get('https://corona.lmao.ninja/v2/countries/india')
		dataIndia = dataIndia.json()
	except Exception as e:
		dataIndia = []
    
	return dataWorld, dataCountry, dataIndia

global dataWorld
global dataCountry
global dataIndia
dataWorld, dataCountry, dataIndia = requestApi()
###################################################
# THREAD
###################################################
def background_thread():
    global dataWorld
    global dataCountry
    global dataIndia
    while True:

        (dataWorld, dataCountry, dataIndia) = requestApi()

        socketio.emit('respuesta_datos',
                      {'data':'Values', 
                      'dataWorld': dataWorld,
                      'dataValueTerritories': len(dataCountry),
                      'dataCountry': dataCountry,
					  'dataIndia': dataIndia
                      },
                      namespace='/carpi')
        socketio.sleep(7)
###################################################
# INICIO
###################################################
@app.route('/', methods=["GET", "POST"])
def index():
    # for specific
    # print(list(filter(lambda x:x["country"]=="India",dataValues2.json())))

    return render_template('index.html',    async_mode = socketio.async_mode, 
                                            dataValuesCases = dataWorld['cases'],
											dataIndiaCases = dataIndia['cases'],
                                            dataValuesDeaths = dataWorld['deaths'],
											dataIndiaDeaths = dataIndia['deaths'],
                                            dataValuesRecovered = dataWorld['recovered'],
											dataIndiaRecovered = dataIndia['recovered'],
											dataIndiaActive = dataIndia['active'],
                                            dataValuesTerritories = len(dataCountry),
											dataIndia = dataIndia,
                                            dataCountry = dataCountry)
###################################################
# Start
###################################################
@app.route('/country', methods=["GET", "POST"])
def country():
    # for specific
    # print(list(filter(lambda x:x["country"]=="India",dataValues2.json())))

    return render_template('country.html', 	async_mode=socketio.async_mode,	
											dataIndiaCases = dataIndia['cases'],
											dataIndiaDeaths = dataIndia['deaths'],
											dataIndiaRecovered = dataIndia['recovered'],
											dataIndiaActive = dataIndia['active'],
											dataIndia = dataIndia,
											dataCountry=dataCountry)
###################################################
# Start
###################################################
@app.route('/india', methods=["GET", "POST"])
def india():
    # for specific
    # print(list(filter(lambda x:x["country"]=="India",dataValues2.json())))

    return render_template('india.html', 	async_mode=socketio.async_mode,	
											dataIndiaCases = dataIndia['cases'],
											dataIndiaDeaths = dataIndia['deaths'],
											dataIndiaRecovered = dataIndia['recovered'],
											dataIndiaActive = dataIndia['active'],
											dataIndia = dataIndia,
											dataCountry=dataCountry)
###################################################
@socketio.on('client_connected', namespace='/carpi')
def handle_client_connect_event(json):
    var = '{0[data]:d}'.format(json)

@socketio.on('connect', namespace='/carpi')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':
    socketio.run(app, debug=True, host=SERVER_HOST, port=SERVER_PORT)
