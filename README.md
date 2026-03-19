# Real-Time 3D Perception System — Jetson Orin Nano Super

A production-grade perception system on NVIDIA Jetson Orin Nano Super, combining TensorRT-optimized object detection with ROS2 middleware for real-time robotic perception.

**Status:** Work in progress — detection pipeline complete, tracking and depth fusion coming next.

---

## System Architecture
```
USB Camera
    │
    ▼
camera_node (ROS2)
    │
    │  publishes /camera/rgb (sensor_msgs/Image)
    │
    ▼
detection_node (ROS2)
    │
    │  YOLOv8n TensorRT FP16 inference
    │
    ├──► /detections (perception_msgs/DetectionArray)
    │
    └──► /camera/detections (annotated Image)
             │
             ▼
        viewer_node (ROS2)
        (displays annotated feed)
```

---

## Performance Benchmarks

### Detection Pipeline (YOLOv8n TensorRT FP16)
| Metric | Value |
|--------|-------|
| Model | YOLOv8n |
| Precision | FP16 (TensorRT) |
| Avg Inference Time | ~26 ms |
| Inference FPS | ~38 FPS |
| Detection Publish Rate | ~29 FPS |
| Input Resolution | 640x480 |

### System Resources (during detection pipeline)
| Metric | Value |
|--------|-------|
| CPU Usage | ~20% avg across 6 cores |
| GPU Usage | Variable (2–46%) |
| Memory | 2.3 GB / 7.4 GB |
| CPU Temperature | ~48°C |
| GPU Temperature | ~48.5°C |
| Power | ~985 mW avg |

---

## Hardware

- NVIDIA Jetson Orin Nano Super Developer Kit
- USB Webcam (640x480 @ 30 FPS, MJPG)
- OAK-D Lite (coming soon — for stereo depth)

## Software Stack

- **JetPack** 6.1 (L4T R36.4.7)
- **ROS2** Humble
- **Python** 3.10
- **YOLOv8n** via Ultralytics
- **TensorRT** 10.3.0 (FP16)
- **OpenCV** 4.x

---

## Project Structure
```
jetson_perception_system/
├── perception_pipeline/          # ROS2 Python package
│   ├── perception_pipeline/
│   │   ├── camera_node.py        # USB camera publisher
│   │   ├── detection_node.py     # TensorRT YOLOv8 inference
│   │   └── viewer_node.py        # Display subscriber
│   ├── launch/
│   │   └── perception.launch.py  # Multi-node launcher
│   ├── setup.py
│   └── package.xml
├── perception_msgs/              # Custom ROS2 message definitions
│   └── msg/
│       ├── Detection.msg         # Single detection (class, confidence, bbox)
│       └── DetectionArray.msg    # Array of detections per frame
├── models/
│   └── yolov8n_fp16.engine       # TensorRT FP16 engine (not tracked in git)
├── benchmarks/
│   └── week1_baseline.md
├── docs/
└── README.md
```

---

## Setup

### Prerequisites
- NVIDIA Jetson Orin Nano Super with JetPack 6.x
- ROS2 Humble installed
- USB webcam

### Install Dependencies
```bash
# ROS2 Humble (if not already installed)
sudo apt install ros-humble-desktop

# Python dependencies
pip3 install ultralytics paho-mqtt "onnx<2.0.0" onnxslim

# Build tools
sudo apt install python3-colcon-common-extensions
```

### Build
```bash
# Clone the repo
git clone https://github.com/ShubhaAgrawal/jetson_perception_system.git

# Symlink packages into ROS2 workspace
ln -s ~/jetson_perception_system/perception_pipeline ~/ros2_ws/src/perception_pipeline
ln -s ~/jetson_perception_system/perception_msgs ~/ros2_ws/src/perception_msgs

# Build
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### Export TensorRT Engine
```bash
python3 -c "
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.export(format='engine', half=True, device=0, simplify=True)
"
mv yolov8n.engine models/yolov8n_fp16.engine
```

### Run
```bash
# Launch all nodes
ros2 launch perception_pipeline perception.launch.py

# Or run individually
ros2 run perception_pipeline camera_node
ros2 run perception_pipeline detection_node
ros2 run perception_pipeline viewer_node
```

---

## Roadmap

- [x] ROS2 workspace and camera pipeline
- [x] Custom detection messages (perception_msgs)
- [x] YOLOv8n TensorRT FP16 detection node
- [ ] Multi-object tracking with persistent IDs
- [ ] OAK-D Lite depth integration
- [ ] 3D object localization (RGB + depth fusion)
- [ ] Occupancy grid generation
- [ ] Real-time scheduling and WCET analysis
- [ ] Power/thermal management and watchdog
- [ ] Boot-to-inference optimization
- [ ] C++ rewrite of performance-critical nodes

---

## Related Project

- [jetson_vision_gpio](https://github.com/ShubhaAgrawal/jetson_vision_gpio) — Edge AI person detection with TensorRT, GPIO control, and MQTT/Node-RED dashboard
