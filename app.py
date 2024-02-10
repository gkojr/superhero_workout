from flask import Flask, render_template, jsonify
import requests
import os
import openai
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import traceback

from packaging import version

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__}"
                     " is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")

from openai import OpenAI

load_dotenv()
openAIKey = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openAIKey)
initTasks = []

app = Flask(__name__)

#ai stuff
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

def generateDiet(age, height, weight, superhero):
    genDiet = Task(
        description=f"""Using the insights provided, develop a fully comprehensive diet plan that ecompasses exactly what the user needs to do to achieve their specified goals. The diet plan should be informative yet accessible, catering to a casual audience who does not know much about dieting. The user is {age} years old, weighs {weight}lbs, and is {height} inches tall. Their superhero physique that they are hoping to achieve is {superhero}.""",
        agent=dietician
    )
    initTasks.append(genDiet)

def generateWorkoutPlan(age, height, weight, superhero):
    genWorkout = Task(
        description=f"""Using the insights provided, develop a fully comprehensive workout plan that ecompasses exactly what the user needs to do to achieve their specified goals. The workout plan should be informative yet accessible, catering to a casual audience who does not know much about working out. The user is {age} years old, weighs {weight}lbs, and is {height} inches tall. Their superhero physique that they are hoping to achieve is {superhero}.""",
        agent=personalTrainer
    )
    initTasks.append(genWorkout)

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

    print(f"response is {response.choices[0].message.content}")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    chat("what can I do to be like you?", "Iron Man")
    plan = Crew(
        agents=[dietician, personalTrainer],
        tasks=initTasks,
        verbose=2
    )
    result = plan.kickoff()
    print(result)


