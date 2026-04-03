# Aerial Object Classification & Detection

An end-to-end computer vision project focused on:

- **Binary image classification** between **Bird** and **Drone**
- **Object detection** using YOLO-format annotations
- A reproducible **Google Colab + Google Drive** workflow
- GitHub-ready modular code structure

## Project Goals

1. Build a robust **classification pipeline** to distinguish Bird vs Drone.
2. Build an **object detection pipeline** using a YOLO-style dataset.
3. Maintain a professional workflow with:
   - modular source code
   - YAML-based configuration
   - notebook orchestration
   - reports and figures
   - test coverage

## Phase 1 Scope

Phase 1 covers:

- Colab workspace setup
- Google Drive integration
- project root creation
- persistent folder structure
- config scaffolding
- classification dataset audit
- detection dataset audit
- sample visualization
- dataset audit summary and report generation

## Project Structure

```text
Aerial_Object_Classification_Detection/
│
├── app/
├── configs/
├── data/
│   ├── raw/
│   │   ├── classification_dataset/
│   │   └── object_detection_dataset/
│   ├── interim/
│   │   ├── dataset_audit/
│   │   ├── previews/
│   │   └── label_checks/
│   └── processed/
├── docs/
├── figures/
│   └── dataset_audit/
├── models/
│   ├── classification/
│   └── detection/
├── notebooks/
├── reports/
├── src/
│   ├── data/
│   └── utils/
└── tests/