import cv2
import time


class Vision:

    def __init__(self):

        # Camera setup
        self.camera = cv2.VideoCapture(
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=1280, height=720, "
            "format=NV12, framerate=21/1 ! "
            "nvvidconv ! "
            "video/x-raw, format=BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=BGR ! "
            "appsink",
            cv2.CAP_GSTREAMER
        )

        if not self.camera.isOpened():
            raise Exception("Camera failed to open")


        # Face detector model
        model_path = "/home/jetbot/face_model/"

        self.net = cv2.dnn.readNetFromCaffe(
            model_path + "deploy.prototxt",
            model_path + "res10_300x300_ssd_iter_140000.caffemodel"
        )


        # Smoothing values
        self.smooth_x = 0.5
        self.smooth_y = 0.5
        self.smoothing = 0.15


        # Face tracking memory
        self.last_seen = time.time()
        self.lost_timeout = 1.5



    def get_face(self):

        ret, frame = self.camera.read()

        if not ret:
            return {
                "found": False
            }


        h, w = frame.shape[:2]


        # Prepare image for SSD network
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0,
            (300, 300),
            (104, 177, 123)
        )


        self.net.setInput(blob)

        detections = self.net.forward()


        best_confidence = 0
        best_face = None


        # Find highest confidence face
        for i in range(detections.shape[2]):

            confidence = detections[0, 0, i, 2]


            if confidence > 0.5 and confidence > best_confidence:

                box = detections[0, 0, i, 3:7] * [
                    w,
                    h,
                    w,
                    h
                ]

                x1, y1, x2, y2 = box.astype(int)


                best_face = (
                    (x1 + x2) // 2,
                    (y1 + y2) // 2
                )


                best_confidence = confidence



        # Face found
        if best_face:

            x, y = best_face


            target_x = x / w
            target_y = y / h


            # Smooth movement
            self.smooth_x += (
                target_x - self.smooth_x
            ) * self.smoothing


            self.smooth_y += (
                target_y - self.smooth_y
            ) * self.smoothing


            self.last_seen = time.time()
            print(
                "FACE PIXELS:",
                x,
                y,
                "IMAGE:",
                w,
                h
            )

            return {
                "found": True,
                "x": self.smooth_x,
                "y": self.smooth_y,
                "confidence": float(best_confidence)
            }



        # No face detected
        return {
            "found": False,
            "x": self.smooth_x,
            "y": self.smooth_y,
            "confidence": 0
        }



    def close(self):

        self.camera.release()