# Week 2 — OAK-D Lite Depth Quality Assessment

## Hardware
- OAK-D Lite (passive stereo, 7.5cm baseline)
- DepthAI v3.5.0
- Resolution: 640x480
- FPS: 30

## Stereo Configuration
- Preset: FAST_DENSITY
- Median Filter: KERNEL_7x7
- Left-Right Check: Enabled
- Extended Disparity: Disabled
- Subpixel: Disabled
- Depth aligned to RGB (CAM_A)

## Results

### General Scene (mixed distances, room environment)
| Metric | Before Filtering | After Filtering |
|--------|-----------------|-----------------|
| Holes (overall) | ~70% | ~50% |
| Holes (center region) | — | ~22% |
| Min depth | 363mm | 363mm |
| Max depth | 65535mm (invalid) | 8612mm |
| StdDev | ~4500mm | ~900mm |

### Flat Surface at ~1 Meter
| Metric | Value |
|--------|-------|
| Mean depth | ~1050mm |
| Accuracy | ~5% error |
| Holes (overall) | ~42% |
| Holes (center) | ~22% |

## Observations
- Passive stereo produces significant holes (~50% overall), especially at frame edges where stereo overlap is reduced
- Center region consistently performs better (~22% holes) than edges
- Textureless surfaces (plain walls) produce more holes than textured surfaces
- Minimum reliable depth is ~363mm, matching the spec (~35cm at 480P)
- Stereo filtering (median + left-right check) reduced holes by ~20% and dramatically reduced noise
- Depth accuracy at 1m is within 5%, suitable for object localization

## Impact on Pipeline
- For object detection + depth fusion, center-region depth quality (~78% valid) is sufficient
- Detection bounding boxes are typically in the center of the frame
- Using median depth within bounding boxes will further reduce noise
- Holes can be handled by falling back to "unknown distance" for that detection
