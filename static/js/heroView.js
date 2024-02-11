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
    button.innerHTML+="Send";
    inputElement.type = "text"; // Set input type to text

    // Replace the content of the div with the input element
    contentDiv.innerHTML = ""; // Clear existing content
    contentDiv.appendChild(inputElement); // Append the input element
    contentDiv.appendChild(button);


    button.onclick = function() {
        //alert("test!");
        var characterText = document.getElementById("chat-text-response");
        var response = inputElement.value;
        response = response.replace('?', '');        
        
        
        characterText.innerHTML = "Typing...";

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
    userId = document.getElementById('user_id')
    //get hero name and get the image for the hero
    $.getJSON('/heroID/' + heroId, function(data) {
        //get name and use for title
        //const heroName = data.name;
        //alert(heroName);
        const heroName = data.name; 
        $('#hero-name').text(heroName);
        $('#chat').text("Chat with " + heroName);
        $('#dietButton').text("Get the " + heroName + " Diet");
        $('#workoutButton').text("Get the " + heroName + " Workout");



        var heroImageUrl = data.image.url;
        //alert(heroImageUrl);
        // Update the src attribute of the "hero-image" img element
        $('#hero-img').attr('src', heroImageUrl);


        $.getJSON('/description/' + heroName, function(data) {
            $('#hero-description').text(data);
        })
        
        if(userId != null) {
            userId = userId.value;
            $.getJSON('/workout/' + heroName + '/' + userId + '/' + "False", function(data) {
                $('#workout-body').text(data);
            })

            $.getJSON('/diet/' + heroName + '/' + userId + '/' + "False", function(data) {
                $('#diet-body').text(data);
            })
        } else {
            //default values
            $('#workout-body').text("Unable to retrieve a workout plan at the moment. Please login first.");
            $('#diet-body').text("Unable to retrieve a diet plan at the moment. Please login first.");
        }
    })
});