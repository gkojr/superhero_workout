const heroNames = ['batman', 'spider-man', 'superman', 'hulk', 'ironman']

$(document).ready(function() {

    //fix this to be done with id instead 
    heroNames.forEach(function(name) {  //maps the heroes given in the array onto the homescreen
        $.getJSON('/hero/' + name, function(data) {
            $.getJSON('/hero/' + name, function(data) {
                // Update the DOM with hero information
                const cardHtml = `
                    <div class="col hero-card-main" id=${data.id}" onclick="showHeroDetails('${data.id}')">
                        <img src="${data.image.url}" class="hero-img-main">
                        <h1 class="hero-name">${data.name}</h1>
                    </div>
                `;
                $('#cards-container').append(cardHtml);
            });
        });
    })

    function showHeroDetails(heroID) {
        window.location.href = `heroView.html?heroID=${heroId}`;
    }


});