import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import depthai as dai
import numpy as np

class OakDCameraNode(Node):
    """
    ROS2 node that streams synchronized RGB + aligned depth
    from OAK-D Lite and publishes them as ROS2 Image topics.
    """

    def __init__(self):
        super().__init__('oakd_camera_node')

        # Publishers
        self.rgb_pub = self.create_publisher(Image, '/camera/rgb', 10)
        self.depth_pub = self.create_publisher(Image, '/camera/depth', 10)
        self.bridge = CvBridge()

        # Build DepthAI pipeline
        self.pipeline = dai.Pipeline()

        # RGB Camera
        cam = self.pipeline.create(dai.node.Camera)
        cam.build()
        rgb_out = cam.requestOutput(size = (640, 480), fps= 30.0)
        self.rgb_q = rgb_out.createOutputQueue()

        # Stereo Cameras
        left = self.pipeline.create(dai.node.MonoCamera)
        left.setBoardSocket(dai.CameraBoardSocket.CAM_B)

        right = self.pipeline.create(dai.node.MonoCamera)
        right.setBoardSocket(dai.CameraBoardSocket.CAM_C)

        # Stereo depth aligned to RGB
        stereo = self.pipeline.create(dai.node.StereoDepth)
        stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
        stereo.setOutputSize(640, 480)
        left.out.link(stereo.left)
        right.out.link(stereo.right)

        self.depth_q = stereo.depth.createOutputQueue()

        # Start the OAK-D pipeline
        self.pipeline.start()
        self.get_logger().info('OAK-D Lite pipeline started')

        # Timer to poll frames at 30 fps
        self.timer = self.create_timer(1.0/30.0, self.timer_callback)

    def timer_callback(self):
        """Grab RGB + depth frames and publish as ROS2 messages."""

        # Get RGB frames
        rgb_msg = self.rgb_q.tryGet()
        if rgb_msg is not None:
            rgb_frame = rgb_msg.getCvFrame()
            ros_rgb = self.bridge.cv2_to_imgmsg(rgb_frame, encoding='bgr8')
            ros_rgb.header.stamp = self.get_clock().now().to_msg()
            ros_rgb.header.frame_id = 'oakd_rgb'
            self.rgb_pub.publish(ros_rgb)

        # Get aligned depth frame
        depth_msg = self.depth_q.tryGet()
        if depth_msg is not None:
            depth_frame = depth_msg.getFrame()
            ros_depth = self.bridge.cv2_to_imgmsg(depth_frame, encoding='16UC1')
            ros_depth.header.stamp = self.get_clock().now().to_msg()
            ros_depth.header.frame_id = 'oakd_depth'
            self.depth_pub.publish(ros_depth)

    def destroy_node(self):
        """Clean shutdown of OAK-D pipeline."""
        self.pipeline.stop()
        self.get_logger().info('OAKD Lite pipeline stopped')
        return super().destroy_node()
    
def main(args=None):
    rclpy.init(args=args)
    node = OakDCameraNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
