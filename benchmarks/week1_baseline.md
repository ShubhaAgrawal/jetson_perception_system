# Week 1 Baseline Benchmarks

## Camera Pipeline
- Webcam resolution: 640x480
- Format: MJPG
- Publish rate: ~30 FPS
- ROS2 topic: /camera/rgb

## System Resources (during camera pipeline)
- CPU usage: ~20% average across 6 cores
- GPU usage: 2-46% (variable, no inference running)
- Memory: 2.3GB / 7.4GB
- CPU temp: ~48°C
- GPU temp: ~48.5°C
- Power: ~985mW avg (CPU + GPU + CV)

## Notes
- GPU usage spikes likely from OpenCV display rendering in viewer node
- Baseline with no ML inference — will compare against TensorRT detection in Week 3
