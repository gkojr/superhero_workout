// Get heroId from URL
var heroId = window.location.pathname.split('/').pop();
//alert(heroId);

function showChatBox() {
    var contentDiv = document.getElementById("chat-text-box");

    // Create an input element
    var inputElement = document.createElement("textarea");
    inputElement.id = "chatBox";
    var button = document.createElement("button")
    button.id = "chatButton";
    inputElement.type = "text"; // Set input type to text

    // Replace the content of the div with the input element
    contentDiv.innerHTML = ""; // Clear existing content
    contentDiv.appendChild(inputElement); // Append the input element
    contentDiv.appendChild(button);

    button.onclick = function() {
        //alert("test!");
        var characterText = document.getElementById("chat-text-response");
        var response = inputElement.value;
        //alert(response);
        characterText.innerHTML = "Loading...";

        $.getJSON('/heroID/' + heroId, function(data) {
            const heroName = data.name; 
            $.getJSON('/chat/' + response + '/' + heroName, function(data) {
                $('#chat-text-response').text(data);
                //console.log(data);
            })
    })
    
        


    }
}

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


        $.getJSON('/description/' + heroName, function(data) {
            $('#hero-description').text(data);
        })

        $.getJSON('/workout/' + heroName + '/' + 12 + '/' + 72 + '/' + 180 + '/' + "False", function(data) {
            //$('.hero-description').text(data);
            $('#workout-body').text(data);
        })

        $.getJSON('/diet/' + heroName + '/' + 12 + '/' + 72 + '/' + 180 + '/' + "False", function(data) {
            //$('.hero-description').text(data);
            $('#diet-body').text(data);
        })

        

        function showWorkout(heroID) {
            //window.location.href = `workout.html?heroID=${heroId}`;
            // Get reference to the div
            var div = document.getElementById('workout');
            // Display text in the div
            $.getJSON('/workout/' + heroName + '/' + 12 + '/' + 72 + '/' + 180 + '/' + "False", function(data) {
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
            $.getJSON('/diet/' + heroName + '/' + 12 + '/' + 72 + '/' + 180 + '/' + "False", function(data) {
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