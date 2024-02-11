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
    var userId = document.getElementById('user_id').value;

    // Do something with the form data, such as sending it to a server
    const metadata = 
    {
        "age": age,
        "height": height,
        "weight": weight
    }

    console.log(metadata);

    fetch('/update_metadata', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            metadata: metadata
        })
    })
    .then(response => {
        if (response.ok) {
            console.log('User metadata updated successfully');
        } else {
            console.error('Failed to update user metadata:', response.statusText);
        }
    })
    .catch(error => {
        console.error('Error updating user metadata:', error);
    });

    

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

