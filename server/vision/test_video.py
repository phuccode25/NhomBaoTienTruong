import cv2
import numpy as np
from pose_estimation import PoseEstimator
from pipeline import ExercisePipeline
from drawKhungXuong import draw
from angle_calculator import AngleCalculator

VIDEO_PATH = "videos/pushup.mp4"


# VIDEO_PATH = 0  # Webcam

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)

    pose = PoseEstimator()
    pipeline = ExercisePipeline()

    current_status = {
        "exercise": "Ready",
        "rep": 0,
        "stage": "-",
        "score": 0,
        "feedback": "..."
    }

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Lấy kích thước video gốc
        h, w, _ = frame.shape

        # ---------------------------------------------------------
        # 1. XỬ LÝ AI
        # ---------------------------------------------------------
        result_pose = pose.process(frame)

        if result_pose.pose_landmarks:
            landmarks = result_pose.pose_landmarks.landmark

            # Vẽ xương lên video gốc
            draw(frame, result_pose.pose_landmarks)

            # Debug góc
            try:
                if current_status["exercise"] in ["SQUAT", "LUNGE", "READY"]:
                    p_hip, p_knee, p_ankle = landmarks[23], landmarks[25], landmarks[27]
                    angle = AngleCalculator.calculate_angle(p_hip, p_knee, p_ankle)
                    cx, cy = int(p_knee.x * w), int(p_knee.y * h)
                    cv2.putText(frame, str(int(angle)), (cx + 10, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

                    # Nếu đang Pushup thì hiện góc tay
                elif current_status["exercise"] == "PUSHUP":
                    p_sho, p_elb, p_wri = landmarks[11], landmarks[13], landmarks[15]
                    angle = AngleCalculator.calculate_angle(p_sho, p_elb, p_wri)
                    cx, cy = int(p_elb.x * w), int(p_elb.y * h)
                    cv2.putText(frame, str(int(angle)), (cx + 10, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            except:
                pass

            # Chạy Pipeline
            result = pipeline.run(landmarks)

            # Cập nhật trạng thái nếu có kết quả
            if result:
                current_status["exercise"] = result["exercise"].upper()
                current_status["rep"] = result.get("rep", 0)
                current_status["stage"] = result.get("stage", "-")
                current_status["score"] = result.get("score", 0)
                current_status["feedback"] = result.get("feedback", "")

        # ---------------------------------------------------------
        # 2. TẠO THANH HEADER (ĐÃ SỬA: ĐƯA RA NGOÀI LOGIC AI)
        # ---------------------------------------------------------
        # Phần này phải chạy mỗi frame, bất kể có detected được người hay không
        header_height = 120
        header = np.zeros((header_height, w, 3), dtype=np.uint8)
        header[:] = (245, 117, 16)  # Màu cam

        # --- CỘT 1: REPS ---
        cv2.rectangle(header, (0, 0), (150, header_height), (200, 90, 10), -1)
        cv2.putText(header, 'REPS', (30, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

        # Căn giữa số Rep
        rep_text = str(current_status["rep"])
        text_size = cv2.getTextSize(rep_text, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 4)[0]
        text_x = int((150 - text_size[0]) / 2)
        cv2.putText(header, rep_text, (text_x, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 4, cv2.LINE_AA)

        # --- CỘT 2: THÔNG TIN BÀI TẬP ---
        cv2.putText(header, f"EXERCISE: {current_status['exercise']}", (170, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        stage_color = (0, 0, 255) if current_status['stage'] == 'down' else (0, 255, 0)
        cv2.putText(header, "STAGE:", (170, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(header, f"{current_status['stage'].upper()}", (270, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, stage_color, 2, cv2.LINE_AA)

        # --- CỘT 3: ĐIỂM SỐ & FEEDBACK ---
        cv2.putText(header, f"SCORE: {current_status['score']}", (500, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        fb_text = current_status["feedback"]
        font_scale = 0.7 if len(fb_text) > 20 else 0.8
        cv2.putText(header, fb_text, (400, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), 2, cv2.LINE_AA)

        # ---------------------------------------------------------
        # 3. GHÉP HEADER VÀO VIDEO
        # ---------------------------------------------------------
        final_frame = np.vstack((header, frame))

        cv2.imshow("AI PERSONAL TRAINER", final_frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()