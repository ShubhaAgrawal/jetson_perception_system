import cv2
import numpy as np
import depthai as dai

pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.Camera)
cam.build()

rgb_out = cam.requestOutput(size = (640, 480), fps = 30.0)
rgb_q = rgb_out.createOutputQueue()

left = pipeline.create(dai.node.MonoCamera)
left.setBoardSocket(dai.CameraBoardSocket.CAM_B)

right = pipeline.create(dai.node.MonoCamera)
right.setBoardSocket(dai.CameraBoardSocket.CAM_C)

stereo = pipeline.create(dai.node.StereoDepth)
stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
stereo.setOutputSize(640, 480)
left.out.link(stereo.left)
right.out.link(stereo.right)

aligned_q = stereo.depth.createOutputQueue()

pipeline.start()

print('RGB + Depth streaming! Press q to quit.')

while True:
    rgb_frames = rgb_q.get().getCvFrame()
    depth_frames = aligned_q.get().getFrame()
    print(f"Depth min: {depth_frames.min()}, max: {depth_frames.max()}")

    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_frames, alpha=0.03), cv2.COLORMAP_JET)
    combined = np.hstack((rgb_frames, depth_colormap))
    cv2.imshow('RGB | Aligned depth', combined)

    if cv2.waitKey(1) == ord('q'):
        break

pipeline.stop()
cv2.destroyAllWindows()

