from display import Display
import time

display = Display()

try:
    while True:
        display.update()
        time.sleep(0.01)

except KeyboardInterrupt:
    pass

finally:
    display.close()