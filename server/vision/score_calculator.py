# ===============================
# FILE: score_calculator.py (CALIBRATED FOR VIDEO)
# ===============================

class ScoreCalculator:
    def __init__(self):
        pass

    # ===============================
    # 1. RAISE ARM (Giữ nguyên mode Dễ)
    # ===============================
    def score_raise_arm(self, angle, wrist_y, shoulder_y):
        if angle > 130: return 100
        score = 100 - (130 - angle)
        return self._clamp(score)

    def score_raise_both(self, angle_left, angle_right, lw_y, rw_y, ls_y, rs_y):
        score_l = self.score_raise_arm(angle_left, lw_y, ls_y)
        score_r = self.score_raise_arm(angle_right, rw_y, rs_y)
        return int((score_l + score_r) / 2)

    # ===============================
    # 2. CROUCH (Giữ nguyên)
    # ===============================
    def score_crouch(self, knee_left_angle, knee_right_angle, ls_y=None, rs_y=None):
        return 100

    # ===============================
    # 3. SQUAT (Giữ nguyên)
    # ===============================
    def score_squat(self, angle):
        lower_limit = 140
        upper_limit = 175
        if angle <= lower_limit: return 100
        elif angle >= upper_limit: return 0
        else:
            score = (upper_limit - angle) / (upper_limit - lower_limit) * 100
            return self._clamp(score + 10)

    # ===============================
    # 4. LUNGE (Giữ nguyên)
    # ===============================
    def score_lunge(self, front_knee_angle, back_knee_angle):
        return 95

    # ===============================
    # 5. PUSHUP (ĐÃ CHỈNH KHỚP VỚI VIDEO)
    # ===============================
    def score_pushup(self, elbow_angle, body_angle):
        """
        Dựa trên video mẫu:
        - Anh mẫu xuống sâu tầm 80-85 độ -> Ta set mốc < 95 là Max điểm.
        - Lưng anh mẫu rất thẳng -> Ta giữ logic check lưng.
        """
        score = 0

        # --- 1. ĐỘ SÂU (Max 60đ) ---
        # Nới lỏng mốc xuất sắc lên 95 độ (thay vì 70-80 quá gắt)
        if elbow_angle < 95:
            score += 60  # Xuất sắc (Video mẫu sẽ rơi vào đây)
        elif elbow_angle < 110:
            score += 45  # Tốt
        elif elbow_angle < 140:
            score += 30  # Tạm được
        else:
            score += 15  # Quá nông

        # --- 2. FORM (Max 40đ) ---
        # Video mẫu lưng thẳng (180 độ). Cho phép sai số rộng hơn chút để AI bắt nhạy hơn.
        # 160 < body < 210 là khoảng an toàn.
        if 160 < body_angle < 210:
            score += 40  # Form chuẩn
        elif 140 < body_angle < 230:
            score += 20  # Hơi sai
        else:
            score += 10  # Sai hẳn

        return self._clamp(score)

    # ===============================
    # UTILS
    # ===============================
    def _clamp(self, value):
        return max(0, min(100, int(value)))

    def score_general(self):
        return 90