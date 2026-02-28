import rclpy
import cv2
import time
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image

class ViewerNode(Node):
    def __init__(self):
        super().__init__('viewer_node')
        self.subscription_ = self.create_subscription(Image, '/camera/rgb', self.listener_callback, 10)
        self.bridge = CvBridge()
        self.prev_time = time.time()
        self.get_logger().info('Viewer Node Started')

    def listener_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        # Calculate and display latency
        now = time.time()
        fps = 1.0/(now-self.prev_time) if (now-self.prev_time)>0 else 0
        self.prev_time = now
        cv2.putText(frame, f'FPS: {fps:.1f}', (10,30), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
        cv2.imshow('Perception Pipeline - Viewer', frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ViewerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
