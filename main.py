import streamlit as st
import os
import re
from montage import create_montage
from music_selector import select_music

st.set_page_config(page_title="🎬 AI Montage Creator", layout="centered")
st.title("🎬 AI Montage Creator")

def extract_duration_from_prompt(prompt):
    match = re.search(r'(\d+)\s*(seconds|second|sec)', prompt.lower())
    if match:
        return int(match.group(1))
    return None

prompt = st.text_input("🎯 Enter a prompt or theme:")
mood = st.selectbox("🎵 Select a mood", ["Happy", "Sad", "Calm", "Energetic", "Romantic"])

uploaded_files = st.file_uploader("📤 Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("Create Montage"):
    if not uploaded_files:
        st.warning("Please upload at least 1 image.")
    elif not prompt:
        st.warning("Please enter a prompt.")
    else:
        os.makedirs("images", exist_ok=True)
        image_paths = []
        for file in uploaded_files:
            path = os.path.join("images", file.name)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            image_paths.append(path)

        st.info("⏳ Generating montage...")
        music_file = select_music(mood)
        duration = extract_duration_from_prompt(prompt)
        if duration:
            st.info(f"📏 Target video duration: {duration} seconds")
        image_output, video_output = create_montage(image_paths, prompt, mood, music_file, total_duration=duration)

        st.success("✅ Montage created!")
        st.image(image_output, caption="🎨 Image Montage", use_container_width=True)
        st.video(video_output)

        with open(video_output, "rb") as f:
            st.download_button("⬇️ Download Montage Video", f, file_name="montage.mp4")
