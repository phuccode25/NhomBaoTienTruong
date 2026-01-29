# ===============================
# FILE: drawKhungXuong.py
# Vẽ khung xương – chuẩn MediaPipe
# ===============================

import mediapipe as mp

mp_draw = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def draw(frame, landmarks):
    """
    landmarks: results.pose_landmarks
    """
    mp_draw.draw_landmarks(
        frame,
        landmarks,
        mp_pose.POSE_CONNECTIONS
    )
