import glob
import numpy as np
import cv2
from calibration import util

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def find_corners(square_size=0.0275, width=8, height=5):
    """ Apply camera calibration operation for images in the given directory path. """
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
    util.info("Finding checkerboard corners...")
    objp = np.zeros((height * width, 2), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)

    objp = objp * square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    img_names = []  # Image sizes with names
    img_shapes = []  # Image sizes with names

    images = glob.glob('images/IMG*.jpg')
    count = 1
    index = 0
    for fname in images:
        index += 1
        util.info("Finding corners for " + fname)
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_shapes.append([img.shape[0], img.shape[1]])
        img_names.append(fname)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (width, height), None)

        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(
                img, (width, height), corners2, ret)
            cv2.imwrite('images/pattern_' + str(count) + '.png', img)
            count += 1
        else:
            print("image" + str(index) + "false")

    util.info("DONE.\n")
    return objpoints, imgpoints, img_shapes, img_names
