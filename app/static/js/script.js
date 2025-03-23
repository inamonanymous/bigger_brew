// script.js - Responsible for all JavaScript functionalities in the project

document.addEventListener("DOMContentLoaded", function () {
    const addEmployeeButton = document.getElementById("create-user");

    if (addEmployeeButton) {
        addEmployeeButton.addEventListener("click", function (event) {
            event.preventDefault();
            showAddEmployeeForm();
        });
    }

    formatAllDates();
});

function formatAllDates() {
    document.querySelectorAll(".format-date").forEach((element) => {
        let rawDate = element.innerText.trim();
        let formattedDate = formatDate(rawDate);
        console.log("before", element.innerText);
        element.innerText = formattedDate;
        console.log("after", element.innerText);
    });
}

function formatDate(dateString) {
    let date = new Date(dateString);
    if (isNaN(date)) return dateString; // Return original if invalid
    return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true, // Ensures AM/PM format
    });
}

function showAddEmployeeForm() {
    Swal.fire({
        title: "Add Employee",
        html: `
            <form id="add-employee-form" class="needs-validation" novalidate>
                <div class="container">
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">Firstname</label>
                            <input type="text" class="form-control" name="firstname" placeholder="Enter Firstname" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Middlename</label>
                            <input type="text" class="form-control" name="middlename" placeholder="Enter Middlename">
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label">Lastname</label>
                            <input type="text" class="form-control" name="lastname" placeholder="Enter Lastname" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Suffix</label>
                            <input type="text" class="form-control" name="suffix" placeholder="Enter Suffix">
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-control" name="username" placeholder="Enter Username" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" name="email" placeholder="Enter Email" required>
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-12">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" placeholder="Enter Password" required>
                        </div>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary mt-3 w-100">Submit</button>
            </form>
        `,
        showCancelButton: true,
        showConfirmButton: false,
        didOpen: () => {
            document.getElementById("add-employee-form").addEventListener("submit", submitCustomerForm);
        }
    });
}

function submitCustomerForm(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    console.log("clicked cliecked");
    fetch("/create-user", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        Swal.fire("Success", "Customer added successfully!", "success");
    })
    .catch(error => {
        Swal.fire("Error", "An unexpected error occurred.", "error");
    });
}
