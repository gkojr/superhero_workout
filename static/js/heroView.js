function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

// Get heroId from URL
var heroId = getParameterByName('heroId');

$(document).ready(function() {

    $.getJSON('/hero/' + heroId, function(data) {
        //get name and use for title
        var heroName = data.name;
        $('.hero-title').text(heroName);

        var heroImageUrl = data.imageUrl;
        // Update the src attribute of the "hero-image" img element
        $('.hero-image').attr('src', heroImageUrl);
    })

    function showWorkout(heroID) {
        window.location.href = `workout.html?heroID=${heroId}`;
    }

    function showDietPlan(heroID) {
        window.location.href = `diet.html?heroID=${heroId}`;
    }






});