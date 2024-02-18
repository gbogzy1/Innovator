from itertools import count
import os
import wget
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from youtube_data import YouTubeTranscriptFetcher, TextAnalyser
from transformers import pipeline

# Loading env files
load_dotenv(find_dotenv())

Youtube_API_KEY = st.secrets["YTA_API_KEY"]
# Page title
st.set_page_config(page_title="AVA", page_icon=":robot_face:")
st.title("Truth Trace: Unveiling Transparency in Youtube Discourse")

st.subheader("Empower Accountability with Our Data App - summarise youtube videos with just one click to assess misinformation")

# Initialize st.session_state
if 'youtube_link' not in st.session_state:
    st.session_state.youtube_link = []


# Initialize Streamlit app
st.title("YouTube Transcript Summarizer")

# User Input
youtube_link = st.text_input("Enter YouTube video link:")

# Function to extract video ID from YouTube link
def extract_video_id(youtube_link):
    try:
        video_id = youtube_link.split("v=")[1]
        return video_id
    except IndexError:
        st.warning("Invalid YouTube link. Please enter a valid link.")
        return None

# Function to get transcript and summary
def process_youtube_link(youtube_link):
    video_id = extract_video_id(youtube_link)
    
    if video_id:
        try:
            # Fetch transcript
            yt_fetcher = YouTubeTranscriptFetcher(api_key=Youtube_API_KEY)
            txt_analysis = TextAnalyser()
            transcript = yt_fetcher.get_transcript(video_id)

            transcript = transcript.replace('.','.<eos>')
            transcript = transcript.replace('?','?<eos>')
            transcript = transcript.replace('!','!<eos>')

            # Display transcript
            st.write("Video Transcript Summary:")

            # Summarize transcript using Hugging Face's model
            summary = txt_analysis.summarise_text(max_len=120, min_len=30, text = transcript)

            # Display summary
            st.write(summary)

        except RuntimeError as e:
            st.warning(f"Error fetching transcript: {str(e)}")

# Process the YouTube link and display transcript/summary
if st.button("Process YouTube Link"):
    process_youtube_link(youtube_link)
