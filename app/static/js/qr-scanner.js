document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded');

    const video = document.getElementById('video');

    // Request access to the camera
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream; // Set the video stream to the video element

            console.log('Camera access granted and streaming...');

            // Initialize Instascan
            let scanner = new Instascan.Scanner({ video: video });

            // When a QR code is scanned
            scanner.addListener('scan', (content) => {
                console.log('Scanned QR Code:', content);

                let data;
                try {
                    data = JSON.parse(content);
                } catch (error) {
                    console.error('Invalid QR Code format:', error);
                    return Swal.fire({
                        icon: 'error',
                        title: 'Invalid QR Code!',
                        text: 'The scanned code is not in a valid format.',
                        timer: 1500,
                        showConfirmButton: false
                    });
                }

                console.log('Type of scanned data:', typeof content);
                console.log('Type of parsed data:', typeof data);

                Swal.fire({
                    icon: 'success',
                    title: 'QR Code Scanned!',
                    text: `Data: ${content}`,
                    timer: 1500,
                    showConfirmButton: false
                });

                sendQRCodeToAPI(data);
            });

            // Start scanning for QR codes using the first available camera
            Instascan.Camera.getCameras()
                .then((cameras) => {
                    if (cameras.length > 0) {
                        scanner.start(cameras[0]); // Use the first camera
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'No cameras found!',
                            text: 'Please connect a camera and try again.'
                        });
                    }
                })
                .catch((error) => {
                    console.error('Error getting cameras:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Camera Error!',
                        text: 'Error accessing camera devices.',
                        timer: 2000,
                        showConfirmButton: false
                    });
                });

        })
        .catch((error) => {
            console.error('Error accessing the camera:', error.name, error.message);

            Swal.fire({
                icon: 'error',
                title: 'Camera Access Denied!',
                text: `Error: ${error.name} - ${error.message}`,
                timer: 2000,
                showConfirmButton: false
            });

            // Replace video with a fallback image if camera access fails
            const image = document.createElement('img');
            image.src = 'static/img/capture.png';
            image.alt = 'Camera access denied';
            image.style.width = '100%';

            video.replaceWith(image);
        });
});

function sendQRCodeToAPI(qrData) {
    fetch('/api/generate_qr_code-code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ qr_code: qrData }) // Send QR data as JSON
    })
    .then(response => {
        if (!response.ok) {
            // If response status is not 2xx, throw an error
            return response.json().then(err => { throw new Error(err.message || "Failed to process request"); });
        }
        return response.json();
    })
    .then(data => {
        console.log('Server Response:', data);
        Swal.fire({
            icon: 'success',
            title: 'Success!',
            text: data.message,
            timer: 1500,
            showConfirmButton: false
        });
    })
    .catch(error => {
        console.error('Error sending QR Code:', error);
        Swal.fire({
            icon: 'error',
            title: 'Failed to Send!',
            text: error.message || 'Failed to send QR code to the server.',
            timer: 1500,
            showConfirmButton: false
        });
    });
}

