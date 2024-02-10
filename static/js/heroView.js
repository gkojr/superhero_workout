// Get heroId from URL
var heroId = window.location.pathname.split('/').pop();
//alert(heroId);


$(document).ready(function() {

    //get hero name and get the image for the hero
    $.getJSON('/heroID/' + heroId, function(data) {
        //get name and use for title
        //const heroName = data.name;
        //alert(heroName);
        const heroName = data.name; 
        $('#hero-name').text(heroName);
        $('#chat').text("Chat with " + heroName);


        var heroImageUrl = data.image.url;
        //alert(heroImageUrl);
        // Update the src attribute of the "hero-image" img element
        $('#hero-img').attr('src', heroImageUrl);

        $.getJSON('/workout/' + heroName + '/' + 12 + '/' + 72 + '/' + 180 + '/' + false, function(data) {
            $('#hero-description').text(data);
        })

        function showWorkout(heroID) {
            //window.location.href = `workout.html?heroID=${heroId}`;
            // Get reference to the div
            var div = document.getElementById('workout');
            // Display text in the div
            $.getJSON('/workout/' + heroName + '/' + 12 + '/' + 72 + '/' + 180 + '/' + false, function(data) {
                //$('.hero-description').text(data);
                const workout = data; 
                div.textContent = workout;
                div.style.display = 'block'; // Show the div
            })
            
        }
    
        function showDietPlan(heroID) {
            //window.location.href = `diet.html?heroID=${heroId}`;
            var div = document.getElementById('diet');
            // Display text in the div
            $.getJSON('/diet/' + heroName + '/' + 12 + '/' + 72 + '/' + 180 + '/' + false, function(data) {
                //$('.hero-description').text(data);
                const workout = data; 
                div.textContent = workout;
                div.style.display = 'block'; // Show the div
            })
        }



        //get the description for the hero
        /*$.getJSON('/description/' + heroName, function(data) {
            //$('.hero-description').text("hello");
            alert("hello");
        })*/

    })


});