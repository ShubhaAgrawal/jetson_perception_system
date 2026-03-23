import depthai as dai
import numpy as np
import cv2

pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.Camera)
cam.build()

rgb_out = cam.requestOutput(size=(640, 480), fps=30.0)
rgb_q = rgb_out.createOutputQueue()

left = pipeline.create(dai.node.MonoCamera)
left.setBoardSocket(dai.CameraBoardSocket.CAM_B)

right = pipeline.create(dai.node.MonoCamera)
right.setBoardSocket(dai.CameraBoardSocket.CAM_C)

stereo = pipeline.create(dai.node.StereoDepth)
stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
stereo.setOutputSize(640, 480)
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.FAST_DENSITY)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
stereo.setLeftRightCheck(True)
stereo.setExtendedDisparity(False)
stereo.setSubpixel(False)

left.out.link(stereo.left)
right.out.link(stereo.right)

depth_q = stereo.depth.createOutputQueue()

pipeline.start()

print('Depth quality test - press q to quit')
print('Move objects to different distances and observe')

while True:
    rgb_frames = rgb_q.get().getCvFrame()
    depth_frames = depth_q.get().getFrame()

    # ------ Quality Metrics -------
    total_pixels = depth_frames.size
    zero_pixels = np.count_nonzero((depth_frames == 0) | (depth_frames == 65535))
    valid_pixels = total_pixels - zero_pixels
    holes_present = (zero_pixels/total_pixels) * 100
    valid_depth = depth_frames[(depth_frames > 0) & (depth_frames < 10000)]

    if valid_depth.size > 0:
        min_mm = valid_depth.min()
        max_mm = valid_depth.max()
        mean_mm = valid_depth.mean()
        std_mm = valid_depth.std()

    else:
        min_mm = max_mm = mean_mm = std_mm = 0

    # Print stats every frame
    print(f"Holes: {holes_present:.1f}% | "
      f"Range: {min_mm}mm - {max_mm}mm | "
      f"Mean: {mean_mm:.0f}mm | "
      f"StdDev: {std_mm:.0f}mm")

    # --- Visualize holes ---
    # White = valid depth, Black = holes
    hole_map = np.where(depth_frames == 0, 0, 255).astype(np.uint8)

    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_frames, alpha = 0.03), cv2.COLORMAP_JET)

    h, w = depth_frames.shape
    center_depth = depth_frames[h // 2, w // 2]
    cv2.circle(rgb_frames, (w //2, h //2), 5, (0, 255, 0), -1)
    
    center_region = depth_frames[h//4:3*h//4, w//4:3*w//4]
    center_holes = np.count_nonzero((center_region == 0)) / center_region.size * 100
    print(f"Center holes: {center_holes:.1f}% vs Overall: {holes_present:.1f}%")

    cv2.putText(rgb_frames, f"{center_depth}mm",
            (w // 2 + 10, h // 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    hole_map_colored = cv2.cvtColor(hole_map, cv2.COLOR_GRAY2BGR)

    top_row = np.hstack((rgb_frames, depth_colormap))
    bottom = cv2.resize(hole_map_colored, (1280, 480))
    combined = np.vstack((top_row, bottom))

    cv2.imshow('RGB | Depth | Holes (black = no depth)', combined)

    if cv2.waitKey(1) == ord('q'):
        break

pipeline.stop()
cv2.destroyAllWindows()