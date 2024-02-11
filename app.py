from flask import Flask, render_template, jsonify, request
import requests
import os
from openai import OpenAI
from crewai import Agent, Task, Crew, Process
import traceback
import http.client
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, jsonify
from flask_cors import CORS

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__, template_folder='templates')
CORS(app)
app.secret_key = env.get("APP_SECRET_KEY")

#oauth stuff
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

#hero info route stuff 
def get_hero_id(name):
    url = f'https://www.superheroapi.com/api.php/1877251196060770/search/{name}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])  # Get the 'results' key from data
        if results:  # Check if results is not empty
            hero_id = results[0]['id']  # Access the first hero's ID
            return hero_id
        else:
            return jsonify(error='Hero not found'), 404
    else:
        return jsonify(error='API request failed'), response.status_code

@app.route('/heroID/<id>')
def get_hero_info(id):
    url = f'https://www.superheroapi.com/api.php/1877251196060770/{id}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return jsonify(error='API request failed'), response.status_code

@app.route('/hero/<name>')
def get_hero_data(name): 
    hero_id = get_hero_id(name)
    hero_data = get_hero_info(hero_id)
    return hero_data

#authoriztion stuff 

DOMAIN = env.get("AUTH0_DOMAIN")
ACCESS_TOKEN = env.get("MANAGEMENT_SECRET")
AUDIENCE = f'https://{DOMAIN}/api/v2/'

def getUserData(user, data):
    url = f"https://{DOMAIN}/api/v2/users/{user}?fields=user_metadata"


    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    responseJson = json.loads(response.text)
    return responseJson['user_metadata'][data]

# Route to update user metadata
@app.route('/update_metadata', methods=['POST'])
def update_metadata():
    # Get user ID and metadata from the request
    user_id = request.json.get('user_id')
    print(user_id)
    metadata = request.json.get('metadata')
    print(metadata)

    url = f"https://{DOMAIN}/api/v2/users/{user_id}"
    headers = {
        'Authorization': f"Bearer {ACCESS_TOKEN}",
        'Content-Type': 'application/json'
    }
    payload = {
        "user_metadata": metadata
    }
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

#ai stuff
initTasks = []
openAIKey = env.get('OPENAI_API_KEY')
client = OpenAI(api_key=openAIKey)

@app.route('/description/<name>')
def generateDescription(name):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            messages=[
                {"role": "system", "content": f"Given the name of a superhero, you are to think of everything that superhero has gone throught within their entire life. You are someone who has religiously tracked every single superhero and knows everything about them. You have done this for over 50 years and has accumulated a vast foundation in superhero knowledge. You have a knack for easily coming up with the answer for any question about any superhero and making sure that the answer is true and easily understanded by laymen."},
                {"role": "user", "content": f"Using the insights provided, develop a fully comprehensive description about {name}. The description should be informative yet accessible, catering to a casual audience who does not know much about superheroes. Your final answer MUST be no longer than 3 sentences."}
            ]
        )
    except Exception as e:
        traceback.print_exc()

    result = response.choices[0].message.content
    return jsonify(result)

# parameters are the users age, height, and weight. as well as the superheroes name. and whether you want the result to be formatted in json
@app.route('/diet/<name>/<userId>/<formatted>')
def generateDiet(name, userId, formatted):
    age = getUserData(userId, "age")
    weight = getUserData(userId, "weight")
    height = getUserData(userId, "height")
    formatted = eval(formatted)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            messages=[
                {"role": "system", "content": f"Given a persons age, height, weight, and a given superhero goal, create a perfect diet to ensure that person reaches their goal. You work at a lead physiological think tank. Your expertise lies in creating diets for anyone to ensure that they reach their goals. You have a knack for making sure that these diets are efficient, tasty, and affordable.,"},
                {"role": "user", "content": f"Using the insights provided, develop a fully comprehensive diet plan that ecompasses exactly what the user needs to do to achieve their specified goals. The diet plan should be informative yet accessible, catering to a casual audience who does not know much about dieting. The user is {age} years old, weighs {weight}lbs, and is {height} inches tall. Their superhero physique that they are hoping to achieve is {name}. Your final answer MUST include at least 3 options for every meal. Your final answer MUST also be relevant to the provided stats of the user (age, height, and weight)."}
            ]
        )
    except Exception as e:
        traceback.print_exc()

    result = response.choices[0].message.content
    if (formatted==True):
        r = formatJson(result)
        return r
    else:
        return jsonify(result)
# parameters are the users age, height, and weight. as well as the superheroes name. and whether you want the result to be formatted in json
@app.route('/workout/<name>/<userId>/<formatted>')
def generateWorkoutPlan(name, userId, formatted):
    age = getUserData(userId, "age")
    weight = getUserData(userId, "weight")
    height = getUserData(userId, "height")
    formatted = eval(formatted)
    print(f'inputted paramters are {name}, {age}, {height}, {weight}, {formatted} {type(formatted)}')
    try:
        print('generating workout plan')
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            messages=[
                {"role": "system", "content": f"Given a persons age, height, weight, and a given superhero goal, create a perfect workout plan to ensure that person reaches their goal. You work at a lead physiological think tank. Your expertise lies in creating workout plans for anyone to ensure that they reach their goals. You have a knack for making sure that these plans are efficient, reasonable, and doable by anyone."},
                {"role": "user", "content": f"Using the insights provided, develop a fully comprehensive workout plan that ecompasses exactly what the user needs to do to achieve their specified goals. The workout plan should be informative yet accessible, catering to a casual audience who does not know much about working out. The user is {age} years old, weighs {weight}lbs, and is {height} inches tall. Their superhero physique that they are hoping to achieve is {name}. Your final answer MUST be relevant to the provided stats of the user (age, height, and weight)."}
            ]
        )
    except Exception as e:
        traceback.print_exc()

    print('generated workout plan')
    result = response.choices[0].message.content
    if (formatted==True):
        r = formatJson(result)
        return r
    else:
        return jsonify(result)
    
    
    
def formatJson(input):
    print("formatting json")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            messages=[
                {"role": "system", "content": f"Given a diet or workout plan, format the result into a json format that can be used in a python array or dataframe to output the data. You work at a lead tech think tank. Your expertise lies in formatting data into JSON for use in code. You have a knack for making sure that the results are efficient, reasonable, and easily implemented by anyone."},
                {"role": "user", "content": f"Given the following diet/workout plan {input}, format the result in a way that each day is specifially seperated in terms of calendar dates (Monday, Tuesday, Wednesday, etc), and properly format in a JSON format so that the result can be used in a future python array."}
            ]
        )
    except Exception as e:
        traceback.print_exc()

    result = response.choices[0].message.content
    print('formatted json')
    return jsonify(result)

@app.route('/chat/<msg>/<hero>')
def chat(msg, hero):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            messages=[
                {"role": "system", "content": f"You are a helpful assistant designed to imitate the speaking style of {hero}, and give the most {hero}esque response to any given question."},
                {"role": "user", "content": msg}
            ]
        )
    except Exception as e:
        traceback.print_exc()

    return jsonify(response.choices[0].message.content)

@app.route('/')
def index():
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route('/heroView/<hero_id>', methods=['GET', 'POST'])
def heroView(hero_id):
    return render_template("heroView.html", hero_id=hero_id, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route('/profile')
def profileView():
    return render_template("profile.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
    
   