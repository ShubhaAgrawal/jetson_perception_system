import depthai as dai
import cv2

pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.Camera)
cam.build()
out = cam.requestOutput(size=(640, 480), fps=30.0)
q = out.createOutputQueue()

pipeline.start()

print('OAK-D Lite streaming! Press q to quit.')
while True:
    frame = q.get().getCvFrame()
    cv2.imshow('OAK-D RGB', frame)
    if cv2.waitKey(1) == ord('q'):
        break

pipeline.stop()
cv2.destroyAllWindows()