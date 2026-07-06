import pygame
import time

from display import Display
from state import RobotState

display = Display()

state = RobotState()

running = True

last_change = time.time()

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    elapsed = time.time() - last_change

    if elapsed > 3:

        if state.mode == state.MODE_EYES:

            state.mode = state.MODE_LISTENING

        elif state.mode == state.MODE_LISTENING:

            state.mode = state.MODE_THINKING

        elif state.mode == state.MODE_THINKING:

            state.mode = state.MODE_MESSAGE

            state.message = (
                "Hello Jared!\n\n"
                "I'm your Jetbot."
            )

        else:

            state.mode = state.MODE_EYES

        last_change = time.time()

    display.update(state)

pygame.quit()