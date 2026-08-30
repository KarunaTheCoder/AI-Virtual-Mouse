import cv2

import mediapipe as mp

import pyautogui

import math

import time

import streamlit as st


# --- STREAMLIT UI CONFIGURATION ---

st.set_page_config(page_title="AI Virtual Mouse", layout="wide")

st.title("AI Virtual Mouse")

st.markdown("Advanced utility integration featuring dynamic application bounding locks and context-aware macro triggers.")


# Sidebar Configuration

st.sidebar.header("🎛️ Advanced Configuration")

alpha = st.sidebar.slider("EMA Smoothing Alpha", min_value=0.05, max_value=1.0, value=0.25, step=0.05)

frame_skip_rate = st.sidebar.slider("Frame Skip Rate", min_value=1, max_value=5, value=2)

click_threshold = st.sidebar.slider("Click Distance Threshold", min_value=20, max_value=60, value=35)


# Sidebar Macro Control Only

st.sidebar.subheader("🔒 Action Macro Triggers")

enable_macros = st.sidebar.checkbox("Enable Fist Macro Trigger", value=True)


# Update this path to your testing clip or keep it for your webcam/video stream



run_app = st.sidebar.checkbox("Start", value=False)


def map_range(value, old_min, old_max, new_min, new_max):

    if value < old_min: value = old_min

    if value > old_max: value = old_max

    return new_min + ((value - old_min) / (old_max - old_min)) * (new_max - new_min)


def check_fingers_status(landmarks):

    # Returns binary array of fingers up: [Thumb, Index, Middle, Ring, Pinky]

    thumb_up = landmarks[4].x < landmarks[3].x if landmarks[4].x < landmarks[17].x else landmarks[4].x > landmarks[3].x

    index_up = landmarks[8].y < (landmarks[6].y + 0.02)

    middle_up = landmarks[12].y < (landmarks[10].y + 0.02)

    ring_up = landmarks[16].y < (landmarks[14].y + 0.02)

    pinky_up = landmarks[20].y < (landmarks[18].y + 0.02)

    return [thumb_up, index_up, middle_up, ring_up, pinky_up]


frame_placeholder = st.empty()


if run_app:

    BaseOptions = mp.tasks.BaseOptions

    HandLandmarker = mp.tasks.vision.HandLandmarker

    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

    VisionRunningMode = mp.tasks.vision.RunningMode


    options = HandLandmarkerOptions(

        base_options=BaseOptions(model_asset_path='hand_landmarker.task'),

        running_mode=VisionRunningMode.VIDEO,

        num_hands=1,

        min_hand_detection_confidence=0.4,

        min_hand_presence_confidence=0.4

    )


    screen_width, screen_height = pyautogui.size()

    pyautogui.FAILSAFE = False


    # State variables

    ploc_x, ploc_y = pyautogui.position()

    prev_y = 0

    cached_hand_landmarks = None

    macro_cooldown = 0  # Prevents firing a hotkey 60 times a second


    cap = cv2.VideoCapture(0)

    fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30


    with HandLandmarker.create_from_options(options) as landmarker:

        frame_index = 0

        

        while cap.isOpened() and run_app:

            success, frame = cap.read()

            if not success:

                st.warning("Processing Complete or Video Stream Ended.")

                break


            frame = cv2.resize(frame, (640, 480))

            cam_width, cam_height = 640, 480

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            

            video_timestamp_ms = int((frame_index / fps) * 1000)

            

            if frame_index % frame_skip_rate == 0:

                video_result = landmarker.detect_for_video(mp_image, video_timestamp_ms)

                if video_result and video_result.hand_landmarks:

                    cached_hand_landmarks = video_result.hand_landmarks[0]

                else:

                    cached_hand_landmarks = None

            

            frame_index += 1


            if cached_hand_landmarks:

                thumb_tip = cached_hand_landmarks[4]

                index_tip = cached_hand_landmarks[8]

                middle_tip = cached_hand_landmarks[12]

                

                tx, ty = int(thumb_tip.x * cam_width), int(thumb_tip.y * cam_height)

                ix, iy = int(index_tip.x * cam_width), int(index_tip.y * cam_height)

                

                # Get state array of all 5 fingers

                fingers = check_fingers_status(cached_hand_landmarks)

                

                # ----------------------------------------------------

                # CRITICAL FEATURE: CONTEXT-AWARE MACRO (FIST CLOSED)

                # ----------------------------------------------------

                if sum(fingers) == 0 and enable_macros:

                    if (time.time() - macro_cooldown) > 1.5:

                        cv2.putText(frame, "EXECUTE MACRO: MINIMIZE ALL", (40, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                        pyautogui.hotkey('win', 'd') # System macro shortcut to clear desktop instantly

                        macro_cooldown = time.time()

                        st.toast("System Workspace Macro Fired!")


                # ----------------------------------------------------

                # MODE 1: SCROLL MODE (Index + Middle + Ring UP)

                # ----------------------------------------------------

                elif fingers[1] and fingers[2] and fingers[3]:

                    cv2.putText(frame, "SYSTEM: SCROLL ENGAGED", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

                    if prev_y == 0:

                        prev_y = iy

                    scroll_distance = prev_y - iy

                    if abs(scroll_distance) > 4:

                        pyautogui.scroll(scroll_distance * 4)

                    prev_y = iy  

                    

                # ----------------------------------------------------

                # MODE 2: NAVIGATION MODE (FIXED FOR LEFT MOVEMENT)

                # ----------------------------------------------------

                elif fingers[1] and not fingers[2] and not fingers[3]:

                    prev_y = 0  

                    cv2.putText(frame, "SYSTEM: NAVIGATION ACTIVE", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                    cv2.circle(frame, (ix, iy), 8, (255, 0, 0), cv2.FILLED)

                    

                    # Map directly across full display scope coordinates

                    mapped_x = map_range(ix, 0, cam_width, 0, screen_width)

                    mapped_y = map_range(iy, 0, cam_height, 0, screen_height)

                    

                    # Trigger visual border alert at actual edge frames of the camera input stream

                    if ix <= 0 or ix >= cam_width or iy <= 0 or iy >= cam_height:

                        cv2.putText(frame, "LIMIT REACHED", (40, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)


                    # Apply Phase 2 filtering logic

                    cloc_x = (alpha * mapped_x) + ((1 - alpha) * ploc_x)

                    cloc_y = (alpha * mapped_y) + ((1 - alpha) * ploc_y)

                    

                    pyautogui.moveTo(int(cloc_x), int(cloc_y))

                    ploc_x, ploc_y = cloc_x, cloc_y

                    

                    # Left click action logic

                    left_pinch_dist = math.hypot(tx - ix, ty - iy)

                    if left_pinch_dist < click_threshold:  

                        pyautogui.click(button='left')

                        cv2.putText(frame, "EXECUTE: LEFT CLICK", (40, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                        time.sleep(0.15)

            else:

                prev_y = 0


            frame_placeholder.image(frame, channels="BGR", use_column_width=True)

            

    cap.release()

else:

    st.info("Check the box in the sidebar to activate the enterprise controller.")