import requests
import cv2

def upload_to_s3(base_url, bucket, folder, filename, file_data):
    url = base_url + bucket + '/' + folder + '/' + filename  # Corrected: added '/'
    files = {'file': (filename, file_data)} 

    response = requests.put(url, files=files) 

    if response.status_code == 200:
        print('File uploaded successfully')
    else:
        print('Upload failed', response.text)

def capture_save_and_upload():
    camera = cv2.VideoCapture(0)  
    success, frame = camera.read()

    if not success:
        print("Could not access the camera")
        return

    # Show a preview window (optional)
    cv2.imshow("Captured Image", frame)

    # Save the image
    filename = 'capture.png'
    cv2.imwrite(filename, frame)

    camera.release()  # Release camera resource
    cv2.destroyAllWindows()  # Close the preview window if it was used

    # Upload to S3
    base_url = 'https://7h7g034k68.execute-api.ap-southeast-1.amazonaws.com/dev/'
    bucket = 'awstipm-infosec'
    folder = 'uploads'

    with open(filename, 'rb') as f:
        file_data = f.read()

    upload_to_s3(base_url, bucket, folder, filename, file_data) 

if __name__ == "__main__":
    capture_save_and_upload()

