const heroNames = ['batman', 'spider-man', 'superman', 'hulk', 'ironman']

function showHeroDetails(heroID) {
    //window.location.href = `heroView`;
    //<a href="/heroView">About Page</a>
    //alert("hello");
}

$(document).ready(function() {

  
    //fix this to be done with id instead 
    heroNames.forEach(function(name) {  //maps the heroes given in the array onto the homescreen
        $.getJSON('/hero/' + name, function(data) {
            $.getJSON('/hero/' + name, function(data) {
                // Update the DOM with hero information
                const cardHtml = `
                    <a href="/heroView/${data.id}">
                    <div class="col hero-card-main" id=${data.id}" onclick="showHeroDetails('${data.id}')">
                        <img src="${data.image.url}" class="hero-img-main">
                        <h1 class="hero-name">${data.name}</h1>
                    </div>
                    </a>
                `;
                $('#cards-container').append(cardHtml);
            });
        });
    })

   


});