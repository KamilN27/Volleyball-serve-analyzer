# Models

This directory is intended for storing model weights used in the project.

## Required models

### YOLOv8 (ball detection)

Download trained weights or base model from:
https://docs.ultralytics.com/models/yolov8/

Place the file here, for example:
models/yolo/best.pt

---

### SAM2 (tracking / segmentation)

Download the SAM2 checkpoint from:
https://ai.meta.com/research/sam2/

Place the checkpoint file here, for example:
models/sam2/sam2.pt

---

## Notes

- Model weights are not included in the repository due to size limitations.
- Make sure paths in the code match the downloaded files.
