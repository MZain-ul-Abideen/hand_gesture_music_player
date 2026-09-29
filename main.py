import cv2
import mediapipe as mp
import pygame
import time
import os


# ============================================================
# CONFIGURATION
# ============================================================

SONGS = {
    1: "music/song1.mp3",
    2: "music/song2.mp3",
    3: "music/song3.mp3",
    4: "music/song4.mp3",
    5: "music/song5.mp3",
}

COOLDOWN = 1.0
CAMERA_INDEX = 0


# ============================================================
# AUDIO
# ============================================================

AUDIO_AVAILABLE = False

try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
    print("Audio initialized successfully.")

except pygame.error as e:
    print("WARNING: Audio could not be initialized.")
    print(f"Audio error: {e}")


# ============================================================
# MUSIC
# ============================================================

current_fingers = None
last_change_time = 0


def play_song(fingers):
    global current_fingers

    # No fingers = stop music
    if fingers == 0:

        if AUDIO_AVAILABLE:
            pygame.mixer.music.stop()

        print("Music stopped.")
        current_fingers = 0
        return

    # Only 1-5 are valid
    if fingers not in SONGS:
        return

    song = SONGS[fingers]

    # Check file
    if not os.path.exists(song):
        print(f"ERROR: Missing file: {song}")
        return

    # Audio unavailable
    if not AUDIO_AVAILABLE:
        print(f"Detected {fingers} finger(s) -> {song}")
        current_fingers = fingers
        return

    try:

        pygame.mixer.music.load(song)
        pygame.mixer.music.play()

        current_fingers = fingers

        print(f"Playing song {fingers}: {song}")

    except pygame.error as e:

        print(f"Could not play {song}")
        print(f"Audio error: {e}")


# ============================================================
# FINGER COUNTING
# ============================================================

def count_fingers(landmarks, handedness):
    """
    Count raised fingers using MediaPipe hand landmarks.

    Landmark IDs:

        Thumb:
            4 = tip
            3 = IP

        Index:
            8 = tip
            6 = PIP

        Middle:
            12 = tip
            10 = PIP

        Ring:
            16 = tip
            14 = PIP

        Pinky:
            20 = tip
            18 = PIP
    """

    fingers = []

    # --------------------------------------------------------
    # Thumb
    # --------------------------------------------------------

    if handedness == "Right":
        thumb_open = landmarks[4].x < landmarks[3].x
    else:
        thumb_open = landmarks[4].x > landmarks[3].x

    fingers.append(thumb_open)

    # --------------------------------------------------------
    # Index
    # --------------------------------------------------------

    fingers.append(
        landmarks[8].y < landmarks[6].y
    )

    # --------------------------------------------------------
    # Middle
    # --------------------------------------------------------

    fingers.append(
        landmarks[12].y < landmarks[10].y
    )

    # --------------------------------------------------------
    # Ring
    # --------------------------------------------------------

    fingers.append(
        landmarks[16].y < landmarks[14].y
    )

    # --------------------------------------------------------
    # Pinky
    # --------------------------------------------------------

    fingers.append(
        landmarks[20].y < landmarks[18].y
    )

    return sum(fingers)


# ============================================================
# MEDIAPIPE TASKS SETUP
# ============================================================

print("Initializing MediaPipe...")

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


# ------------------------------------------------------------
# IMPORTANT:
# MediaPipe Tasks requires a hand-landmarker model file.
# ------------------------------------------------------------

MODEL_PATH = "hand_landmarker.task"


if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"""
Missing MediaPipe model:

    {MODEL_PATH}

Download the Hand Landmarker model and place it next to
main.py before running the program.
"""
    )


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),

    running_mode=VisionRunningMode.IMAGE,

    num_hands=1,

    min_hand_detection_confidence=0.7,

    min_hand_presence_confidence=0.7,

    min_tracking_confidence=0.7
)


landmarker = HandLandmarker.create_from_options(options)

print("MediaPipe initialized successfully.")


