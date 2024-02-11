function editInformation() {
    // Get elements
    var information = document.getElementById("information");
    var inputForm = document.getElementById("inputForm");

    // Hide information, show form
    information.style.display = "none";
    inputForm.style.display = "block";
}

function submitForm() {
    // Get form data
    var age = document.getElementById("age").value;
    var height = document.getElementById("height").value;
    var weight = document.getElementById("weight").value;

    // Do something with the form data, such as sending it to a server
    const metaData = 
    {
        "age": age,
        "height": height,
        "weight": weight
    }

    console.log(metaData);

    // For demonstration, log the form data to the console
    //console.log("Age:", age);
    //console.log("Height (inches):", height);
    //console.log("Weight (pounds):", weight);

    // Update displayed information
    document.getElementById("displayAge").textContent = age;
    document.getElementById("displayHeight").textContent = height;
    document.getElementById("displayWeight").textContent = weight;

    // Hide form, show information
    document.getElementById("information").style.display = "block";
    document.getElementById("inputForm").style.display = "none";

    // Clear form fields
    document.getElementById("age").value = "";
    document.getElementById("height").value = "";
    document.getElementById("weight").value = "";
}
