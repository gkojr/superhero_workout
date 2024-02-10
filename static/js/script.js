const heroNames = ['batman', 'spiderman', 'superman', 'wonderwoman', 'greenlantern']

$(document).ready(function() {

    function populateCards() {
        const cardContainer = document.getElementById("cards-container"); 
    
        cardsContainer.innerHTML = "";
    
        heroNames.forEach((heroName, index) => {
            const card = document.createElement("div");
            card.classList.add("card");
    
            //const img = 
        })
    
    }

    function getHeroData(name) { //gets the json info from the data
        $.getJSON('/hero/' + name, function(data) {
            
        })
    }













});