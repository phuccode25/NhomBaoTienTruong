# ==========================================
# FILE: main_app.py (PHIÊN BẢN HOÀN CHỈNH)
# ==========================================

import cv2
import numpy as np
from pose_estimation import PoseEstimator
from pipeline import ExercisePipeline
from drawKhungXuong import draw
from yanshee_connector import YansheeConnector  # Class điều khiển Robot
from dataset_logger import DatasetLogger  # Class lưu file


def draw_info_box(image, exercise, count, score, feedback, mode):
    """ Vẽ bảng thông tin đẹp trên màn hình """
    # Vẽ hộp nền bán trong suốt
    overlay = image.copy()
    cv2.rectangle(overlay, (0, 0), (350, 180), (0, 0, 0), -1)
    alpha = 0.7
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    # Viết chữ
    cv2.putText(image, f"MODE: {mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(image, f"BAI: {exercise.upper()}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(image, f"REP: {count}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    cv2.putText(image, f"SCORE: {score}", (160, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (50, 100, 255), 2)

    # Feedback màu đỏ hoặc xanh tùy điểm
    color = (0, 255, 0) if score > 50 else (0, 0, 255)
    cv2.putText(image, f"{feedback}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def main():
    # 1. KHỞI TẠO HỆ THỐNG
    cap = cv2.VideoCapture(0)  # Hoặc đường dẫn video "videos/test.mp4"
    cap.set(3, 1280)  # Set độ phân giải rộng
    cap.set(4, 720)

    pose = PoseEstimator()

    # Pipeline: Chế độ 'auto' sẽ dùng model.pkl để đoán bài tập
    pipeline = ExercisePipeline(mode="auto")

    # Kết nối Robot (Nếu không có thì nó tự bỏ qua)
    try:
        robot = YansheeConnector("192.168.1.xxx")  # <-- ĐIỀN IP ROBOT VÀO ĐÂY
    except:
        robot = None
        print("⚠️ Không kết nối được Robot - Chạy chế độ Im lặng")

    logger = DatasetLogger()

    print("✅ HỆ THỐNG SẴN SÀNG! BẮT ĐẦU TẬP...")

    # Biến lưu trạng thái cũ để tránh spam lệnh cho Robot
    last_rep_count = 0

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Lật ảnh cho giống gương (nếu dùng webcam)
        frame = cv2.flip(frame, 1)

        # 2. XỬ LÝ AI
        pose_result = pose.process(frame)

        if pose_result.pose_landmarks:
            landmarks = pose_result.pose_landmarks.landmark

            # Vẽ xương
            draw(frame, pose_result.pose_landmarks)

            # Chạy logic đếm & phân loại
            result = pipeline.run(landmarks)

            if result:
                # Lấy dữ liệu ra
                ex_name = result.get("exercise", "Unknown")
                rep = result.get("rep", 0)
                score = result.get("score", 0)
                feedback = result.get("feedback", "...")
                stage = result.get("stage", "")

                # 3. LOGIC GỌI ROBOT & LƯU LOG
                # Chỉ thực hiện khi số Rep tăng lên (Tức là vừa làm xong 1 cái)
                if rep > last_rep_count:
                    print(f"🔥 HOÀN THÀNH: {ex_name} - Điểm: {score}")

                    # A. Lưu vào JSON
                    logger.log_rep(ex_name, rep, score, feedback)

                    # B. Gọi Robot
                    if robot:
                        # Robot nói lời khen/chê
                        robot.speak(feedback)
                        # Robot làm hành động (nếu điểm cao)
                        if score >= 80: robot.do_action("clap")

                    last_rep_count = rep

                # 4. VẼ GIAO DIỆN
                draw_info_box(frame, ex_name, rep, score, feedback, "AI-AUTO")

        else:
            # Nếu không thấy người
            cv2.putText(frame, "KHONG THAY NGUOI", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("AI WORKOUT ASSISTANT", frame)

        if cv2.waitKey(1) == 27:  # ESC
            break

    pose.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()