import cv2 as cv
import math
import re
from tkinter import *
from tkinter import filedialog as fd
from datetime import datetime

root = Tk()
root.winfo_toplevel().title("PhotoDNA-Replica")


def compareHashes(mode, hash1, hash2):
    """ Different comparison modes:
    Mean square error (MSE)
    Linear distance (LD)
    Raw squared difference (RSD)"""
    squared_difference = 0
    for n in range(144):
        squared_difference += (hash1[n] - hash2[n]) ** 2
    if (mode == 'MSE'):
        return str((squared_difference / 144))
    elif (mode == 'LD'):
        return str((math.sqrt(squared_difference)))
    elif (mode == 'RSD'):
        return str(squared_difference)
    else:
        return -1


def calculateHash(imgPath, scaling=100, crop=0):
    # Image is being loaded an greyscaled
    img_gsc = cv.imread(imgPath, cv.IMREAD_GRAYSCALE)

    # Getting image dimensions
    imgHeight = img_gsc.shape[0]
    imgWidth = img_gsc.shape[1]

    # Scaling of the image according to parameter
    width = int(imgWidth * scaling / 100)
    height = int(imgHeight * scaling / 100)
    dim = (width, height)
    img_gsc = cv.resize(img_gsc, dim)

    # Cropping the image according to parameter
    if crop != 0:
        offsetX = int(imgWidth * (crop / 100) / 2)
        offsetY = int(imgHeight * (crop / 100) / 2)
        topLimitX = imgWidth - offsetX
        topLimitY = imgHeight - offsetY
        img_gsc = img_gsc[offsetX:topLimitX, offsetY:topLimitY]

    # Image is scaled down to 26x26 pixels
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

            sumOfGradients.append(
                [grad_horizontal_left, grad_horizontal_right, grad_vertical_up, grad_vertical_down])
            hash.extend([grad_horizontal_left, grad_horizontal_right,
                        grad_vertical_up, grad_vertical_down])
    return hash


def setOriginalImage():
    global originalImage
    originalImage = fd.askopenfilename()


def setImgLst():
    global imgLst
    imgLst = fd.askopenfilenames()


def hashToStr(hash):
    strImgHash = ''
    for i in range(144):
        if i % 4 == 0:
            strImgHash += '('
        if i % 4 == 3:
            strImgHash += str(hash[i]) + '),'
        else:
            strImgHash += str(hash[i]) + ','
    return strImgHash


def downloadCSV():
    if originalImage != '':
        print(originalImage)
        # Insert the hash and the name for the original data
        filename = re.search(r"[^\/]+[.].+$", originalImage).group()
        outputCSV = open(
            "Results/" + filename + '_' + datetime.now().isoformat('_', 'seconds') + '.csv', 'a')
        outputCSV.write(
            'Image name;Image hash;MSE comparison;LD comparison;RSD comparison\n')
        originalHash = calculateHash(originalImage)
        outputCSV.write(filename + ' (Scaling:100%);' +
                        hashToStr(originalHash) + ';;;\n')

        # Check if images to compare against were selected
        imgListSet = True
        try:
            imgLst
        except NameError:
            imgListSet = False

        # If yes, compare the selected images to the original
        # else compare the image to itself with different scaling and cropping
        if imgListSet:
            for img in imgLst:
                imgHash = calculateHash(img)
                strImgHash = hashToStr(imgHash)

                outputCSV.write(re.search(r"[^\/]+[.].+$", img).group() + ';' + strImgHash + ';')
                outputCSV.write(compareHashes(
                    'MSE', originalHash, imgHash) + ';')
                outputCSV.write(compareHashes(
                    'LD', originalHash, imgHash) + ';')
                outputCSV.write(compareHashes(
                    'RSD', originalHash, imgHash) + '\n')
        else:
            for n in range(9):
                scaling = (9 - n)*10
                imgHash = calculateHash(originalImage, scaling)
                strImgHash = hashToStr(imgHash)

                outputCSV.write('Original (Scaling:' + str(scaling) + '%)' +
                                ';' + strImgHash + ';')
                outputCSV.write(compareHashes(
                    'MSE', originalHash, imgHash) + ';')
                outputCSV.write(compareHashes(
                    'LD', originalHash, imgHash) + ';')
                outputCSV.write(compareHashes(
                    'RSD', originalHash, imgHash) + '\n')
            for n in range(10):
                crop = (n + 1) * 2
                imgHash = calculateHash(originalImage, 100, crop)
                strImgHash = hashToStr(imgHash)

                outputCSV.write('Original (Crop:' + str(crop) + '%)' +
                                ';' + strImgHash + ';')
                outputCSV.write(compareHashes(
                    'MSE', originalHash, imgHash) + ';')
                outputCSV.write(compareHashes(
                    'LD', originalHash, imgHash) + ';')
                outputCSV.write(compareHashes(
                    'RSD', originalHash, imgHash) + '\n')

        outputCSV.close()


Button(root, text='Select original picture',
       command=setOriginalImage).grid(row=2, column=30)
Button(root, text='Select pictures to compare with',
       command=setImgLst).grid(row=3, column=30)
Button(root, text='Calculate and save to .csv',
       command=downloadCSV).grid(row=4, column=30)
Button(root, text="Quit", command=root.destroy).grid(row=5, column=30)

mainloop()
