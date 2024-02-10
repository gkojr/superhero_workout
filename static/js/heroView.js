// Get heroId from URL
var heroId = window.location.pathname.split('/').pop();
//alert(heroId);

$(document).ready(function() {

    //get hero name and get the image for the hero
    $.getJSON('/heroID/' + heroId, function(data) {
        //get name and use for title
        const heroName = data.name;
        alert(heroName);
        $('.hero-title').text(heroName);

        var heroImageUrl = data.imageUrl;
        // Update the src attribute of the "hero-image" img element
        $('.hero-image').attr('src', heroImageUrl);
    })

    //get the description for the hero
    $.getJSON('/description/' + heroName, function(data) {
        $('.hero-description').text("hello");
    })

    function showWorkout(heroID) {
        //window.location.href = `workout.html?heroID=${heroId}`;
        // Get reference to the div
        var div = document.getElementById('workout');
        // Display text in the div
        $.getJSON('/workout/' + heroName, function(data) {
            //$('.hero-description').text(data);
            const workout = data; 
        })
        div.textContent = workout;
        div.style.display = 'block'; // Show the div
    }

    function showDietPlan(heroID) {
        //window.location.href = `diet.html?heroID=${heroId}`;
    }

});