# ============================================================
# WEBCAM
# ============================================================

cap = cv2.VideoCapture(CAMERA_INDEX)


if not cap.isOpened():

    raise RuntimeError(
        "Could not open webcam."
    )


print()
print("=" * 50)
print("       HAND MUSIC CONTROLLER")
print("=" * 50)
print()
print("Show your hand to the camera.")
print()
print("1 finger  -> Song 1")
print("2 fingers -> Song 2")
print("3 fingers -> Song 3")
print("4 fingers -> Song 4")
print("5 fingers -> Song 5")
print("0 fingers -> Stop music")
print()
print("Press Q to quit.")
print("=" * 50)
print()


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # Read frame
        # ----------------------------------------------------

        success, frame = cap.read()

        if not success:
            print("Could not read webcam frame.")
            break

        # ----------------------------------------------------
        # Mirror image
        # ----------------------------------------------------

        frame = cv2.flip(frame, 1)

        # ----------------------------------------------------
        # Convert OpenCV image to MediaPipe image
        # ----------------------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        # ----------------------------------------------------
        # Detect hand
        # ----------------------------------------------------

        result = landmarker.detect(mp_image)

        fingers = None

        # ----------------------------------------------------
        # Hand detected
        # ----------------------------------------------------

        if result.hand_landmarks:

            landmarks = result.hand_landmarks[0]

            # ------------------------------------------------
            # Determine handedness
            # ------------------------------------------------

            handedness = "Right"

            if result.handedness:

                handedness = (
                    result.handedness[0][0].category_name
                )

            # ------------------------------------------------
            # Draw landmarks manually
            # ------------------------------------------------

            h, w, _ = frame.shape

            # Draw points
            for landmark in landmarks:

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

            # ------------------------------------------------
            # Draw connections
            # ------------------------------------------------

            connections = [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 4),

                (0, 5),
                (5, 6),
                (6, 7),
                (7, 8),

                (5, 9),
                (9, 10),
                (10, 11),
                (11, 12),

                (9, 13),
                (13, 14),
                (14, 15),
                (15, 16),

                (13, 17),
                (17, 18),
                (18, 19),
                (19, 20),

                (0, 17)
            ]

            for start, end in connections:

                x1 = int(landmarks[start].x * w)
                y1 = int(landmarks[start].y * h)

                x2 = int(landmarks[end].x * w)
                y2 = int(landmarks[end].y * h)

                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

            # ------------------------------------------------
            # Count fingers
            # ------------------------------------------------

            fingers = count_fingers(
                landmarks,
                handedness
            )

            # ------------------------------------------------
            # Change song
            # ------------------------------------------------

            now = time.time()

            if (
                fingers != current_fingers
                and now - last_change_time >= COOLDOWN
            ):

                play_song(fingers)

                last_change_time = now

            # ------------------------------------------------
            # Display fingers
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"Fingers: {fingers}",
                (30, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 0),
                3
            )

            # ------------------------------------------------
            # Display hand
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"Hand: {handedness}",
                (30, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )

        else:

            # ------------------------------------------------
            # No hand
            # ------------------------------------------------

            cv2.putText(
                frame,
                "No hand detected",
                (30, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2
            )

        # ----------------------------------------------------
        # Audio status
        # ----------------------------------------------------

        audio_text = (
            "Audio: ON"
            if AUDIO_AVAILABLE
            else "Audio: OFF"
        )

        cv2.putText(
            frame,
            audio_text,
            (30, 155),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        # ----------------------------------------------------
        # Show webcam
        # ----------------------------------------------------

        cv2.imshow(
            "Hand Music Controller",
            frame
        )

        # ----------------------------------------------------
        # Quit
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# ============================================================
# CLEANUP
# ============================================================

finally:

    cap.release()

    landmarker.close()

    cv2.destroyAllWindows()

    if AUDIO_AVAILABLE:

        pygame.mixer.music.stop()
        pygame.mixer.quit()

    print()
    print("Hand Music Controller stopped.")