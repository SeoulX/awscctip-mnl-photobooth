const video = document.getElementById('video');
const captureBtn = document.getElementById('captureBtn');
const retakeBtn = document.getElementById('retakeBtn'); 
const capturedImage = document.getElementById('capturedImage');
const previewImage = document.getElementById('previewImage');
const retakePhotoBtn = document.getElementById('retakePhotoBtn');
const proceedBtn = document.getElementById('proceedBtn');
const previewModal = document.getElementById('previewModal');
let canvas;
// Access webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error("Error accessing camera:", error);
        // Consider displaying an error message to the user here
    });

captureBtn.addEventListener('click', () => {
    canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    // Show preview
    previewImage.src = canvas.toDataURL('image/png'); 
    previewModal.style.display = 'flex';

    // Hide other elements temporarily
    video.style.display = 'none';
    captureBtn.style.display = 'none';
});

retakePhotoBtn.addEventListener('click', () => {
    previewModal.style.display = 'none';
    video.style.display = 'block';
    captureBtn.style.display = 'block';
});

proceedBtn.addEventListener('click', () => {
    previewModal.style.display = 'none';

    let email = prompt("Please enter your email:");
    if (email && validateEmail(email)) { 
        const photoId = generateUniqueId(); 
        const presignedUrl = 'https://7h7g034k68.execute-api.ap-southeast-1.amazonaws.com/dev/awstipm-infosec/uploads';

        canvas.toBlob(blob => {  
            const targetWidth = 1280;
            const scaleFactor = targetWidth / canvas.width; 

            canvas.width = targetWidth;  
            canvas.height *= scaleFactor;

            canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
            fetch(buildUrl(presignedUrl, 'image_' + photoId + '.png'), {
                method: 'PUT',
                body: blob,
                headers: {
                    'Content-Type': 'image/png' 
                }
            })
            .then(response => {
                console.log('S3 Response:', response);

                if (!response.ok) {
                    throw new Error('S3 Upload Error');
                }

                s3Path = response.url;  // Assign path from response
                console.log('s3Path:', s3Path);

                return addItemToDynamoDB(photoId, email, s3Path); 
            })
            .then(() => {
                resetToInitialState(); 
                alert('Image stored and details added!');
            })
            .catch(error => {
                console.error('Error:', error); // Log errors thoroughly
                alert('There was an error. Please try again.');
            }); 
        }, 'image/png'); 
    } else {
        alert("Please enter a valid email.");
        previewModal.style.display = 'flex';
    }
});

function resetToInitialState() {
    video.style.display = 'block';
    captureBtn.style.display = 'block';
    document.getElementById('imageAndButtonContainer').style.display = 'none'; 
    previewModal.style.display = 'none'; 
}
function validateEmail(email) {
    return email.includes('@') && email.includes('.');
}
function generateUniqueId() {
    const timestamp = Date.now().toString();
    const randomPart = Math.floor(Math.random() * 1000);
    return Number(timestamp + randomPart);
}
function buildUrl(presignedUrl, filename) {
    return `${presignedUrl}/${filename}`;
}
async function addItemToDynamoDB(photoId, email, photoPath) {
    try {
        const response = await fetch('https://js85ilg935.execute-api.ap-southeast-1.amazonaws.com/does/add', {
            method: 'POST',
            headers: {
               "Content-Type": "application/json" 
            },
            body: JSON.stringify({
                'photoId': photoId,
                'email': email,
                "photoEditPath": '', // Adjust if needed 
                'photoPath': photoPath,
                'status': false 
            })
        });

        if (!response.ok) {
            throw new Error(`DynamoDB API error: ${response.status}`); 
        }

        return { success: true }; // Indicate success

    } catch (error) {
        console.error('Error adding item:', error);
        return { success: false, error: error.message }; // Return error details
    }
}