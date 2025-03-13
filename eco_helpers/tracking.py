from deep_sort_realtime.deepsort_tracker import DeepSort

# Initialize DeepSORT tracker correctly
tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0)

def track_objects(detections, frame):
    """
    Tracks detected animals using DeepSORT.
    Returns tracked objects with IDs and bounding box data.
    """
    dets = [
        {
            "tlwh": (x1, y1, x2 - x1, y2 - y1),
            "confidence": conf,
            "class": cls
        }
        for x1, y1, x2, y2, conf, cls in detections
    ]

    tracked_objects = tracker.update_tracks(dets, frame=frame)
    return tracked_objects
