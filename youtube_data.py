import textwrap
import numpy as np
import pandas as pd
from pprint import pprint
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi as yta
from youtube_transcript_api.formatters import TextFormatter

# Import pipeline function
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


class YouTubeTranscriptFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_videos(self, query, max_results=5):
        search_response = self.youtube.search().list(
            q=query,
            type='video',
            part='id,snippet',
            maxResults=max_results,
            regionCode='GB'
        ).execute()
        ids = [item['id']['videoId'] for item in search_response['items']]
        return ids

    def get_transcript(self, video_id):
        try:
            transcript = yta.get_transcript(video_id)
            formatter = TextFormatter()
            formatted_transcript = formatter.format_transcript(transcript)
            return formatted_transcript
        except Exception as e:
            # Raise an exception with the error message
            raise RuntimeError(f"Error fetching transcript: {str(e)}")

class TextAnalyser:
    def __init__(self):
        pass

    def wrap(self, x):
        """
      :param x: text
      :return: the function will try to wrap sentences at a period (.) if possible.

      """

        return textwrap.fill(x, replace_whitespace=False, fix_sentence_endings=True)

    def summarise_text(self, max_len, min_len, text):
        # Split the text into chunks of max 500 tokens - to avoid Index error for max length reached.
        sentences = text.split('<eos>')
        max_chunk = 500
        current_chunk = 0 
        chunks = []
        for sentence in sentences:
            if len(chunks) == current_chunk + 1: 
                if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                    chunks[current_chunk].extend(sentence.split(' '))
                else:
                    current_chunk += 1
                    chunks.append(sentence.split(' '))
            else:
                print(current_chunk)
                chunks.append(sentence.split(' '))

        for chunk_id in range(len(chunks)):
            chunks[chunk_id] = ' '.join(chunks[chunk_id])

        # Summarize each chunk and load back into text.
        summaries = summarizer(chunks, max_length=max_len, min_length=min_len, do_sample=False)
        print(summaries)
        summary_texts = summaries[0]

        # Concatenate the summaries
        return ' '.join([summary['summary_text'] for summary in summaries])

yt = YouTubeTranscriptFetcher('AIzaSyA5bVbQyryIq9TZFD9YfWSz-ubGcVR29so')

