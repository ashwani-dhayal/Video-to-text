import requests
import time
import json
import os

# Your AssemblyAI API key
api_key = "1ed1f96bcb4441038ce128a5919d6d9c"

# Set up the headers with your API key
headers = {
    "authorization": api_key,
    "content-type": "application/json"
}

# Function to upload the file to AssemblyAI
def upload_file(file_path):
    print("Uploading file...")
    
    # Open the file in binary mode
    with open(file_path, "rb") as f:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers={"authorization": api_key},
            data=f
        )
    
    if response.status_code == 200:
        return response.json()["upload_url"]
    else:
        print(f"Error uploading file: {response.text}")
        return None

# Function to transcribe the uploaded file
def transcribe_file(upload_url):
    print("Submitting file for transcription...")
    
    # Set up the payload with the upload URL
    data = {
        "audio_url": upload_url
    }
    
    # Submit the file for transcription
    response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print(f"Error submitting file for transcription: {response.text}")
        return None

# Function to get the transcription result
def get_transcription(transcript_id):
    print("Waiting for transcription to complete...")
    
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    
    while True:
        response = requests.get(polling_endpoint, headers=headers)
        response_json = response.json()
        
        if response_json["status"] == "completed":
            print("Transcription completed!")
            return response_json["text"]
        elif response_json["status"] == "error":
            print(f"Transcription error: {response_json['error']}")
            return None
        else:
            print(f"Transcription status: {response_json['status']}")
            time.sleep(5)  # Wait 5 seconds before checking again

# Main function to convert MP4 to text
def mp4_to_text(file_path, output_file=None):
    # Upload the file
    upload_url = upload_file(file_path)
    if not upload_url:
        return
    
    # Submit for transcription
    transcript_id = transcribe_file(upload_url)
    if not transcript_id:
        return
    
    # Get the transcription result
    transcription = get_transcription(transcript_id)
    if not transcription:
        return
    
    # Save the transcription to a file if specified
    if output_file:
        with open(output_file, "w") as f:
            f.write(transcription)
        print(f"Transcription saved to {output_file}")
    
    return transcription

# Create necessary directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("transcriptions", exist_ok=True)

# Example usage
if __name__ == "__main__":
    video_filename = input("Enter the name of your MP4 file in the uploads folder: ")
    video_file = os.path.join("uploads", video_filename)
    
    if not os.path.exists(video_file):
        print(f"Error: File {video_file} does not exist")
    else:
        # Create output filename based on input filename
        output_filename = os.path.splitext(video_filename)[0] + ".txt"
        output_file = os.path.join("transcriptions", output_filename)
        
        transcription = mp4_to_text(video_file, output_file)
        if transcription:
            print("\nTranscription preview:")
            print(transcription[:500] + "..." if len(transcription) > 500 else transcription)
