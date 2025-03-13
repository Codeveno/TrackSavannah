import sys
import os
sys.path.append(os.path.join(os.getcwd(), "yolov5"))  # Correct YOLOv5 path

import torch
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.general import check_img_size

def load_yolo_model():
    """
    Load the YOLOv5 model using your custom-trained weights (best.pt).
    """
    model = DetectMultiBackend("models/best.pt", device=torch.device('cpu'))
    model.warmup(imgsz=(1, 3, 640, 640))  # Warm-up for stable model initialization
    return model
