#! /usr/bin/env python

import cv2, math
import numpy as np
import sys

### Constants
LowRedlow = 0
LowRedhigh = 3
UpRedlow = 177
UpRedhigh = 180

###


# Get image
orig_img = cv2.imread('inputcup2.png')
height, width, depth = orig_img.shape

# Preprocess, convert to HSV
img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2HSV)

# Set the bounds cup selection range
red_lowerlow = np.array([LowRedlow, 100, 0],np.uint8)
red_lowerhigh = np.array([LowRedhigh, 255, 255],np.uint8)
red_upperlow = np.array([UpRedlow, 100, 0],np.uint8)
red_upperhigh = np.array([UpRedhigh, 255, 255],np.uint8)
red_binarylower = cv2.inRange(img, red_lowerlow, red_lowerhigh)
red_binaryupper = cv2.inRange(img, red_upperlow, red_upperhigh)
red_binary = cv2.bitwise_or(red_binarylower, red_binaryupper)
dilation = np.ones((int(width/100), int(width/100)), "uint8")

# Red binary is the set of red blobs
red_binary = cv2.dilate(red_binary, dilation)
cv2.imwrite('red_binary.png',red_binary)

# Find the sets of red blobs
contours, hierarchy = cv2.findContours(red_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

if not contours:
	print "no contours"
	sys.exit()

# Loop to find the largest contour
max_area = 0
largest_contour = None
largest_idx = 0
for idx, contour in enumerate(contours):
   area = cv2.contourArea(contour)
   if area > max_area:
     max_area = area
     largest_contour = contour
     largest_idx = idx

cv2.drawContours(orig_img, contours, largest_idx, [100,0,100])
cv2.imwrite('largest_contour.png',orig_img)



# # Find the box excompassing the largest red blob
rect = cv2.minAreaRect(largest_contour)
box = cv2.cv.BoxPoints(rect)
box = np.int0(box)
box_width = box[3][0]-box[1][0]
box_height = box[3][1]-box[1][1]
print box_width
print box_height
replace = cv2.imread('coke.png')
rheight, rwidth, rdepth = replace.shape
#replace_resize = cv2.resize(replace, (int(math.ceil((box_width/rwidth)))*rwidth,int(math.ceil((box_height/rheight)))*rheight))
replace_resize = cv2.resize(replace, (box_width , box_height))
theight, twidth, tdepth = replace_resize.shape
print twidth
print theight
replace_transform = cv2.cvtColor(replace_resize, cv2.COLOR_BGR2HSV)
# # Make everything in the blob white (WRONG)
for x in range (int(box[1][0]), int(box[3][0])):
 	for y in range (int(box[1][1]), int(box[3][1])):
		px = img[y][x]
 		if (px[0] >= 0 and px[1] >= 100 and px[2] >= 0 and px[0] <= 10 and px[1] <= 255 and px[2] <= 255) or (px[0] >= 170 and px[1] >= 100 and px[2] >= 0 and px[0] <= 180 and px[1] <= 255 and px[2] <= 255): 
			img[y][x] = replace_transform[(theight/2)+((y-box[1][1])-(theight/2))][(twidth/2)+((x-box[1][0])-(twidth/2))]
out_img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
cv2.imwrite('out2.png',out_img)