# PausePlayMedia.py

import cv2
import time
import HandTrackingModule as htm
from pynput.keyboard import Key, Controller
import math
import asyncio

# ——— WinRT imports for media status ———
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus
)

################################
wCam, hCam = 640, 480
################################

# ——— Helper to grab the media session manager asynchronously ———
async def _get_media_manager():
    return await GlobalSystemMediaTransportControlsSessionManager.request_async()

# Run the coroutine now to get the manager
_media_manager: GlobalSystemMediaTransportControlsSessionManager = asyncio.get_event_loop().run_until_complete(
    _get_media_manager()
)

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❗️ Cannot open camera. Check index or connection.")
    exit(1)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
detector = htm.handDetector(detectionCon=0.8, maxHands=1)
keyboard = Controller()

# Debounce and state variables
touching = False
touch_frame_count = 0
TOUCH_FRAME_REQUIRED = 3  # Minimum consecutive frames required to confirm contact

while True:
    success, img = cap.read()
    if not success:
        break

    # 1) Detect hand landmarks
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)

    if lmList:
        # Coordinates of thumb tip (id=4), pinky tip (id=20), pinky base (id=17)
        thumb_tip = (lmList[4][1], lmList[4][2])
        pinky_tip = (lmList[20][1], lmList[20][2])
        pinky_mcp = (lmList[17][1], lmList[17][2])

        # A) Compute Euclidean distance between thumb and pinky tip
        dist = math.hypot(pinky_tip[0] - thumb_tip[0], pinky_tip[1] - thumb_tip[1])

        # B) Normalize distance by hand‐bbox height
        bbox_height = bbox[3] - bbox[1]
        norm_dist = dist / bbox_height if bbox_height > 0 else float('inf')

        # C) Compute angle between pinky direction and vector to thumb
        vec1 = (pinky_tip[0] - pinky_mcp[0], pinky_tip[1] - pinky_mcp[1])
        vec2 = (thumb_tip[0] - pinky_mcp[0], thumb_tip[1] - pinky_mcp[1])
        dot = vec1[0] * vec2[0] + vec1[1] * vec2[1]
        mag1 = math.hypot(*vec1)
        mag2 = math.hypot(*vec2)
        angle_deg = 180.0
        if mag1 > 0 and mag2 > 0:
            angle_deg = math.degrees(math.acos(dot / (mag1 * mag2)))

        # D) Decision: “touch” only if normalized distance < 0.25 AND angle < 60°
        if norm_dist < 0.25 and angle_deg < 60:
            touch_frame_count += 1
            if touch_frame_count == TOUCH_FRAME_REQUIRED and not touching:
                # Send a media play/pause keystroke
                keyboard.press(Key.media_play_pause)
                keyboard.release(Key.media_play_pause)
                touching = True

                # Brief visual feedback (green circle at midpoint)
                mx = (thumb_tip[0] + pinky_tip[0]) // 2
                my = (thumb_tip[1] + pinky_tip[1]) // 2
                cv2.circle(img, (mx, my), 20, (0, 255, 0), cv2.FILLED)
        else:
            touch_frame_count = 0
            touching = False

    # ——— 2) Determine “Media On/Off” by querying the current session status ———
    media_on = False
    try:
        current_session = _media_manager.get_current_session()
        if current_session:
            playback_info = current_session.get_playback_info()
            status = playback_info.playback_status
            # Enum: PLAYING, PAUSED, etc.
            if status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING:
                media_on = True
    except:
        # If anything fails (e.g. no session), treat as “Off”
        media_on = False

    # 3) Overlay FPS and “Media: On/Off”
    cTime = time.time()
    fps = 1.0 / (cTime - pTime) if (cTime - pTime) != 0 else 0
    pTime = cTime

    # Draw FPS
    cv2.putText(
        img,
        f'FPS: {int(fps)}',
        (10, 40),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        (255, 0, 255),
        2
    )

    # Draw Media status below FPS
    status_text = "Media: On" if media_on else "Media: Off"
    cv2.putText(
        img,
        status_text,
        (10, 80),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        (0, 255, 255),
        2
    )

    cv2.imshow("Media Hand Control (Pinky+Thumb)", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()