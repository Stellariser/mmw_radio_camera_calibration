from calibration import corner_detection as cd
from calibration import util
from calibration import homography_operations as ho
from calibration import intrinsic_estimation as intr
from calibration import extrinsic_estimation as extr
from calibration import distortion_estimation as de
from calibration import parameter_refinement as pr
from calibration import util
import numpy as np
import pandas as pd
import cv2


def calibration_mmw_radar_camera():
    obj_points, img_points, img_shapes, img_names = cd.find_corners()

    refined_homographies = []
    for index in range(len(img_points)):
        util.info("Image Count: " + str(index + 1))
        h = ho.create_homography(img_points[index], obj_points[index])
        util.info("Homography:\n" + str(h) + "\n")
        h = ho.refine_homography(h, img_points[index], obj_points[index])
        util.info("Refined Homography:\n" + str(h) + "\n")
        refined_homographies.append(h)
        # analysis.plot_differences(img_points[index], obj_points[index], h, str(index + 1))

    A = intr.compute_intrinsics(refined_homographies)
    util.info("Camera Intrinsics:\n" + str(A) + "\n")

    # Once A is known, the extrinsic parameters for each image is readily computed.
    extrinsics = []
    for h_index in range(len(refined_homographies)):
        E = extr.compute_extrinsics(A, refined_homographies[h_index])
        util.info("Camera Extrinsic Matrix For Image-" + str(h_index + 1) + ":\n" + str(E) + "\n")
        extrinsics.append(E)

    # As the radial distortion is expected to be small, one would expect to estimate the other five intrinsic parameters,
    # using the Maximum likelihood estimation, reasonable well by simply ignoring distortion. One strategy is then to estimate
    # k1 and k2 after having estimated the other parameters, which will give us the ideal pixel coordinates.
    k = de.estimate_radial_distortion(obj_points, img_points, A, extrinsics)
    util.info("Radial Distortion: \n" + str(k) + "\n")

    K_opt, k_opt, extrinsics_opt = pr.refine(A, k, extrinsics, obj_points, img_points)
    util.info("Parameters:")
    print('\t   Focal Length: [ {:.5f}  {:.5f} ]'.format(K_opt[0, 0], K_opt[1, 1]))
    print('\tPrincipal Point: [ {:.5f}  {:.5f} ]'.format(K_opt[0, 2], K_opt[1, 2]))
    print('\t           Skew: [ {:.7f} ]'.format(K_opt[0, 1]))
    print('\t     Distortion: [ {:.6f}  {:.6f} ]'.format(k_opt[0], k_opt[1]))

    util.info("Projection Matrices for WebGL:\n")
    znear, zfar = .1, 1000.
    intrinsic_matrix = []
    for idx, e in enumerate(extrinsics_opt):
        p = util.get_camera_matrix(K_opt, e)
        util.info("P matrix for image " + str(idx + 1) + ":\n" + str(p))
        decomposed_p = util.decompose(p)
        webgl_p = util.to_opengl_projection(decomposed_p['intrinsic'], 0, 0, img_shapes[idx][0], img_shapes[idx][1],
                                            znear,
                                            zfar, direction="y down")
        intrinsic_matrix = decomposed_p['intrinsic']
        util.info("P matrix(WebGl) for image " + str(idx + 1) + ":\n" + str(webgl_p))

    wwm_extrinsics_matrix = extr.compute_wwm_extrinsics(np.array([0, -0.077, 0]))

    return intrinsic_matrix, wwm_extrinsics_matrix



# aaa = util.to_homogeneous_3d_multiple_points(obj_points[0])
# extr_answer = np.dot(util.to_homogeneous_3d_multiple_points(obj_points[0]), extrinsics_opt[0].T)
# inter_answer = np.dot(extr_answer, intrinsic_matrix.T)
#
#
# inter_answer = np.divide(inter_answer, inter_answer[:, 2].reshape(inter_answer.shape[0], 1))
#
#
# width = 0.3875
# height = 0.28
# x = -(width/2)
# y = -0.13
# z = 0.4
#
# a = util.create_sample_plane(width, height, x, y, z)
#
# model = np.column_stack((a, np.ones(a.shape[0])))
#
# tmpp = np.dot(model, wwm_extrinsics_matrix.T)
# tmp1 = np.dot(np.dot(model, wwm_extrinsics_matrix.T), intrinsic_matrix.T)
# tmp1 = np.divide(tmp1, tmp1[:, 2].reshape(tmp1.shape[0], 1))
# image = cv2.imread("./testData/image2.jpg")
# point_size = 1
# point_color = (0, 0, 255)  # BGR
# thickness = 4  # 0 、4、8
#
# for coor in tmp1:
#     cv2.circle(image, (int(coor[0]), int(coor[1])), point_size, point_color, thickness)
#
# cv2.imwrite('./testData/1.png', image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

# using plane for testing
# frame = pd.read_csv("../visualization/testData/pcl2.csv")
# frame[' Timestamp'] = pd.to_datetime(frame[' Timestamp'] / 1000, unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
# frame = frame[frame[' Timestamp'] == '2022-01-06 09:47:57']
# frame['union'] = 1
# frame = frame[frame[' ZPos'] >= 0.3]
# frame = frame[frame[' ZPos'] <= 1.0]
# frame = frame[frame[' Xpos'] <= 0.5]
# frame = frame[frame[' Xpos'] >= -0.5]
# frame = frame[frame[' YPos'] <= 0.3]
# frame = frame[frame[' YPos'] >= -0.3]


# posArray = frame[[' Xpos', ' YPos', ' ZPos', 'union']].to_numpy(dtype=float)
# tmp1 = np.dot(posArray, wwm_extrinsics_matrix.T)
# test1 = np.dot(np.dot(posArray, wwm_extrinsics_matrix.T), intrinsic_matrix.T)
# # normalize z axis
# test = np.divide(test1, test1[:, 2].reshape(test1.shape[0], 1))


# point_size = 1
# point_color = (0, 0, 255)  # BGR
# thickness = 4  # 0 、4、8
# image = cv2.imread("../visualization/testData/image3.jpg")
# for coor in test:
#     cv2.circle(image, (int(coor[0]), int(coor[1])), point_size, point_color, thickness)
#
# cv2.imwrite('../visualization/testData/6.png', image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])