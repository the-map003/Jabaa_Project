// JavaScript code for handling form submission

document.addEventListener("DOMContentLoaded", function () {
  const addCitizenForm = document.getElementById("addCitizenForm");

  addCitizenForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const fullName = document.getElementById("fullName").value;
    const dob = document.getElementById("dob").value;
    const gender = document.getElementById("gender").value;
    const age = document.getElementById("age").value;
    const contact = document.getElementById("contact").value;
    const address = document.getElementById("address").value;

    // For now, just log the form data to the console
    console.log({
      fullName,
      dob,
      gender,
      age,
      contact,
      address,
    });

    // Here you could add further logic to send the data to a backend server
    alert("Citizen registered successfully!");
  });
});
