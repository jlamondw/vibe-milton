"""
Robot Eyes

Displays a pair of animated eyes that track the most prominent
face detected by the Jetson Nano CSI camera.

Components:
- Pygame: eye rendering
- OpenCV DNN: face detection
- CSI camera via GStreamer

Behavior:
- Tracks the highest-confidence detected face
- Smooths eye motion
- Holds the last face position briefly when detection flickers
"""

import os
import sys
import math
import time

import cv2
import pygame


# ---------------------------------------------------------------------------
# Face detector
# ---------------------------------------------------------------------------

net = cv2.dnn.readNetFromCaffe(
    "/home/jetbot/face_model/deploy.prototxt",
    "/home/jetbot/face_model/res10_300x300_ssd_iter_140000.caffemodel"
)


# ---------------------------------------------------------------------------
# Camera pipeline
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Pygame setup
# ---------------------------------------------------------------------------

os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.display.init()

WIDTH, HEIGHT = 800, 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Eyes")

clock = pygame.time.Clock()


# ---------------------------------------------------------------------------
# Eye configuration
# ---------------------------------------------------------------------------

# Basic eye dimensions.
eye_radius = int(HEIGHT * 0.20)
pupil_radius = int(eye_radius * 0.35)

# Maximum distance pupils can move from eye center.
max_pupil_offset = eye_radius - pupil_radius - 12

left_eye_center = (int(WIDTH * 0.30), int(HEIGHT * 0.50))
right_eye_center = (int(WIDTH * 0.70), int(HEIGHT * 0.50))

# Smoothed eye position.
smooth_x = 0.0
smooth_y = 0.0

# Higher = smoother but slower.
# Lower = faster but more twitchy.
SMOOTHING = 0.30


# ---------------------------------------------------------------------------
# Face tracking state
# ---------------------------------------------------------------------------

# Hold the last known face position briefly to prevent
# eye jitter when detection flickers.
FACE_HOLD_TIME = 0.5

last_face_time = 0.0
last_target_x = 0.0
last_target_y = 0.0


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def clamp_pupil_offset(dx, dy, max_dist):
    """Keep pupils inside the eye."""
    dist = math.sqrt(dx * dx + dy * dy)

    if dist > max_dist and dist > 0:
        scale = max_dist / dist
        dx *= scale
        dy *= scale

    return dx, dy


def draw_eye(center, offset_x, offset_y):
    """Draw a single eye."""

    cx, cy = center

    pygame.draw.circle(
        screen,
        (255, 255, 255),
        (cx, cy),
        eye_radius
    )

    pupil_x = int(cx + offset_x)
    pupil_y = int(cy + offset_y)

    pygame.draw.circle(
        screen,
        (0, 0, 0),
        (pupil_x, pupil_y),
        pupil_radius
    )


# ---------------------------------------------------------------------------
# Camera startup
# ---------------------------------------------------------------------------

print("Starting robot eyes...")
print("Opening CSI camera...")

pipeline = gstreamer_pipeline()

cap = cv2.VideoCapture(
    pipeline,
    cv2.CAP_GSTREAMER
)

if not cap.isOpened():
    print("ERROR: Could not open CSI camera")
    pygame.display.quit()
    sys.exit(1)

print("Camera ready")
print("Face detector loaded")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

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

        (h, w) = frame.shape[:2]

        # Run OpenCV SSD face detector.
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )

        net.setInput(blob)
        detections = net.forward()

        best_conf = 0.0
        best_center = None

        # Find the highest-confidence face.
        for i in range(detections.shape[2]):

            confidence = detections[0, 0, i, 2]

            if confidence > 0.4:

                box = detections[0, 0, i, 3:7] * [w, h, w, h]

                x1, y1, x2, y2 = box.astype("int")

                cx = (x1 + x2) / 2.0
                cy = (y1 + y2) / 2.0

                if confidence > best_conf:
                    best_conf = confidence
                    best_center = (cx, cy)

        now = time.time()

        if best_center is not None:

            faces_found = 1

            cx, cy = best_center

            # Convert face position into normalized coordinates.
            norm_x = (cx - w / 2) / (w / 2)
            norm_y = (cy - h / 2) / (h / 2)

            # Convert normalized position into pupil movement.
            target_x = -norm_x * max_pupil_offset * 1.6
            target_y = norm_y * max_pupil_offset * 1.2

            last_target_x = target_x
            last_target_y = target_y
            last_face_time = now

        else:

            # Face temporarily lost.
            # Continue looking at the previous location for a short time.
            if now - last_face_time < FACE_HOLD_TIME:

                target_x = last_target_x
                target_y = last_target_y
                faces_found = 1

            else:

                target_x = 0.0
                target_y = 0.0
                faces_found = 0

        if time.time() - last_debug_print > 1.0:

            print(
                f"faces={faces_found} "
                f"target=({target_x:.0f},{target_y:.0f}) "
                f"smooth=({smooth_x:.0f},{smooth_y:.0f})"
            )

            last_debug_print = time.time()

    # Keep pupils inside the eye.
    target_x, target_y = clamp_pupil_offset(
        target_x,
        target_y,
        max_pupil_offset
    )

    # Smooth movement so eyes don't jump instantly.
    smooth_x += (target_x - smooth_x) * SMOOTHING
    smooth_y += (target_y - smooth_y) * SMOOTHING

    # Draw eyes.
    screen.fill((0, 0, 0))

    draw_eye(
        left_eye_center,
        smooth_x,
        smooth_y
    )

    draw_eye(
        right_eye_center,
        smooth_x,
        smooth_y
    )

    pygame.display.flip()
    clock.tick(30)


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

cap.release()
pygame.display.quit()
sys.exit()