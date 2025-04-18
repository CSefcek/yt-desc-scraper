import pandas as pd
import re
from googleapiclient.discovery import build

# Your YouTube API key
API_KEY = "Insert your YouTube Data API v3 key"

# Input and output Excel filenames
input_excel = 'input_videos.xlsx'
output_excel = 'video_descriptions.xlsx'

# Build YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Read URLs from Excel
df = pd.read_excel(input_excel)

# Function to extract video ID from URL
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", str(url))
    return match.group(1) if match else None

video_data = []
video_urls = df['url'].dropna().tolist()
video_ids = [extract_video_id(url) for url in video_urls if extract_video_id(url)]

# Fetch video data in chunks of 50 (API limit)
for i in range(0, len(video_ids), 50):
    chunk_ids = video_ids[i:i + 50]
    response = youtube.videos().list(
        part="snippet",
        id=",".join(chunk_ids)
    ).execute()

    for item in response['items']:
        vid = item['id']
        description = item['snippet']['description']
        title = item['snippet']['title']
        matched_url = next((url for url in video_urls if extract_video_id(url) == vid), '')
        video_data.append({
            'url': matched_url,
            'title': title,
            'description': description
        })

# Convert to DataFrame and save to Excel
output_df = pd.DataFrame(video_data)
output_df.to_excel(output_excel, index=False)

print(f"Descriptions saved to {output_excel}")
