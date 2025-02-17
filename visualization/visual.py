from calibration import calibration
from visualization import clean_radar_data
from visualization import util

intrinsic_matrix, wwm_extrinsics_matrix = calibration.calibration_mmw_radar_camera()

model = clean_radar_data.common_read("")

calibration_points = clean_radar_data.get_calibration_result(intrinsic_matrix, wwm_extrinsics_matrix, model)


util.draw_points_on_picture()



##






