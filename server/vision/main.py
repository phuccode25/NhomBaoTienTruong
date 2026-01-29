import cv2
from pipeline import Pipeline
from drawKhungXuong import draw, draw_text

cap = cv2.VideoCapture(0)
pipe = Pipeline()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    landmarks, counter, stage, feedback = pipe.run(frame)

    draw(frame, landmarks)
    draw_text(frame, counter, stage, feedback)

    cv2.imshow("AI Fitness", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
