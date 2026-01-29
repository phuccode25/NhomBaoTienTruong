def generate_feedback(angle, stage):
    if angle > 160:
        return "Hạ tay xuống"
    if angle < 45:
        return "Giơ tay lên cao hơn"
    return "Giữ nhịp ổn định"
