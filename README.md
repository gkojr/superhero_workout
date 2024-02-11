## The Team
Our front-end developer, Sean Malavet. Taking care of the middleware is George Owusu, and finally handling the backend is Jean-Guy Leconte.

## Inspiration
_Healthy Heroes_ was inspired by a drive to inspire people to be active and a love for comic book superheroes. Our web application combines these two objectives into one cohesive experience. 

## What it does
_Healthy Heroes_ allows users to enter their information such as age, weight, and height to get a personalized workout and diet plan. However, what's special about these plans is that they are tailored to get you into the physique of your chosen hero. You can also ask your selected hero any question, and they'll respond with a response fitting for that hero. 

## How we built it
Our web application is built on Flask, a lightweight web framework for Python. The front end was built using HTML and JavaScript, wrapped with Bootstrap CSS. We used the Python backend to make calls to the OpenAI API for the generated diet, workout, and chat responses. Additionally, we also used the Auth0 API to easily have authenticated user accounts with saved user information. The Superhero API was called to generate all the data on the different heroes. Finally, we used JavaScript and jQuery to make calls to the Python backend and bring the backend data to the front end and vice versa. 


## Challenges we ran into
During our project, we ran into three major challenges. Our first and biggest challenge was attempting to get the authorization and user accounts to work. After looking through a lot of documentation, we were 
able to find all the correct endpoints and the correct POST request to get the accounts and metadata working. Another challenge we ran into was trying to correctly format the API endpoints in JavaScript so that we could correctly get the data from the Python endpoints. In order to do this, we had to learn to use jQuery, and that was a fairly steep learning curve that required us to look up a lot of new information. On the front end, ensuring that our site was responsive and functional on both mobile and desktop screen widths was an important challenge. We wanted to make sure that our site looked great no matter how you chose to view it. The amount of people who access the internet via their phones rather than a desktop is a constantly increasing number, so good mobile support is essential. To accomplish this, we used Bootstrap and breakpoints to have it change depending on the screen size.

## Accomplishments that we're proud of
We're incredibly proud of our functional authorization, responsive desktop and mobile view, and the detailed AI-generated responses we received from well-crafted OpenAI API prompts. 

## What we learned
While we learned about the new technologies we used along the way, we believe the biggest takeaway from this project is how to effectively work together, plan, and communicate as a team. We all worked on different parts of the project, but these parts (frontend, middleware, backend) all greatly intertwined with each other, so if we did not have a good system in place to keep up with each other's work, we would have ended up running into far more obstacles than we already did. 

## What's next for Healthy Heroes
In the future, we would love to increase security and user privacy. Additionally, we plan on adding a tracking feature so that you can track your daily exercise and the food you eat. Finally, if possible, we could expand into a more general self-help application rather than being specific to diet and exercise. 
