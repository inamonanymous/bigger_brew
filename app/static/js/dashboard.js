document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("employeeModal");
    const openBtn = document.getElementById("open-add-employee-modal");
    const closeBtn = document.getElementById("closeModal");

    openBtn.addEventListener("click", function () {
        modal.style.display = "block"; // Show the modal
        console.log('open')
    });

    closeBtn.addEventListener("click", function () {
        modal.style.display = "none"; // Hide the modal
    });

    // Close modal if user clicks outside of it
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

});