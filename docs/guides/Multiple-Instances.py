# Requirements:
# pip install groq soundfile nltk
# For Windows users, set your API key in the terminal with:
#   set GROQ_API_KEY=your-api-key-here
# Or in PowerShell:
#   $env:GROQ_API_KEY="your-api-key-here"
# You can also set it below for testing only (not recommended for production).

import os
import re
import soundfile as sf
from pathlib import Path
from nltk.sentiment import SentimentIntensityAnalyzer
from groq import Groq
# --- Optional: Set your API key here for testing only ---
# Uncomment and set your key if you want to hardcode it (not recommended for production)
os.environ["GROQ_API_KEY"] = "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"

# --- Optional: Override Groq API endpoint (rarely needed) ---
# client = Groq(base_url="https://api.groq.com/openai/v1")
# Otherwise, just use:
client = Groq()

# List of keywords to detect (you can expand this list)
profanity_keywords = ['fuck', 'shit', 'bitch', 'asshole', 'pussy']
# You can add moan_keywords if needed, e.g. moan_keywords = ['moan', ...]
moan_keywords = []

def remove_duplicate_phrases(text):
    sentences = text.split('. ')
    cleaned_sentences = []
    for i, sentence in enumerate(sentences):
        if i == 0 or sentence != sentences[i - 1]:
            cleaned_sentences.append(sentence)
    cleaned_text = '. '.join(cleaned_sentences)
    return cleaned_text

def highlight_keywords(text, keywords, highlight_color='red'):
    for keyword in keywords:
        text = re.sub(f'\\b{keyword}\\b', f'\033[1;31m{keyword}\033[0m', text, flags=re.IGNORECASE)
    return text

def transcribe_and_analyze(audio_path, groq_client, sia):
    try:
        # Check the file size (Groq limit is 25MB)
        if os.path.getsize(audio_path) > 25 * 1024 * 1024:
            raise ValueError("Audio file exceeds Groq's 25MB limit.")

        # Transcribe the audio file using Groq
        with open(audio_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(str(audio_path), file.read()),
                model="whisper-large-v3-turbo",  # Use the latest Groq Whisper model
                response_format="json",
                language="en"
            )
            text = transcription.text

        if not text.strip():
            raise ValueError("Transcription resulted in empty text")

        # Clean the transcribed text to remove duplicate phrases
        cleaned_text = remove_duplicate_phrases(text)

        # Highlight moans and profanity
        highlighted_text = highlight_keywords(cleaned_text, moan_keywords + profanity_keywords)

        # Perform sentiment analysis on the cleaned transcribed text
        sentiment = sia.polarity_scores(cleaned_text)

        return highlighted_text, sentiment
    except FileNotFoundError:
        print(f"Audio file does not exist: {audio_path}")
        return None, None
    except PermissionError:
        print(f"Permission denied when accessing the audio file: {audio_path}")
        return None, None
    except Exception as e:
        print(f"Error processing the audio file: {e}")
        return None, None

# Ensure GROQ_API_KEY is set
if not os.environ.get("GROQ_API_KEY"):
    print("Please set your GROQ_API_KEY environment variable.")
    exit(1)

# Initialize VADER (Valence Aware Dictionary and sEntiment Reasoner)
sia = SentimentIntensityAnalyzer()

# Path to the audio file (use pathlib for cross-platform compatibility)
audio_file = Path(r'D:/carlo/Edits/1_1463825_20240501-000937-remastered.wav')

# Transcribe and analyze the audio file
transcribed_text, sentiment = transcribe_and_analyze(audio_file, client, sia)

if transcribed_text and sentiment:
    # Print the transcribed and highlighted text
    print(f'Transcribed Text:\n{transcribed_text}')

    # Print the sentiment analysis results
    print(f'Sentiment Analysis:\n{sentiment}')