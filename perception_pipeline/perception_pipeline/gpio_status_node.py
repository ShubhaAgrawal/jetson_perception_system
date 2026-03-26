import rclpy
from rclpy.node import Node
import Jetson.GPIO as GPIO
import threading

# Physical pin numbers (BOARD Mode)
PIN_LED_BLUE = 15   # GPIO12 -- booting
PIN_LED_GREEN = 33  # GPIO13 -- running
PIN_LED_RED = 29    # GPIO01 -- error
PIN_BUTTON = 32     # GPIO07 -- start/stop trigger

class GPIOStatusNode(Node):
    def __init__(self):
        super().__init__('gpio_status_node')

        # --- GPIO setup ---
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        # LEDs are outputs
        GPIO.setup(PIN_LED_BLUE, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PIN_LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PIN_LED_RED, GPIO.OUT, initial=GPIO.LOW)

        # Button is an input
        GPIO.setup(PIN_BUTTON, GPIO.IN)

        self._running = False
        self._button_lock = threading.Lock()
        self._set_leds(blue=True, green=False, red=False)
        self.get_logger().info('GPIO status node started - showing BOOTING (blue)')

        GPIO.add_event_detect(PIN_BUTTON, GPIO.FALLING, callback=self._button_callback, bouncetime=300)

        self._boot_timer = self.create_timer(2.0, self._boot_complete)

    def _set_leds(self, blue=False, green=False, red=False):
        GPIO.output(PIN_LED_BLUE, GPIO.HIGH if blue else GPIO.LOW)
        GPIO.output(PIN_LED_GREEN, GPIO.HIGH if green else GPIO.LOW)
        GPIO.output(PIN_LED_RED, GPIO.HIGH if red else GPIO.LOW)

    def set_error(self):
        """Call this from other nodes to signal an error state."""
        self._running = False
        self._set_leds(blue=False, green=False, red=True)
        self.get_logger().error('ERROR state - showing red LED')

    def _boot_complete(self):
        self._boot_timer.cancel()
        self._running = True
        self._set_leds(blue=False, green=True, red=False)
        self.get_logger().info('Boot complete - showing RUNNING (green)')

    def _button_callback(self, channel):
        with self._button_lock:
            self._running = not self._running

            if self._running:
                self._set_leds(blue=False, green=True, red=False)
                self.get_logger().info('Button presses - RUNNING (green)')

            else:
                self._set_leds(blue=False, green=False, red=False)
                self.get_logger().info('Button pressed - STOPPED (all off)')

    def destroy_node(self):
        self._set_leds(blue=False, green=False, red=False)
        GPIO.cleanup()
        self.get_logger().info('GPIO cleaned up')
        super().destroy_node()

def main(args=None):
    rclpy.init()
    node = GPIOStatusNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()