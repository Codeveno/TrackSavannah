import cv2

# Animal class names (from the best.pt model)
CLASS_NAMES = [
    'tiger', 'giraffe', 'bear', 'lion', 'elephant',
    'deer', 'wolf', 'bull', 'monkey', 'leopard',
    'rhinoceros', 'hippo', 'cattle'
]

def draw_tracks(frame, tracks):
    """
    Draws bounding boxes and labels on the frame for tracked objects.
    """
    for track in tracks:
        if track.is_confirmed() and track.time_since_update == 0:
            track_id = track.track_id
            bbox = track.to_ltwh()
            x, y, w, h = map(int, bbox)

            # Ensure class ID is within range; otherwise, label as 'Unknown'
            label = CLASS_NAMES[track.det_class] if track.det_class < len(CLASS_NAMES) else "Unknown"
            color = (0, 255, 0)

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            # Display label with track ID
            text = f"{label} ID:{track_id}"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return frame
