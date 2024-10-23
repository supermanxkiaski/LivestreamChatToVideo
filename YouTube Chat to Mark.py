import cv2
import pygame
import pytchat
import multiprocessing
import time

# Initialize pygame for audio playback
pygame.mixer.init()

# Function to play a video with sound
def play_video(video_path, interrupt_event):
    print(f"Attempting to play video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    # Assume the audio file has the same name as the video file but with .mp3 extension
    audio_path = video_path.rsplit('.', 1)[0] + '.mp3'
    
    cv2.namedWindow('Video Player', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video Player', 640, 480)
    
    if audio_path:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
    
    while cap.isOpened() and not interrupt_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error: Frame not read properly.")
            break
        cv2.imshow('Video Player', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            interrupt_event.set()
            break
    
    cap.release()
    pygame.mixer.music.stop()
    cv2.destroyAllWindows()

# Function to fetch chat messages and return the next video path
def fetch_chat(video_id, queue):
    chat = pytchat.create(video_id=video_id)
    while chat.is_alive():
        for message in chat.get().sync_items():
            input_text = message.message.lower()
            print(f"Chat message: {input_text}")
            if input_text == "stop":
                queue.put("stop")
                return
            elif input_text == "skibidi":
                queue.put('skibidi.mov')
            elif input_text == "what the sigma":
                queue.put('whatthesigma.mov')
            elif input_text == "what is this":
                queue.put('whatisthis.mov')
            else:
                print("Unknown command. Continuing default video...")

# Function to manage video playback based on chat input
def video_manager(video_id):
    queue = multiprocessing.Queue()
    chat_process = multiprocessing.Process(target=fetch_chat, args=(video_id, queue))
    chat_process.start()

    default_video_path = 'default_video.mp4'
    interrupt_event = multiprocessing.Event()

    # Play default video in a separate process
    default_process = multiprocessing.Process(target=play_video, args=(default_video_path, interrupt_event))
    default_process.start()

    while True:
        if not queue.empty():
            next_video = queue.get()
            if next_video == "stop":
                interrupt_event.set()
                break
            else:
                interrupt_event.set()
                default_process.join()
                interrupt_event.clear()
                play_video(next_video, interrupt_event)
                default_process = multiprocessing.Process(target=play_video, args=(default_video_path, interrupt_event))
                default_process.start()

        time.sleep(0.1)  # Small sleep to prevent CPU overuse

    chat_process.terminate()
    chat_process.join()

if __name__ == "__main__":
    # YouTube Video ID
    video_id = "-9xa5zacOZE"  # Replace with your actual YouTube video ID

    # Start the video manager
    video_manager(video_id)

    # Cleanup
    cv2.destroyAllWindows()
