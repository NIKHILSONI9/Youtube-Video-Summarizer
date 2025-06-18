import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    video_id_match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([\w-]+)", url)
    return video_id_match.group(1) if video_id_match else None

def get_transcript(video_id):
    """Fetch the transcript of the YouTube video."""
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry['text'] for entry in transcript_data])
        return transcript
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def summarize_text(text, max_length):
    """Summarize the given text using Hugging Face transformers."""
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=max_length, min_length=max_length//2, do_sample=False)
    return summary[0]['summary_text']

def answer_question(context, question):
    """Answer user questions based on the transcript or summary."""
    qa_pipeline = pipeline("question-answering")
    answer = qa_pipeline(question=question, context=context)
    return answer['answer']

st.title("YouTube Video Transcript & Summary Extractor")

youtube_url = st.text_input("Enter YouTube Video URL:")
if youtube_url:
    video_id = extract_video_id(youtube_url)
    if video_id:
        transcript = get_transcript(video_id)
        if "Error" not in transcript:
            st.subheader("Original Transcript:")
            st.text_area("Transcript", transcript, height=250)
            
            # User selects summary length
            summary_length = st.slider("Select summary length (words):", min_value=20, max_value=500, value=100)
            
            if st.button("Generate Summary"):
                summary = summarize_text(transcript, summary_length)
                st.subheader("Summarized Transcript:")
                st.write(summary)
                
                # Chatbot for Q&A
                st.subheader("Ask a question about the video:")
                question = st.text_input("Enter your question:")
                if st.button("Get Answer"):
                    context = summary if summary else transcript
                    answer = answer_question(context, question)
                    st.write("Answer:", answer)
        else:
            st.error(transcript)
    else:
        st.error("Invalid YouTube URL. Please enter a valid link.")