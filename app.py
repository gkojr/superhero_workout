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


def getUserData(user, data):
    import requests

    url = f"https://dev-odr1q7ojdd4dxh2p.us.auth0.com/api/v2/users/{user}?fields=user_metadata"


    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhtNDFBOXkxTW44eF9vQ3JfZmNDbiJ9.eyJpc3MiOiJodHRwczovL2Rldi1vZHIxcTdvamRkNGR4aDJwLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJoa0sxOTVTZlZSVjM2V1NkclJZaTk0bmJOazVCZHJld0BjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9kZXYtb2RyMXE3b2pkZDRkeGgycC51cy5hdXRoMC5jb20vYXBpL3YyLyIsImlhdCI6MTcwNzU4MjM5MiwiZXhwIjoxNzA3NjY4NzkyLCJhenAiOiJoa0sxOTVTZlZSVjM2V1NkclJZaTk0bmJOazVCZHJldyIsInNjb3BlIjoicmVhZDpjbGllbnRfZ3JhbnRzIGNyZWF0ZTpjbGllbnRfZ3JhbnRzIGRlbGV0ZTpjbGllbnRfZ3JhbnRzIHVwZGF0ZTpjbGllbnRfZ3JhbnRzIHJlYWQ6dXNlcnMgdXBkYXRlOnVzZXJzIGRlbGV0ZTp1c2VycyBjcmVhdGU6dXNlcnMgcmVhZDp1c2Vyc19hcHBfbWV0YWRhdGEgdXBkYXRlOnVzZXJzX2FwcF9tZXRhZGF0YSBkZWxldGU6dXNlcnNfYXBwX21ldGFkYXRhIGNyZWF0ZTp1c2Vyc19hcHBfbWV0YWRhdGEgcmVhZDp1c2VyX2N1c3RvbV9ibG9ja3MgY3JlYXRlOnVzZXJfY3VzdG9tX2Jsb2NrcyBkZWxldGU6dXNlcl9jdXN0b21fYmxvY2tzIGNyZWF0ZTp1c2VyX3RpY2tldHMgcmVhZDpjbGllbnRzIHVwZGF0ZTpjbGllbnRzIGRlbGV0ZTpjbGllbnRzIGNyZWF0ZTpjbGllbnRzIHJlYWQ6Y2xpZW50X2tleXMgdXBkYXRlOmNsaWVudF9rZXlzIGRlbGV0ZTpjbGllbnRfa2V5cyBjcmVhdGU6Y2xpZW50X2tleXMgcmVhZDpjb25uZWN0aW9ucyB1cGRhdGU6Y29ubmVjdGlvbnMgZGVsZXRlOmNvbm5lY3Rpb25zIGNyZWF0ZTpjb25uZWN0aW9ucyByZWFkOnJlc291cmNlX3NlcnZlcnMgdXBkYXRlOnJlc291cmNlX3NlcnZlcnMgZGVsZXRlOnJlc291cmNlX3NlcnZlcnMgY3JlYXRlOnJlc291cmNlX3NlcnZlcnMgcmVhZDpkZXZpY2VfY3JlZGVudGlhbHMgdXBkYXRlOmRldmljZV9jcmVkZW50aWFscyBkZWxldGU6ZGV2aWNlX2NyZWRlbnRpYWxzIGNyZWF0ZTpkZXZpY2VfY3JlZGVudGlhbHMgcmVhZDpydWxlcyB1cGRhdGU6cnVsZXMgZGVsZXRlOnJ1bGVzIGNyZWF0ZTpydWxlcyByZWFkOnJ1bGVzX2NvbmZpZ3MgdXBkYXRlOnJ1bGVzX2NvbmZpZ3MgZGVsZXRlOnJ1bGVzX2NvbmZpZ3MgcmVhZDpob29rcyB1cGRhdGU6aG9va3MgZGVsZXRlOmhvb2tzIGNyZWF0ZTpob29rcyByZWFkOmFjdGlvbnMgdXBkYXRlOmFjdGlvbnMgZGVsZXRlOmFjdGlvbnMgY3JlYXRlOmFjdGlvbnMgcmVhZDplbWFpbF9wcm92aWRlciB1cGRhdGU6ZW1haWxfcHJvdmlkZXIgZGVsZXRlOmVtYWlsX3Byb3ZpZGVyIGNyZWF0ZTplbWFpbF9wcm92aWRlciBibGFja2xpc3Q6dG9rZW5zIHJlYWQ6c3RhdHMgcmVhZDppbnNpZ2h0cyByZWFkOnRlbmFudF9zZXR0aW5ncyB1cGRhdGU6dGVuYW50X3NldHRpbmdzIHJlYWQ6bG9ncyByZWFkOmxvZ3NfdXNlcnMgcmVhZDpzaGllbGRzIGNyZWF0ZTpzaGllbGRzIHVwZGF0ZTpzaGllbGRzIGRlbGV0ZTpzaGllbGRzIHJlYWQ6YW5vbWFseV9ibG9ja3MgZGVsZXRlOmFub21hbHlfYmxvY2tzIHVwZGF0ZTp0cmlnZ2VycyByZWFkOnRyaWdnZXJzIHJlYWQ6Z3JhbnRzIGRlbGV0ZTpncmFudHMgcmVhZDpndWFyZGlhbl9mYWN0b3JzIHVwZGF0ZTpndWFyZGlhbl9mYWN0b3JzIHJlYWQ6Z3VhcmRpYW5fZW5yb2xsbWVudHMgZGVsZXRlOmd1YXJkaWFuX2Vucm9sbG1lbnRzIGNyZWF0ZTpndWFyZGlhbl9lbnJvbGxtZW50X3RpY2tldHMgcmVhZDp1c2VyX2lkcF90b2tlbnMgY3JlYXRlOnBhc3N3b3Jkc19jaGVja2luZ19qb2IgZGVsZXRlOnBhc3N3b3Jkc19jaGVja2luZ19qb2IgcmVhZDpjdXN0b21fZG9tYWlucyBkZWxldGU6Y3VzdG9tX2RvbWFpbnMgY3JlYXRlOmN1c3RvbV9kb21haW5zIHVwZGF0ZTpjdXN0b21fZG9tYWlucyByZWFkOmVtYWlsX3RlbXBsYXRlcyBjcmVhdGU6ZW1haWxfdGVtcGxhdGVzIHVwZGF0ZTplbWFpbF90ZW1wbGF0ZXMgcmVhZDptZmFfcG9saWNpZXMgdXBkYXRlOm1mYV9wb2xpY2llcyByZWFkOnJvbGVzIGNyZWF0ZTpyb2xlcyBkZWxldGU6cm9sZXMgdXBkYXRlOnJvbGVzIHJlYWQ6cHJvbXB0cyB1cGRhdGU6cHJvbXB0cyByZWFkOmJyYW5kaW5nIHVwZGF0ZTpicmFuZGluZyBkZWxldGU6YnJhbmRpbmcgcmVhZDpsb2dfc3RyZWFtcyBjcmVhdGU6bG9nX3N0cmVhbXMgZGVsZXRlOmxvZ19zdHJlYW1zIHVwZGF0ZTpsb2dfc3RyZWFtcyBjcmVhdGU6c2lnbmluZ19rZXlzIHJlYWQ6c2lnbmluZ19rZXlzIHVwZGF0ZTpzaWduaW5nX2tleXMgcmVhZDpsaW1pdHMgdXBkYXRlOmxpbWl0cyBjcmVhdGU6cm9sZV9tZW1iZXJzIHJlYWQ6cm9sZV9tZW1iZXJzIGRlbGV0ZTpyb2xlX21lbWJlcnMgcmVhZDplbnRpdGxlbWVudHMgcmVhZDphdHRhY2tfcHJvdGVjdGlvbiB1cGRhdGU6YXR0YWNrX3Byb3RlY3Rpb24gcmVhZDpvcmdhbml6YXRpb25zX3N1bW1hcnkgY3JlYXRlOmF1dGhlbnRpY2F0aW9uX21ldGhvZHMgcmVhZDphdXRoZW50aWNhdGlvbl9tZXRob2RzIHVwZGF0ZTphdXRoZW50aWNhdGlvbl9tZXRob2RzIGRlbGV0ZTphdXRoZW50aWNhdGlvbl9tZXRob2RzIHJlYWQ6b3JnYW5pemF0aW9ucyB1cGRhdGU6b3JnYW5pemF0aW9ucyBjcmVhdGU6b3JnYW5pemF0aW9ucyBkZWxldGU6b3JnYW5pemF0aW9ucyBjcmVhdGU6b3JnYW5pemF0aW9uX21lbWJlcnMgcmVhZDpvcmdhbml6YXRpb25fbWVtYmVycyBkZWxldGU6b3JnYW5pemF0aW9uX21lbWJlcnMgY3JlYXRlOm9yZ2FuaXphdGlvbl9jb25uZWN0aW9ucyByZWFkOm9yZ2FuaXphdGlvbl9jb25uZWN0aW9ucyB1cGRhdGU6b3JnYW5pemF0aW9uX2Nvbm5lY3Rpb25zIGRlbGV0ZTpvcmdhbml6YXRpb25fY29ubmVjdGlvbnMgY3JlYXRlOm9yZ2FuaXphdGlvbl9tZW1iZXJfcm9sZXMgcmVhZDpvcmdhbml6YXRpb25fbWVtYmVyX3JvbGVzIGRlbGV0ZTpvcmdhbml6YXRpb25fbWVtYmVyX3JvbGVzIGNyZWF0ZTpvcmdhbml6YXRpb25faW52aXRhdGlvbnMgcmVhZDpvcmdhbml6YXRpb25faW52aXRhdGlvbnMgZGVsZXRlOm9yZ2FuaXphdGlvbl9pbnZpdGF0aW9ucyBkZWxldGU6cGhvbmVfcHJvdmlkZXJzIGNyZWF0ZTpwaG9uZV9wcm92aWRlcnMgcmVhZDpwaG9uZV9wcm92aWRlcnMgdXBkYXRlOnBob25lX3Byb3ZpZGVycyBkZWxldGU6cGhvbmVfdGVtcGxhdGVzIGNyZWF0ZTpwaG9uZV90ZW1wbGF0ZXMgcmVhZDpwaG9uZV90ZW1wbGF0ZXMgdXBkYXRlOnBob25lX3RlbXBsYXRlcyBjcmVhdGU6ZW5jcnlwdGlvbl9rZXlzIHJlYWQ6ZW5jcnlwdGlvbl9rZXlzIHVwZGF0ZTplbmNyeXB0aW9uX2tleXMgZGVsZXRlOmVuY3J5cHRpb25fa2V5cyByZWFkOnNlc3Npb25zIGRlbGV0ZTpzZXNzaW9ucyByZWFkOnJlZnJlc2hfdG9rZW5zIGRlbGV0ZTpyZWZyZXNoX3Rva2VucyByZWFkOmNsaWVudF9jcmVkZW50aWFscyBjcmVhdGU6Y2xpZW50X2NyZWRlbnRpYWxzIHVwZGF0ZTpjbGllbnRfY3JlZGVudGlhbHMgZGVsZXRlOmNsaWVudF9jcmVkZW50aWFscyIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyJ9.TYCZ3LeoUT060UtgEH_B5JW6GkBXwzqRr6nqB9PW1egKWN4smJrJDkHvVFBe3BZ7x1ygexfagaLSXOU6vr-h0E4cwXo1aH7U0dnDH4aAuYls8YTsdWPW9lqGTQesBwFj_aUJqjYctWRsCrnqqBWWTR2xS2GBXwaIVyH9ckfOmHeoQEyjcWd59LZ8JNfB9ZdnaJHxDcyguZsgJerS6TIFkGigN0hykvwGCfHDQCvjun9Si1jvhnHvt55w8vmXUIslwjyvQjYkLxRLvDPFm8K3mtMwvy59sLvG8bcdzdsBYM1gcnf3c_HXIkJRVjjY_DgDEra5MqYiF8tz4MdPXl6icw'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    responseJson = json.loads(response.text)
    return responseJson['user_metadata'][data]



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
    allow_delegation=False,

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
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=4000,
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

    print(result)
    result = response.choices[0].message.content
    return jsonify(result)

# parameters are the users age, height, and weight. as well as the superheroes name. and whether you want the result to be formatted in json
@app.route('/diet/<name>/<age>/<height>/<weight>/<formatted>')
def generateDiet(name, age, height, weight, formatted):
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
@app.route('/workout/<name>/<age>/<height>/<weight>/<formatted>')
def generateWorkoutPlan(name, age, height, weight, formatted):
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

    return response.choices[0].message.content

@app.route('/')
def index():
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route('/heroView/<hero_id>', methods=['GET', 'POST'])
def heroView(hero_id):
    return render_template("heroView.html", hero_id=hero_id, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
    
   