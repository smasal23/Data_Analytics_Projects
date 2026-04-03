# Dataset Description

## Classification Dataset
Expected directory layout:

classification_dataset/
├── train/
│   ├── Bird/
│   └── Drone/
├── valid/
│   ├── Bird/
│   └── Drone/
└── test/
    ├── Bird/
    └── Drone/

Each file is expected to be a `.jpg` image.

## Detection Dataset
Expected YOLO-style layout:

object_detection_dataset/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/

Each image should have a matching `.txt` annotation file with YOLO rows:
<class_id> <x_center> <y_center> <width> <height>