import os
import sys
import math
import time
import pygame
import cv2

net = cv2.dnn.readNetFromCaffe(
    "/home/jetbot/face_model/deploy.prototxt",
    "/home/jetbot/face_model/res10_300x300_ssd_iter_140000.caffemodel"
)

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1280,
    capture_height=720,
    display_width=320,
    display_height=240,
    framerate=21,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.display.init()

last_face_time = 0
last_target_x = 0.0
last_target_y = 0.0
FACE_HOLD_TIME = 0.5  # seconds

WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Eyes")

clock = pygame.time.Clock()

eye_radius = int(HEIGHT * 0.2)
pupil_radius = int(eye_radius * 0.35)
max_pupil_offset = eye_radius - pupil_radius - 12

left_eye_center = (int(WIDTH * 0.3), int(HEIGHT * 0.5))
right_eye_center = (int(WIDTH * 0.7), int(HEIGHT * 0.5))

smooth_x = 0.0
smooth_y = 0.0
SMOOTHING = 0.3

print("Opening camera...")
#cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
#if not cap.isOpened():
#    print("V4L2 open failed, trying default backend...")
#    cap = cv2.VideoCapture(0)

#if not cap.isOpened():
#    print("ERROR: Could not open camera")
#    pygame.display.quit()
#    sys.exit(1)

#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

print("Opening CSI camera with GStreamer pipeline...")
pipeline = gstreamer_pipeline()

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("ERROR: Could not open CSI camera with GStreamer")
    pygame.display.quit()
    sys.exit(1)

print("CSI camera opened successfully")

#print("Camera opened successfully")

cascade_path = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
if not os.path.exists(cascade_path):
    cascade_path = "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml"

print("Using cascade:", cascade_path)

# face_cascade = cv2.CascadeClassifier(cascade_path)
# if face_cascade.empty():
#    print("ERROR: Could not load Haar cascade")
#    cap.release()
#    pygame.display.quit()
#    sys.exit(1)

def clamp_pupil_offset(dx, dy, max_dist):
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > max_dist and dist > 0:
        scale = max_dist / dist
        dx *= scale
        dy *= scale
    return dx, dy

def draw_eye(center, offset_x, offset_y):
    cx, cy = center
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy), eye_radius)
    pupil_x = int(cx + offset_x)
    pupil_y = int(cy + offset_y)
    pygame.draw.circle(screen, (0, 0, 0), (pupil_x, pupil_y), pupil_radius)

frame_count = 0
last_debug_print = time.time()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ok, frame = cap.read()
    frame_count += 1

    target_x = 0.0
    target_y = 0.0
    faces_found = 0

    if not ok or frame is None:
        if time.time() - last_debug_print > 1.0:
            print("WARNING: camera read failed")
            last_debug_print = time.time()
    else:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Improve contrast in low light
        gray = cv2.equalizeHist(gray)

        # faces = face_cascade.detectMultiScale(
        #    gray,
        #    scaleFactor=1.15,
        #    minNeighbors=3,
        #    minSize=(30, 30)
        #)

        # faces_found = len(faces)

        # if faces_found > 0:
        #    if time.time() - last_debug_print > 1.0:
        #        print("ok={ok} faces={faces_found} smooth=({smooth_x:.1f},{smooth_y:.1f})")
        #        last_debug_print = time.time()
        #    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        #    face_x = x + w / 2.0
        #    face_y = y + h / 2.0
        #    cam_h, cam_w = gray.shape

        #    norm_x = (face_x - cam_w / 2.0) / (cam_w / 2.0)
        #    norm_y = (face_y - cam_h / 2.0) / (cam_h / 2.0)

            # not sure about putting this here!!!
            # if abs(norm_x) < 0.1:
            #    norm_x = 0
            # if abs(norm_y) < 0.1:
            #    norm_y = 0

        #    target_x = norm_x * max_pupil_offset * 1.6
        #    target_y = norm_y * max_pupil_offset * 1.2

        (h, w) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )

        net.setInput(blob)
        detections = net.forward()

        faces_found = 0
        target_x = 0.0
        target_y = 0.0

        best_conf = 0
        best_center = None

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.4:
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (x1, y1, x2, y2) = box.astype("int")

                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                if confidence > best_conf:
                    best_conf = confidence
                    best_center = (cx, cy)

        now = time.time()

        if best_center is not None:
            faces_found = 1
            cx, cy = best_center

            norm_x = (cx - w / 2) / (w / 2)
            norm_y = (cy - h / 2) / (h / 2)

            target_x = -norm_x * max_pupil_offset * 1.6
            target_y = norm_y * max_pupil_offset * 1.2

            last_target_x = target_x
            last_target_y = target_y
            last_face_time = now

        else:
            # No face this frame — hold previous position briefly
            if now - last_face_time < FACE_HOLD_TIME:
                target_x = last_target_x
                target_y = last_target_y
                faces_found = 1  # treat as still tracking
            else:
                target_x = 0.0
                target_y = 0.0
                faces_found = 0

        if time.time() - last_debug_print > 1.0:
            print(f"frame={frame_count} ok={ok} faces={faces_found}")
            print(f"target=({target_x:.1f},{target_y:.1f})")
            last_debug_print = time.time()

    target_x, target_y = clamp_pupil_offset(target_x, target_y, max_pupil_offset)

    smooth_x += (target_x - smooth_x) * SMOOTHING
    smooth_y += (target_y - smooth_y) * SMOOTHING

    screen.fill((0, 0, 0))
    draw_eye(left_eye_center, smooth_x, smooth_y)
    draw_eye(right_eye_center, smooth_x, smooth_y)

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.display.quit()
sys.exit()
