# Imports
from flask import Flask, send_file, request, render_template
from Services import scrapService as ScrapService
from Schemas.SearchParametersModel import SearchParametersModel
from flask_pydantic import validate
import os

app = Flask(__name__)

@app.route('/')
def init():
    opciones_dropdown = ['Server on', 'Server off']
    return render_template('index.html', opciones=opciones_dropdown)

@app.route('/bypass/', methods=['POST'])
@validate()
def bypassSite(body: SearchParametersModel):
    response = ScrapService.scrapSouthCarolina(body)
    # txt = f'{result_file_name}'
    # if not os.path.exists(txt):
    #     return 'txt cant be found', 404
    # response = send_file(txt, as_attachment=True)
    # os.remove(txt)

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)