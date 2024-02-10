from flask import Flask, render_template, jsonify
import requests
import os
from openai import OpenAI
from crewai import Agent, Task, Crew, Process
import traceback
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__, template_folder='templates')
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
    hero_id = get_hero_id(name);
    hero_data = get_hero_info(hero_id);
    return hero_data;


#ai stuff
initTasks = []
openAIKey = env.get('OPENAI_API_KEY')
client = OpenAI(api_key=openAIKey)


dietician = Agent(
    role='Dietician',
    goal='Given a persons age, height, weight, and a given superhero goal, create a perfect diet to ensure that person reaches their goal.',
    backstory='You work at a lead physiological think tank. Your expertise lies in creating diets for anyone to ensure that they reach their goals. You have a knack for making sure that these diets are efficient, tasty, and affordable.',
    verbose=True,
    allow_delegation=False
)

personalTrainer = Agent(
    role='Personal Trainer',
    goal='Given a persons age, height, weight, and a given superhero goal, create a perfect workout plan to ensure that person reaches their goal.',
    backstory='You work at a lead physiological think tank. Your expertise lies in creating workout plans for anyone to ensure that they reach their goals. You have a knack for making sure that these plans are efficient, reasonable, and doable by anyone.',
    verbose=True,
    allow_delegation=False
)

jsonFormatter = Agent(
    role='JSON Formatter',
    goal='Given a diet or workout plan, format the result into a json format that can be used in a python array or dataframe to output the data.',
    backstory='You work at a lead tech think tank. Your expertise lies in formatting data into JSON for use in code. You have a knack for making sure that the results are efficient, reasonable, and easily implemented by anyone.',
    verbose=False,
    allow_delegation=False
)

fanboy = Agent(
    role='Fanboy',
    goal='Given the name of a superhero, you are to think of everything that superhero has gone throught within their entire life.',
    backstory='You are someone who has religiously tracked every single superhero and knows everything about them. You have done this for over 50 years and has accumulated a vast foundation in superhero knowledge. You have a knack for easily coming up with the answer for any question about any superhero and making sure that the answer is true and easily understanded by laymen.',
    verbose=True,
    allow_delegation=False
)

@app.route('/description/<name>')
def generateDescription(name):
    genDesc = Task(
        description=f"""Using the insights provided, develop a fully comprehensive description about a given superhero. The description should be informative yet accessible, catering to a casual audience who does not know much about superheroes. Your final answer MUST be no longer than 3 sentences.""",
        agent=dietician
    )
    result = runTask(genDesc)
    return result

# parameters are the users age, height, and weight. as well as the superheroes name. and whether you want the result to be formatted in json
def generateDiet(age, height, weight, superhero, formatted):
    genDiet = Task(
        description=f"""Using the insights provided, develop a fully comprehensive diet plan that ecompasses exactly what the user needs to do to achieve their specified goals. The diet plan should be informative yet accessible, catering to a casual audience who does not know much about dieting. The user is {age} years old, weighs {weight}lbs, and is {height} inches tall. Their superhero physique that they are hoping to achieve is {superhero}. Your final answer MUST include at least 3 options for every meal. Your final answer MUST also be relevant to the provided stats of the user (age, height, and weight).""",
        agent=dietician
    )
    result = runTask(genDiet)
    if formatted:
        r = formatJson(result)
        return r
    else:
        return result

# parameters are the users age, height, and weight. as well as the superheroes name. and whether you want the result to be formatted in json
def generateWorkoutPlan(age, height, weight, superhero, formatted):
    genWorkout = Task(
        description=f"""Using the insights provided, develop a fully comprehensive workout plan that ecompasses exactly what the user needs to do to achieve their specified goals. The workout plan should be informative yet accessible, catering to a casual audience who does not know much about working out. The user is {age} years old, weighs {weight}lbs, and is {height} inches tall. Their superhero physique that they are hoping to achieve is {superhero}. Your final answer MUST be relevant to the provided stats of the user (age, height, and weight).""",
        agent=personalTrainer
    )
    result = runTask(genWorkout)
    if formatted:
        r = formatJson(result)
        return r
    else:
        return result 
    
def formatJson(input):
    formatJson = Task(
        description=f'Given the following diet/workout plan {input}, format the result in a way that each day is specifially seperated in terms of calendar dates (Monday, Tuesday, Wednesday, etc), and properly format in a JSON format so that the result can be used in a future python array.',
        agent=jsonFormatter
    )
    result = runTask(formatJson)
    return result

def runTask(task):
    plan = Crew(
        agents=[dietician, personalTrainer],
        tasks=task,
        verbose=2
    )
    result = plan.kickoff()
    return result

def chat(msg, hero):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=4000,
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

    return response.choices[0].message.content

@app.route('/')
def index():
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
    
   