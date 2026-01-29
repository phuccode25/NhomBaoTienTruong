from angle_calculator import AngleCalculator


def build_json(exercise, stage, rep, status, feedback):
    return {
        "exercise": exercise,
        "stage": stage,
        "rep": rep,
        "status": status,
        "feedback": feedback
    }


class ExerciseEvaluator:
    def __init__(self):
        self.stage_left = None
        self.stage_right = None
        self.stage_both = None

        self.rep_left = 0
        self.rep_right = 0
        self.rep_both = 0

        # crouch
        self.stage_crouch = None
        self.rep_crouch = 0
        self.base_ankle_y = None

        # squat
        self.stage_squat = "up"
        self.rep_squat = 0

        # lunge
        self.stage_lunge = "up"
        self.rep_lunge = 0

        # plank
        self.plank_start_time = None

        # ===========================
        # MỚI THÊM: PUSHUP (HÍT ĐẤT)
        # ===========================
        self.stage_pushup = "up"
        self.rep_pushup = 0

    # ===============================
    # 1. raise left (GIỮ NGUYÊN)
    # ===============================
    def check_raise_left(self, angle_left, wrist_left_y, shoulder_left_y, wrist_right_y, shoulder_right_y):
        if angle_left > 160 and wrist_right_y > shoulder_right_y:
            if wrist_left_y > shoulder_left_y:
                self.stage_left = "down"
            elif wrist_left_y < shoulder_left_y and self.stage_left == "down":
                self.stage_left = "up"
                self.rep_left += 1
                return build_json("raise_left", "up", self.rep_left, "correct", "Gio tay trai tot")
        return None

    # ===============================
    # 2. raise right (GIỮ NGUYÊN)
    # ===============================
    def check_raise_right(self, angle_right, wrist_right_y, shoulder_right_y, wrist_left_y, shoulder_left_y):
        if angle_right > 160 and wrist_left_y > shoulder_left_y:
            if wrist_right_y > shoulder_right_y:
                self.stage_right = "down"
            elif wrist_right_y < shoulder_right_y and self.stage_right == "down":
                self.stage_right = "up"
                self.rep_right += 1
                return build_json("raise_right", "up", self.rep_right, "correct", "Gio tay phai tot")
        return None

    # ===============================
    # 3. raise both (GIỮ NGUYÊN)
    # ===============================
    def check_raise_both(self, angle_left, angle_right, wrist_left_y, wrist_right_y, shoulder_left_y, shoulder_right_y):
        if self.stage_both is None:
            self.stage_both = "down"

        if angle_left > 160 and angle_right > 160:
            if wrist_left_y > shoulder_left_y and wrist_right_y > shoulder_right_y:
                self.stage_both = "down"

            elif (shoulder_left_y - 0.08 < wrist_left_y < shoulder_left_y + 0.02 and
                  shoulder_right_y - 0.08 < wrist_right_y < shoulder_right_y + 0.02 and
                  self.stage_both == "down"):
                self.stage_both = "horizontal"
                return build_json("raise_both", "horizontal", self.rep_both, "correct", "Hai tay dang ngang tot")

            elif (wrist_left_y < shoulder_left_y and
                  wrist_right_y < shoulder_right_y and
                  self.stage_both in ["down", "horizontal"]):
                self.stage_both = "up"
                self.rep_both += 1
                return build_json("raise_both", "up", self.rep_both, "correct", "Gio hai tay len tot")
        return None

    # ===============================
    # 4. crouch (GIỮ NGUYÊN)
    # ===============================
    def check_crouch(self, left_ankle_y, right_ankle_y):
        ankle_y = (left_ankle_y + right_ankle_y) / 2

        if self.base_ankle_y is None:
            self.base_ankle_y = ankle_y
            self.stage_crouch = "up"
            return None

        if ankle_y > self.base_ankle_y + 0.03 and self.stage_crouch == "up":
            self.stage_crouch = "down"

        elif ankle_y < self.base_ankle_y + 0.01 and self.stage_crouch == "down":
            self.stage_crouch = "up"
            self.rep_crouch += 1
            return build_json("crouch", "up", self.rep_crouch, "correct", "Ngoi xuong dung")
        return None

    # ===============================
    # 5. SQUAT (GIỮ NGUYÊN)
    # ===============================
    def check_squat(self, landmarks):
        # Lấy điểm
        hip = landmarks[23]
        knee = landmarks[25]
        ankle = landmarks[27]

        # Tính góc
        angle = AngleCalculator.calculate_angle(hip, knee, ankle)

        SQUAT_DOWN_THRESH = 135.0
        SQUAT_UP_THRESH = 160.0

        if angle < SQUAT_DOWN_THRESH:
            if self.stage_squat != "down":
                self.stage_squat = "down"
                return {
                    "exercise": "squat",
                    "stage": "down",
                    "rep": self.rep_squat,
                    "score": 0,
                    "feedback": f"Giu nguyen! (Goc: {int(angle)})"
                }

        if angle > SQUAT_UP_THRESH and self.stage_squat == "down":
            self.stage_squat = "up"
            self.rep_squat += 1
            return {
                "exercise": "squat",
                "stage": "up",
                "rep": self.rep_squat,
                "score": 100,
                "feedback": "Tot lam! Tiep tuc"
            }

        if self.stage_squat == "down":
            return {
                "exercise": "squat",
                "stage": "down",
                "rep": self.rep_squat,
                "score": 0,
                "feedback": "Xuong sau them chut nua!"
            }
        return None

    # ===============================
    # 6. lunge (GIỮ NGUYÊN)
    # ===============================
    def check_lunge(self, front_knee_angle, back_knee_angle):
        if front_knee_angle < 105 and back_knee_angle > 155:
            self.stage_lunge = "down"

        elif front_knee_angle > 165 and self.stage_lunge == "down":
            self.stage_lunge = "up"
            self.rep_lunge += 1
            return build_json("lunge", "up", self.rep_lunge, "correct", "Lunge dung")

        return None

    # ===============================
    # 7. PUSHUP (MỚI THÊM)
    # ===============================
    def check_pushup(self, landmarks):
        """
        Check hít đất:
        - Elbow angle (11-13-15): Góc tay
        - Body angle (11-23-27): Góc người (Vai - Hông - Chân) để check thẳng lưng
        """

        # 1. Lấy toạ độ (Dùng bên trái làm chuẩn vì thường quay ngang)
        shoulder = landmarks[11]
        elbow = landmarks[13]
        wrist = landmarks[15]

        hip = landmarks[23]
        ankle = landmarks[27]

        # 2. Tính góc
        elbow_angle = AngleCalculator.calculate_angle(shoulder, elbow, wrist)
        body_angle = AngleCalculator.calculate_angle(shoulder, hip, ankle)

        # 3. Logic Đếm & Check Form
        feedback_form = "Tot!"
        status = "correct"

        # Check lưng (Body alignment) - Nếu < 150 độ là lưng bị gập hoặc chổng mông
        if body_angle < 150:
            feedback_form = "Thang lung len!"
            status = "warning"

        # --- XUỐNG (DOWN) ---
        if elbow_angle < 90:  # Tay gập vuông góc
            if self.stage_pushup != "down":
                self.stage_pushup = "down"
                return build_json("pushup", "down", self.rep_pushup, "processing", "Xuong sau nua...")

        # --- LÊN (UP) ---
        if elbow_angle > 160 and self.stage_pushup == "down":
            self.stage_pushup = "up"
            self.rep_pushup += 1

            # Nếu form sai thì báo lỗi, form đúng thì khen
            final_fb = "Tot lam!" if status == "correct" else feedback_form

            return build_json("pushup", "up", self.rep_pushup, status, final_fb)

        # Nếu đang giữ ở dưới thì vẫn trả về để hiện thông báo
        if self.stage_pushup == "down":
            return build_json("pushup", "down", self.rep_pushup, "processing", "Giu lung thang!")

        return None