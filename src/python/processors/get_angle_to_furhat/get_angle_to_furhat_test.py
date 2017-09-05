from unittest.mock import MagicMock
from get_angle_to_furhat import calculate_angle

# Assuming furhat is Participant A

furhat_position = {"x": 0, "y": 0, "z": 0, "qx": 0, "qy": 0, "qz": 0, "qw": 0}

result_2 = calculate_angle(
    furhat_position, {"x": 0, "y": 0, "z": 0, "qx": 0, "qy": 0, "qz": 0, "qw": 0}
)
result_1 = calculate_angle(
    furhat_position, {"x": 0, "y": 0, "z": 0, "qx": 0, "qy": 0, "qz": 0, "qw": 0}
)
result_3 = calculate_angle(
    furhat_position, {"x": 0, "y": 0, "z": 0, "qx": 0, "qy": 0, "qz": 0, "qw": 0}
)
result_4 = calculate_angle(
    furhat_position, {"x": 0, "y": 0, "z": 0, "qx": 0, "qy": 0, "qz": 0, "qw": 0}
)

assert result_1 == {'furhat_gaze_angle': (0, 0, 0)}
assert result_2 == {'furhat_gaze_angle': (0, 0, 0)}
assert result_3 == {'furhat_gaze_angle': (0, 0, 0)}
assert result_4 == {'furhat_gaze_angle': (0, 0, 0)}
