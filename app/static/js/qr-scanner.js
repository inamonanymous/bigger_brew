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
                alert(`Scanned QR Code: ${content}`);
                let data = JSON.parse(content);
                console.log('Type of scanned data:', typeof content);
                console.log('Type of parsed data:', typeof data);
                sendQRCodeToAPI(data);
            });

            // Start scanning for QR codes using the first available camera
            Instascan.Camera.getCameras()
                .then((cameras) => {
                    if (cameras.length > 0) {
                        scanner.start(cameras[0]); // Use the first camera
                    } else {
                        alert('No cameras found.');
                    }
                })
                .catch((error) => {
                    console.error('Error getting cameras:', error);
                    alert('Error accessing camera devices.');
                });

        })
        .catch((error) => {
            console.error('Error accessing the camera:', error.name, error.message);
            alert(`Camera error: ${error.name} - ${error.message}`);

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
    .then(response => response.json()) // Convert response to JSON
    .then(data => {
        console.log('Server Response:', data);
        alert(data.message); // Show success or error message
    })
    .catch(error => {
        console.error('Error sending QR Code:', error);
        alert('Failed to send QR code to the server.');
    });
}