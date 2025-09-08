YOLOPlayer 🎥

A OpenCV wrapper for video playback, detection overlays, and future extensions (YOLO, DeepSORT, SAM, Faster-RCNN).    #right now only tested on YOLO


✨ Features:
✅ Replace cv2.imshow with a more usable player
⏯️ Pause/Play with Spacebar
🔁 Forward/Rewind with Arrow Keys
🖥️ Toggle Fullscreen with F
🚪 Quit with Q
🤖 (Optional) YOLO integration for human detection
📦 Easy to extend with tracking (DeepSORT), segmentation (SAM), Faster-RCNN, etc.



⌨️ Controls

| Key     | Action            |
| ------- | ----------------- |
| `SPACE` | Pause / Play      |
| `Q`     | Quit              |
| `F`     | Fullscreen toggle |
| `→`     | Forward 1 seconds |
| `←`     | Rewind 1 seconds  |
    



Installation-

Clone the repo:

git clone https://github.com/raunitsingh/cvplayer.git
cd yoloplayer


create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


install dependencies:

pip install -r requirements.txt





🚀 Usage:

Basic video player:

from yoloplayer import YOLOPlayer

# Play a video file
player = YOLOPlayer("video.mp4")
player.run()



for webcam:

player = YOLOPlayer(0)
player.run()



For YOLO detection:

from yoloplayer import YOLOPlayer

player = YOLOPlayer("video.mp4", use_yolo=True, model_path="yolov8n.pt")
player.run()



