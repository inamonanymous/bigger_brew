document.addEventListener('DOMContentLoaded', () => {
    $(document).ready(function () {
        $('#inventoryTable').DataTable({
            "order": [[0, "asc"]], // Sort by first column (Item Name)
            "paging": true,  // Enable pagination
            "searching": true,  // Enable search
            "info": true,  // Show info text
            "lengthMenu": [5, 10, 25, 50]  // Dropdown for rows per page
        });
    });




    document.querySelectorAll('[data-modal-btn]').forEach(button => {
        const modalId = button.getAttribute('data-modal-btn');
        const modal = document.getElementById(modalId);

        if (modal) {
            // Open modal
            button.addEventListener('click', () => {
                // Close any open modal first
                document.querySelectorAll('.modal').forEach(m => {
                    m.style.display = "none";
                });

                // Open the clicked modal
                modal.style.display = "flex";

                // Add class to body to block background interaction
                document.body.classList.add('modal-open');
            });

            // Close modal when clicking the close button
            const closeButton = modal.querySelector('.close');
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    modal.style.display = "none";

                    // Remove class from body to allow background interaction
                    document.body.classList.remove('modal-open');
                });
            }

            // Close modal when clicking outside
            window.addEventListener('click', (event) => {
                if (event.target === modal) {
                    modal.style.display = "none";

                    // Remove class from body to allow background interaction
                    document.body.classList.remove('modal-open');
                }
            });
        }
    });


    document.querySelectorAll(".btn.action.delete-item").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default link behavior

            let itemId = this.getAttribute("data-value"); // Extract item_id from button

            Swal.fire({
                title: "Are you sure?",
                text: "You won't be able to revert this!",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Yes, delete it!",
                cancelButtonText: "Cancel"
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/manage-items/${itemId}`, {
                        method: "DELETE",
                        headers: { "Content-Type": "application/json" }
                    })
                    .then(res => {
                        if (!res.ok) {
                            return res.json().then(err => { throw new Error(err.message); });
                        }
                        return res.json();
                    })
                    .then(response => {
                        Swal.fire("Deleted!", response.message, "success").then(() => location.reload());
                    })
                    .catch(error => {
                        Swal.fire("Error!", error.message || "Failed to delete item.", "error");
                    });
                }
            });
        });
    });


    document.querySelectorAll(".edit-item").forEach(button => {
        button.addEventListener("click", function () {
            let itemId = this.getAttribute("data-value");

            // Get existing values from table
            let row = this.closest("tr");
            let itemName = row.cells[0].textContent.trim();
            let itemDescription = row.cells[1].textContent.trim();
            let itemPrice = row.cells[3].textContent.replace("₱: ", "").trim();
            let itemMeasurement = row.cells[5].textContent.trim();

            // SweetAlert Form
            Swal.fire({
                title: "Edit Item",
                html: `
                    <input id="swal-item-name" class="swal2-input" placeholder="Item Name" value="${itemName}">
                    <input id="swal-item-description" class="swal2-input" placeholder="Description" value="${itemDescription}">
                    <input id="swal-item-price" type="number" class="swal2-input" placeholder="Price" value="${itemPrice}">
                    <input id="swal-item-measurement" class="swal2-input" placeholder="Measurement" value="${itemMeasurement}">
                `,
                focusConfirm: false,
                showCancelButton: true,
                confirmButtonText: "Save Changes",
                preConfirm: () => {
                    return {
                        item_name: document.getElementById("swal-item-name").value,
                        item_description: document.getElementById("swal-item-description").value,
                        item_price: document.getElementById("swal-item-price").value,
                        item_measurement: document.getElementById("swal-item-measurement").value
                    };
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    let updatedData = result.value;
                    
                    // Send AJAX request to update item
                    fetch(`/edit-item-details/${itemId}`, {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(updatedData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire("Success!", "Item updated successfully.", "success").then(() => {
                                location.reload(); // Reload to reflect changes
                            });
                        } else {
                            Swal.fire("Error", data.message, "error");
                        }
                    })
                    .catch(() => Swal.fire("Error", "Something went wrong!", "error"));
                }
            });
        });
    });

    document.querySelectorAll(".btn.action.edit-quantity").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default link behavior

            let itemId = this.getAttribute("data-value"); // Extract item_id from URL
            console.log("item id:", itemId)
            // Fetch item details from the backend
            fetch(`/manage-items/${itemId}`)
                .then(response => response.json())
                .then(data => {
                    Swal.fire({
                        title: `Manage Item: ${data.item_name}`,
                        html: `
                            <table style="width:100%; text-align:left;">
                                <tr><th>Item Name:</th><td>${data.item_name}</td></tr>
                                <tr><th>Category:</th><td>${data.category_name}</td></tr>
                                <tr><th>Description:</th><td>${data.item_description}</td></tr>
                                <tr><th>Stock:</th><td id="stock-count">${data.item_stock}</td></tr>
                                <tr><th>Added At:</th><td>${data.added_at}</td></tr>
                                <tr><th>Updated At:</th><td>${data.updated_at}</td></tr>
                            </table>
                            <br>
                            <input id="quantity" type="number" class="swal2-input" placeholder="Enter Quantity">
                        `,
                        showCancelButton: true,
                        confirmButtonText: "Increase Stock",
                        denyButtonText: "Decrease Stock",
                        showDenyButton: true,
                        preConfirm: () => {
                            let quantity = document.getElementById("quantity").value;
                            if (!quantity || quantity <= 0) {
                                Swal.showValidationMessage("Enter a valid quantity.");
                                return false;
                            }
                            return { quantity, action: "increase" };
                        },
                        preDeny: () => {
                            let quantity = document.getElementById("quantity").value;
                            if (!quantity || quantity <= 0) {
                                Swal.showValidationMessage("Enter a valid quantity.");
                                return false;
                            }
                            return { quantity, action: "decrease" };
                        }
                    }).then(result => {
                        if (result.isConfirmed || result.isDenied) {
                            let actionType = result.isConfirmed ? "increase" : "decrease";

                            // Send request to update stock
                            fetch("/update-item", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    item_id: data.item_id,
                                    item_quantity: result.value.quantity,
                                    action_type: actionType
                                })
                            })
                            .then(res => {
                                if (!res.ok) {
                                    return res.json().then(err => { throw new Error(err.message); });
                                }
                                return res.json();
                            })
                            .then(response => {
                                Swal.fire("Success!", response.message, "success").then(() => location.reload());
                            })
                            .catch(error => {
                                Swal.fire("Error!", error.message || "Failed to update stock.", "error");
                            });
                        }
                    });
                })
                .catch(error => {
                    Swal.fire("Error!", "Failed to fetch item details.", "error");
                });
        });
    });

});
