import rclpy
from rclpy.node import Node
from perception_msgs.msg import Detection, DetectionArray
from cv_bridge import CvBridge
import time
from ultralytics import YOLO
from sensor_msgs.msg import Image

class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        # Subscribe to camera frames
        self.subscriptions_ = self.create_subscription(Image, '/camera/rgb', self.detection_callback, 10)

        # Publish detections
        self.detection_pub_ = self.create_publisher(DetectionArray, '/detections', 10)

        # Publish annoated image (with bounding boxes drawn on it)
        self.image_pub_ = self.create_publisher(Image, '/camera/detections', 10)

        # Load TensorRT model
        self.model = YOLO('/home/shubha/jetson_perception_system/models/yolov8n_fp16.engine')
        self.bridge = CvBridge()

        # Performance tracking
        self.frame_count = 0
        self.total_inference_time = 0.0

        self.get_logger().info('Detection Node started - TensorRT FP16 loaded')

    def detection_callback(self,msg):
        # Convert ROS2 image to OpenCV format
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Run inference and measure time
        start = time.time()
        results = self.model(frame, verbose = False, conf=0.5)
        inference_time = (time.time() - start)*1000  # in ms

        # Track performance
        self.frame_count+=1
        self.total_inference_time+=inference_time
        if self.frame_count%100 == 0:
            avg = self.total_inference_time/self.frame_count
            self.get_logger().info(
                f'Frames: {self.frame_count} |'
                f'Avg inference: {avg:.1f}ms |'
                f'FPS: {1000/avg:.1f}')
            
        # Build detection array message
        det_array = DetectionArray()
        det_array.header = msg.header

        for result in results:
            for box in result.boxes:
                det = Detection()
                det.header = msg.header
                det.class_id = int(box.cls[0])
                det.class_name = self.model.names[int(box.cls[0])]
                det.confidence = float(box.conf[0])
                det.x1 = float(box.xyxy[0][0])
                det.y1 = float(box.xyxy[0][1])
                det.x2 = float(box.xyxy[0][2])
                det.y2 = float(box.xyxy[0][3])
                det_array.detections.append(det)

        # Publish detetctions
        self.detection_pub_.publish(det_array)

        # Publish annoated images
        annoated = results[0].plot()
        annoated_msg = self.bridge.cv2_to_imgmsg(annoated, encoding='bgr8')
        annoated_msg.header = msg.header
        self.image_pub_.publish(annoated_msg)

def main(args=None):
        rclpy.init(args=args)
        node = DetectionNode()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
        


        
