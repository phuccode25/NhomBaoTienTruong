# ===============================
# FILE: pipeline.py (UPDATED WITH PUSHUP)
# ===============================

from angle_calculator import AngleCalculator
from exercise_evaluator import ExerciseEvaluator
from score_calculator import ScoreCalculator
from dataset_logger import DatasetLogger


def score_to_level(score):
    if score >= 85:
        return "good"
    elif score >= 60:
        return "medium"
    else:
        return "bad"


class ExercisePipeline:
    def __init__(self, mode="auto"):
        self.mode = mode
        self.evaluator = ExerciseEvaluator()
        self.scorer = ScoreCalculator()
        self.logger = DatasetLogger()

    def run(self, landmarks):
        # =============================
        # 1. LANDMARK
        # =============================
        # Tay
        ls, rs = landmarks[11], landmarks[12]  # Shoulders
        le, re = landmarks[13], landmarks[14]  # Elbows
        lw, rw = landmarks[15], landmarks[16]  # Wrists

        # Chân
        lh, rh = landmarks[23], landmarks[24]  # Hips
        lk, rk = landmarks[25], landmarks[26]  # Knees
        la, ra = landmarks[27], landmarks[28]  # Ankles

        # =============================
        # 2. ANGLES (Góc cơ bản)
        # =============================
        angle_left = AngleCalculator.calculate_angle(ls, le, lw)  # Góc khuỷu tay trái
        angle_right = AngleCalculator.calculate_angle(rs, re, rw)  # Góc khuỷu tay phải

        knee_left = AngleCalculator.calculate_angle(lh, lk, la)  # Góc đầu gối trái
        knee_right = AngleCalculator.calculate_angle(rh, rk, ra)  # Góc đầu gối phải

        # =============================
        # 3. CHECK ĐỘNG TÁC (PRIORITY)
        # =============================

        # --- 1. RAISE BOTH ---
        result = self.evaluator.check_raise_both(
            angle_left, angle_right,
            lw.y, rw.y,
            ls.y, rs.y
        )
        if result:
            return self._finalize(result, angle_left, angle_right, knee_left, knee_right, lw, rw, ls, rs, landmarks)

        # --- 2. RAISE ONE HAND ---
        result = self.evaluator.check_raise_left(
            angle_left, lw.y, ls.y, rw.y, rs.y
        )
        if result:
            return self._finalize(result, angle_left, angle_right, knee_left, knee_right, lw, rw, ls, rs, landmarks)

        result = self.evaluator.check_raise_right(
            angle_right, rw.y, rs.y, lw.y, ls.y
        )
        if result:
            return self._finalize(result, angle_left, angle_right, knee_left, knee_right, lw, rw, ls, rs, landmarks)

        # --- 3. CROUCH ---
        result = self.evaluator.check_crouch(la.y, ra.y)
        if result:
            return self._finalize(result, angle_left, angle_right, knee_left, knee_right, lw, rw, ls, rs, landmarks)

        # --- 4. SQUAT ---
        result = self.evaluator.check_squat(landmarks)
        if result:
            return self._finalize(result, angle_left, angle_right, knee_left, knee_right, lw, rw, ls, rs, landmarks)

        # --- 5. LUNGE ---
        result = self.evaluator.check_lunge(
            min(knee_left, knee_right),
            max(knee_left, knee_right)
        )
        if result:
            return self._finalize(result, angle_left, angle_right, knee_left, knee_right, lw, rw, ls, rs, landmarks)

        # --- 6. PUSHUP (MỚI THÊM) ---
        # Gọi hàm check_pushup trong Evaluator
        result = self.evaluator.check_pushup(landmarks)
        if result:
            return self._finalize(result, angle_left, angle_right, knee_left, knee_right, lw, rw, ls, rs, landmarks)

        return None

    # =============================
    # FINALIZE (TÍNH ĐIỂM & LOG)
    # =============================
    def _finalize(self, result,
                  angle_left, angle_right,
                  knee_left, knee_right,
                  lw, rw, ls, rs,
                  landmarks):

        ex = result["exercise"]
        score = 0  # Default

        # --- TÍNH ĐIỂM ---
        if ex == "raise_left":
            score = self.scorer.score_raise_arm(angle_left, lw.y, ls.y)

        elif ex == "raise_right":
            score = self.scorer.score_raise_arm(angle_right, rw.y, rs.y)

        elif ex == "raise_both":
            score = self.scorer.score_raise_both(
                angle_left, angle_right,
                lw.y, rw.y, ls.y, rs.y
            )

        elif ex == "crouch":
            score = self.scorer.score_crouch(
                knee_left, knee_right,
                ls.y, rs.y
            )

        elif ex == "squat":
            # Lấy góc của chân gập sâu hơn để tính điểm
            min_knee = min(knee_left, knee_right)
            score = self.scorer.score_squat(min_knee)

        elif ex == "lunge":
            score = self.scorer.score_lunge(
                min(knee_left, knee_right),
                max(knee_left, knee_right)
            )

        elif ex == "pushup":
            # --- TÍNH ĐIỂM PUSHUP ---
            # Cần tính thêm góc thân người (Vai-Hông-Chân) để chấm điểm Plank
            # 11: Vai trái, 23: Hông trái, 27: Cổ chân trái
            body_angle = AngleCalculator.calculate_angle(landmarks[11], landmarks[23], landmarks[27])

            # Dùng góc tay trái (angle_left) đại diện cho độ sâu
            score = self.scorer.score_pushup(angle_left, body_angle)

        else:
            score = 80  # Default score

        # Cập nhật điểm và level vào result
        result["score"] = score
        result["level"] = score_to_level(score)

        # =========================================================
        # [NEW] LƯU JSON KHI HOÀN THÀNH 1 REP
        # =========================================================
        stage = result.get("stage", "")

        if stage == "up":
            self.logger.log_rep(
                exercise=ex,
                rep_count=result.get("rep", 0),
                score=score,
                feedback=result.get("feedback", "")
            )

        # =========================================================
        # LOG DATA CSV
        # =========================================================
        label = self.logger.exercise_to_label(ex)

        # Log thêm body_angle nếu cần thiết cho Deep Learning sau này
        current_body_angle = AngleCalculator.calculate_angle(landmarks[11], landmarks[23], landmarks[27])

        self.logger.log_dl(
            angles={
                "left_arm": angle_left,
                "right_arm": angle_right,
                "knee_left": knee_left,
                "knee_right": knee_right,
                "body": current_body_angle  # Đã cập nhật để log góc body chuẩn
            },
            ys={
                "lw": lw.y,
                "rw": rw.y,
                "ls": ls.y,
                "rs": rs.y,
                "lh": landmarks[23].y,
                "rh": landmarks[24].y
            },
            label=label
        )

        return result