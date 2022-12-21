import cv2 as cv
import sys
import math

# Different comparison modes:
# Mean square error (MSE)
# Linear distance (LD)
# Raw squared difference (RSD)
def compareHashes (mode, hash1, hash2) :
    squared_difference = 0
    for i in range(144):
        squared_difference += (hash1[n] - hash2[n]) ** 2
    if (mode == 'MSE') :
        return (squared_difference / 144)
    elif (mode == 'LD') :
        return (math.sqrt(squared_difference))
    elif (mode == 'RSD') :
        return squared_difference
    else : 
        return -1


# Image is being loaded an greyscaled
img_gsc = cv.imread("Tests/Photos/windmill.png", cv.IMREAD_GRAYSCALE)

height, width = (26, 26)  # img_gsc.shape[:2]
overlap = 2

# Normalize the image
img_nrm = cv.resize(img_gsc, (height, width))

# Divide the image into 6x6 segments and calculate their sobel gradients
ssize = 6

sumOfGradients = []
hash = []

for y in range(ssize):
    for x in range(ssize):
        offsety, offsetx = (y*ssize - y*overlap, x*ssize - x*overlap)
        segment = img_nrm[offsety:offsety +
                          ssize, offsetx:offsetx + ssize]

        # Calculate the sobel gradients
        grad_x = cv.Sobel(segment, cv.CV_64F, 1, 0, ksize=1)
        grad_y = cv.Sobel(segment, cv.CV_64F, 0, 1, ksize=1)

        # rows,cols = grad_x.shape
        # for i in range(rows):
        #     k = []
        #     for j in range(cols):
        #         k.append(grad_x[i,j])
        #     print(k)
        # print("\n")
        # rows,cols = grad_y.shape
        # for i in range(rows):
        #     k = []
        #     for j in range(cols):
        #         k.append(grad_y[i,j])
        #     print(k)
        # print("\n")

        grad_horizontal_right = 0
        grad_horizontal_left = 0
        
        for i in range(ssize):
            for j in range(ssize):
                if (grad_x[i, j] > 0):
                    grad_horizontal_right += grad_x[i, j]
                else:
                    grad_horizontal_left -= grad_x[i, j]

        grad_vertical_up = 0
        grad_vertical_down = 0
        for i in range(ssize):
            for j in range(ssize):
                if (grad_y[j, i] > 0):
                    grad_vertical_up += grad_y[j, i]
                else:
                    grad_vertical_down -= grad_y[j, i]

        sumOfGradients.append([grad_horizontal_left, grad_horizontal_right, grad_vertical_up, grad_vertical_down])
        hash.extend([grad_horizontal_left, grad_horizontal_right, grad_vertical_up, grad_vertical_down])

#print(sumOfGradients)
print(hash)

if img_nrm is None:
    sys.exit("Could not read the image.")

cv.imwrite("Temp/result.png", img_nrm)
