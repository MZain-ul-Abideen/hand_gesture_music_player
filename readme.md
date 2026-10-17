# Hand Gesture Music Controller

A Python application that lets you control music playback using hand gestures detected through your webcam.

## Features
- Real-time hand detection and landmark tracking using MediaPipe.
- Finger counting with OpenCV.
- Music playback using Pygame.
- Visual feedback showing finger count and hand landmarks.

## Gesture Controls

| Gesture | Action |
|---|---|
| 1 finger | Play Song 1 |
| 2 fingers | Play Song 2 |
| 3 fingers | Play Song 3 |
| 4 fingers | Play Song 4 |
| 5 fingers | Play Song 5 |
| Closed fist | Stop music |
| Q | Quit application |

## Installation

```bash
git clone https://github.com/MZain-ul-Abideen/hand_gesture_music_player.git
cd hand_gesture_music_player

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt
```

Download the [MediaPipe Hand Landmarker model](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task) and place `hand_landmarker.task` beside `main.py`.

Add five MP3 files to the `music/` directory, named `song1.mp3` through `song5.mp3`.

## Run

```bash
python main.py
```

## Technologies

Python · OpenCV · MediaPipe · Pygame

## Acknowledgements

[MediaPipe](https://developers.google.com/edge/mediapipe) for hand landmark detection, [OpenCV](https://opencv.org/) for computer vision, and [Pygame](https://www.pygame.org/) for audio playback.