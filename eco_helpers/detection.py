

from eco_helpers.yolo import load_yolo_model


# Load YOLOv5 model
model = load_yolo_model()

def detect_animals(frame):
    """
    Detect animals using YOLOv5.
    Returns a list of detections: [(x1, y1, x2, y2, confidence, class_id), ...]
    """
    results = model(frame)  # Updated from `.predict()` to direct callable inference

    detections = []
    for result in results.pred[0]:  # Corrected to `.pred[0]` for accessing predictions
        x1, y1, x2, y2, conf, cls = map(float, result[:6])
        if conf > 0.5:
            detections.append((int(x1), int(y1), int(x2), int(y2), conf, int(cls)))

    return detections
