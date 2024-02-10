from flask import Flask, render_template, jsonify
import requests

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

#@app.route('/hero/<name>')
def get_hero_data(name): 
    hero_id = get_hero_id(name);
    hero_data = get_hero_info(hero_id);
    return hero_data;

#print(get_hero_id('ironman'))
#doota = get_hero_info(69);
#print(doota['powerstats'])


def get_spiderman_intro():
    response = requests.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "format": "json",
        "titles": "Iron Man",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True
    }).json()
    
    intro_text = next(iter(response['query']['pages'].values()))['extract']
    
    # Return the first 500 characters of the intro text
    return intro_text[:600]

# Example usage
spiderman_intro = get_spiderman_intro()
print(spiderman_intro)



    