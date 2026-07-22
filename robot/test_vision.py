from vision import Vision
import time

vision = Vision()

while True:
    face = vision.get_face()

    if face["found"]:
        print(
            "Face:",
            round(face["x"],2),
            round(face["y"],2),
            "confidence:",
            round(face["confidence"],2)
        )
    else:
        print("No face")

    time.sleep(0.1)