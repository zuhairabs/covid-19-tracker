#!/usr/bin/env python 
from flask import Flask, render_template, request, make_response, session, redirect, url_for, g
from flask_socketio import SocketIO, emit, send
import json # para poder utilizar y manipular archivos json
import time
import requests

SERVER_HOST = "localhost"
SERVER_PORT = 5000

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def requestApi():
    try:
        dataWorld = requests.get('https://corona.lmao.ninja/all')
        dataWorld = dataWorld.json()
    except Exception as e:
        dataWorld = []
    try:
        dataCountry = requests.get('https://corona.lmao.ninja/countries')
        dataCountry = dataCountry.json()
    except Exception as e:
        dataCountry = []
    
    return dataWorld, dataCountry

global dataWorld
global dataCountry
dataWorld, dataCountry = requestApi()
###################################################
# THREAD
###################################################
def background_thread():
    global dataWorld
    global dataCountry
    while True:

        (dataWorld, dataCountry) = requestApi()

        socketio.emit('respuesta_datos',
                      {'data':'Values', 
                      'dataWorld': dataWorld,
                      'dataValueTerritories': len(dataCountry),
                      'dataCountry': dataCountry
                      },
                      namespace='/carpi')
        socketio.sleep(7)
###################################################
# INICIO
###################################################
@app.route('/', methods=["GET", "POST"])
def index():
    # para buscar uno específico
    # print(list(filter(lambda x:x["country"]=="Chile",dataValues2.json())))

    return render_template('index.html',    async_mode = socketio.async_mode, 
                                            dataValuesCases = dataWorld['cases'], 
                                            dataValuesDeaths = dataWorld['deaths'],
                                            dataValuesRecovered = dataWorld['recovered'],
                                            dataValuesTerritories = len(dataCountry),
                                            dataCountry = dataCountry) # retorna la pestaña de inicio
###################################################
# INICIO
###################################################
@app.route('/country', methods=["GET", "POST"])
def country():
    # para buscar uno específico
    # print(list(filter(lambda x:x["country"]=="Chile",dataValues2.json())))

    return render_template('country.html', async_mode=socketio.async_mode, dataCountry=dataCountry) # retorna la pestaña de inicio
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