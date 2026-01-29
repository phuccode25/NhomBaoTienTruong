# ===============================
# FILE: dataset_logger.py
# CHỨC NĂNG: LƯU LỊCH SỬ TẬP (JSON) & THU THẬP DỮ LIỆU (CSV)
# ===============================

import json
import csv
import os
from datetime import datetime


class DatasetLogger:
    def __init__(self, json_file="workout_log.json", csv_file="dataset/pose_dataset.csv"):
        self.json_file = json_file
        self.csv_file = csv_file

        # 1. Tạo thư mục dataset nếu chưa có (để lưu CSV)
        if not os.path.exists("dataset"):
            os.makedirs("dataset")

        # 2. Khởi tạo header cho file CSV nếu chưa tồn tại
        if not os.path.exists(self.csv_file):
            self._init_csv()

    # =========================================
    # PHẦN 1: LOG JSON (CHO APP / LỊCH SỬ)
    # =========================================
    def log_rep(self, exercise, rep_count, score, feedback):
        """
        Hàm này được gọi khi hoàn thành 1 Rep (Stage = UP)
        Lưu kết quả vào file workout_log.json
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exercise": exercise,
            "rep": rep_count,
            "score": score,
            "feedback": feedback
        }

        # Đọc dữ liệu cũ
        data = []
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = []

        # Thêm dữ liệu mới
        data.append(entry)

        # Ghi lại vào file
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"[JSON] Đã lưu Rep {rep_count} - Score: {score}")

    # =========================================
    # PHẦN 2: LOG CSV (CHO DEEP LEARNING)
    # =========================================
    def _init_csv(self):
        """ Tạo dòng tiêu đề cho file CSV """
        # Chúng ta lưu Label + Góc + Toạ độ Y quan trọng
        headers = [
            "label",
            "angle_left", "angle_right", "knee_left", "knee_right", "body_angle",
            "lw_y", "rw_y", "ls_y", "rs_y", "lh_y", "rh_y"
        ]
        with open(self.csv_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def log_dl(self, angles, ys, label):
        """ 
        Hàm này chạy liên tục mỗi khung hình.
        Lưu dữ liệu thô vào CSV để sau này Train AI.
        """
        if label == -1: return  # Không lưu nếu không rõ bài tập

        row = [
            label,
            angles["left_arm"], angles["right_arm"], angles["knee_left"], angles["knee_right"], angles["body"],
            ys["lw"], ys["rw"], ys["ls"], ys["rs"], ys["lh"], ys["rh"]
        ]

        with open(self.csv_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def exercise_to_label(self, ex):
        """ Chuyển tên bài tập thành số để lưu vào CSV """
        mapping = {
            "squat": 0,
            "raise_both": 1,
            "raise_left": 2,
            "raise_right": 3,
            "lunge": 4,
            "crouch": 5
        }
        return mapping.get(ex, -1)