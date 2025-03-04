import os
import yt_dlp
import whisper
from transformers import pipeline
import streamlit as st
from time import sleep

st.set_page_config(page_title="SummarizeTube", page_icon="🎥")

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1533134486753-c833f0ed4866?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-position: center;
    }
    .stTextInput>div>div>input {
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border-radius: 5px;
        border: 1px solid #4CAF50;
        padding: 10px;
    }
    .stTextArea>div>div>textarea {
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border-radius: 5px;
        border: 1px solid #4CAF50;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stProgress>div>div>div>div {
        background-color: #4CAF50;
    }
    .stSpinner>div>div {
        border-top-color: #4CAF50;
    }
    .css-1aumxhk {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎥 SummarizeTube")
st.markdown("Enter a YouTube video URL to transcribe and summarize its content.")

youtube_url = st.text_input("Enter YouTube Video URL:")

def download_audio(youtube_url, output_filename="audio.mp3"):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio",
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return "audio.mp3" if os.path.exists("audio.mp3") else None

def transcribe_audio(audio_path, model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return result["text"]

def chunk_text(text, max_length=1000):
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def summarize_text(text):
    summarizer = pipeline("summarization", model="t5-small")  # Alternative small model

    chunks = chunk_text(text, max_length=1000)
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    return " ".join(summaries)

if youtube_url:
    with st.spinner("Downloading audio..."):
        audio_file = download_audio(youtube_url)
    
    if audio_file:
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio(audio_file)
        
        st.subheader("Transcription")
        st.text_area("Transcription", transcript, height=300, key="transcription")
        
        with st.spinner("Generating summary..."):
            summary = summarize_text(transcript)
        
        st.subheader("Summary")
        st.text_area("Summary", summary, height=150, key="summary")
    else:
        st.error("Failed to download audio. Please check the URL and try again.")