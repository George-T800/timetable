function addClass(day) {
    // Get the input fields for the class name and time
    const input = document.getElementById(`${day}-input`);
    const time = document.getElementById(`${day}-time`);
    const list = document.getElementById(`${day}-list`);

    // Get the values from the input fields
    const className = input.value;
    const classTime = time.value;

    // If the input is not empty, create a new list item
    if (className.trim() !== "" && classTime.trim() !== "") {
        const listItem = document.createElement('li');
        listItem.innerHTML = `${classTime} - ${className} 
                              <button onclick="modifyClass(this, '${day}')">Modify</button>
                              <button onclick="removeClass(this)">Remove</button>`;

        // Append the new list item to the corresponding day's list
        list.appendChild(listItem);

        // Clear the input fields after adding the class
        input.value = '';
        time.value = '';
    }
}

function removeClass(button) {
    // Remove the <li> element containing the class details
    const listItem = button.parentElement;
    listItem.remove();
}

function modifyClass(button, day) {
    // Get the <li> element containing the class details
    const listItem = button.parentElement;

    // Extract the time and class name from the list item
    const [time, className] = listItem.textContent.split(' - ');

    // Set the extracted values back to the input fields
    document.getElementById(`${day}-input`).value = className.replace("ModifyRemove", "").trim();
    document.getElementById(`${day}-time`).value = time.trim();

    // Remove the current item so it can be replaced with the updated one
    listItem.remove();
}
