from flask import Flask, render_template, jsonify
import requests
import os
from crewai import Agent, Task, Crew, Process
from openai import OpenAI
#from dotenv import load_dotenv


#load_dotenv()
#openai_api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/hero/<name>')
def get_hero_id(name):
    url = f'https://www.superheroapi.com/api.php/1877251196060770/search/{name}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        id = data.results[0].id; 
        return id; 
    else:
        return jsonify(error = 'Hero not found'), 404
    
    