const heroIDS = [69, 620, 644, 332, 732, 720, 106, 38, 149, 579, 714, 275]

function showHeroDetails(heroID) {
    //window.location.href = `heroView`;
    //<a href="/heroView">About Page</a>
    //alert("hello");
}

$(document).ready(function() {

  
    //fix this to be done with id instead 
    heroIDS.forEach(function(id) {  //maps the heroes given in the array onto the homescreen
            $.getJSON('/heroID/' + id, function(data) {
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
        
    })

   


});