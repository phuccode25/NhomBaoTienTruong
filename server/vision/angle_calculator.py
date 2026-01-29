import numpy as np
import math


class AngleCalculator:
    @staticmethod
    def calculate_angle(a, b, c):
        """
        Tính góc hợp bởi 3 điểm a, b, c.
        Điểm b là đỉnh góc (ví dụ: Hông -> ĐẦU GỐI -> Cổ chân).

        Args:
            a, b, c: Có thể là list [x, y], numpy array,
                     hoặc object landmark của MediaPipe (có thuộc tính .x, .y).

        Returns:
            float: Góc tính bằng độ (0 -> 180).
        """
        # 1. Chuẩn hóa đầu vào thành numpy array [x, y]
        point_a = AngleCalculator._to_array(a)
        point_b = AngleCalculator._to_array(b)
        point_c = AngleCalculator._to_array(c)

        # 2. Tính toán góc dùng arctan2
        # vecto BA = a - b
        # vecto BC = c - b
        radians = np.arctan2(point_c[1] - point_b[1], point_c[0] - point_b[0]) - \
                  np.arctan2(point_a[1] - point_b[1], point_a[0] - point_b[0])

        angle = np.abs(radians * 180.0 / np.pi)

        # 3. Chuẩn hóa về góc nhọn/tù (0-180) thay vì 360
        if angle > 180.0:
            angle = 360.0 - angle

        return angle

    @staticmethod
    def _to_array(point):
        """Hàm phụ trợ: Chuyển đổi input bất kỳ thành numpy array [x, y]"""
        # Nếu là landmark của MediaPipe (có thuộc tính x, y)
        if hasattr(point, 'x') and hasattr(point, 'y'):
            return np.array([point.x, point.y])

        # Nếu là list hoặc tuple
        return np.array(point[:2])  # Chỉ lấy 2 phần tử đầu (x, y), bỏ qua z hoặc visibility


# Alias để tương thích ngược nếu code cũ của bạn đang gọi hàm này
tinhToan_goc = AngleCalculator.calculate_angle