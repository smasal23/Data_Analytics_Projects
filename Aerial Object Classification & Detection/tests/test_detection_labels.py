from src.data.validate_detection_labels import validate_yolo_line


def test_valid_yolo_line():
    values = ["0", "0.5", "0.5", "0.2", "0.3"]
    is_valid, message = validate_yolo_line(values)
    assert is_valid is True
    assert message == "OK"


def test_invalid_yolo_line_length():
    values = ["0", "0.5", "0.5", "0.2"]
    is_valid, message = validate_yolo_line(values)
    assert is_valid is False


def test_invalid_yolo_range():
    values = ["0", "1.5", "0.5", "0.2", "0.3"]
    is_valid, message = validate_yolo_line(values)
    assert is_valid is False