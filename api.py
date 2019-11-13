import configparser
import constant
from flask import Flask, request, render_template
from flask_restful import Resource


config = configparser.ConfigParser()
config.read(constant.valueConfig)
conser = config.options('server')
congen = config.options('general')
congate = config.options('gate')
    
class SelectConfig(Resource):
    
    def get(self):
        result = congen + conser + congate
        print ("test", result)
        return render_template('index.html', result=result)

    # def post(self):
    #     for i in conser:
    #         config['server'][i] = request.form['{}'.format(i)]
        
    #     return 

        