import os
import torch
import random
import numpy as np
import cv2
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# Load CLIP model (only once)
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def score_images_with_clip(image_paths, prompt, mood, top_k=6):
    results = []
    full_text = f"A photo that represents a {mood.lower()} feeling with the theme: {prompt.lower()}"
    print("CLIP Prompt:", full_text)

    for path in image_paths:
        try:
            image = Image.open(path).convert("RGB")
            inputs = processor(text=[full_text], images=image, return_tensors="pt", padding=True)
            with torch.no_grad():
                outputs = model(**inputs)
                score = outputs.logits_per_image.item()
                results.append((score, path))
                print(f"Scoring {path} -> {score:.4f}")
        except Exception as e:
            print(f"Error processing {path}: {e}")
            continue

    MIN_SCORE_THRESHOLD = 0.2
    filtered_results = [(s, p) for s, p in results if s >= MIN_SCORE_THRESHOLD]

    if not filtered_results:
        print("No high-confidence matches found. Falling back to random images.")
        return random.sample(image_paths, min(top_k, len(image_paths)))

    filtered_results.sort(reverse=True)
    return [path for _, path in filtered_results[:top_k]]

def create_montage(image_paths, prompt, mood, music_file=None, total_duration=None):
    os.makedirs("outputs", exist_ok=True)
    top_images = score_images_with_clip(image_paths, prompt, mood)

    # Montage Image
    random.shuffle(top_images)
    images = [cv2.imread(p) for p in top_images]
    resized = [cv2.resize(img, (300, 300)) for img in images if img is not None]

    rows = []
    for i in range(0, len(resized), 3):
        row_imgs = resized[i:i+3]
        if row_imgs:
            rows.append(np.hstack(row_imgs))
    if not rows:
        raise ValueError("No valid images to create a montage.")
    montage_img = np.vstack(rows)

    image_out = "outputs/montage_image.jpg"
    cv2.imwrite(image_out, montage_img)

    # Video Montage
    clip_count = len(top_images)
    duration_per_clip = 2  # default per-image duration
    if total_duration and clip_count > 0:
        duration_per_clip = total_duration / clip_count

    clips = []
    for path in top_images:
        clip = ImageClip(path).set_duration(duration_per_clip).resize(height=480)
        clips.append(clip)
    final_video = concatenate_videoclips(clips, method="compose")

    if music_file and os.path.exists(music_file):
        audio = AudioFileClip(music_file).set_duration(final_video.duration)
        final_video = final_video.set_audio(audio)

    video_out = "outputs/montage_video.mp4"
    final_video.write_videofile(video_out, fps=24, codec="libx264", audio_codec="aac")

    return image_out, video_out
