#! /usr/bin/env python

import cv2, math
import numpy as np
import sys

import Image
import StringIO
import boto
import os
import random, string
from boto.s3.key import Key

### Constants
LowRedlow = 0
LowRedhigh = 5
UpRedlow = 175
UpRedhigh = 180
ExclusionRatio = 0
Offset = 0

###

### Functions

def not_min_size(area):
    if area >= height*width / ExclusionRatio:
        return 0
    else:
        return 1

def max_min_box(box):
    # returns [minx maxx miny maxy]
    [xs,ys] = map(list, zip(*box))
    minx = min(xs)
    maxx = max(xs)
    miny = min(ys)
    maxy = max(ys)
    return [minx, maxx, miny, maxy]

def replace_contour(largest_contour, img):
    ## Find the box excompassing the largest red blob
    moment = cv2.moments(largest_contour)
    if moment["m00"] > 4000:

        pheight, pwidth, pdepth = img.shape

        rect = cv2.minAreaRect(largest_contour)
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)
        # if (not_min_size(cv2.contourArea(largest_contour))): # minimum threshold
        #         return img
        # print box
        [minx,maxx,miny,maxy] = max_min_box(box)

        box_width = maxx-minx
        maxy = int((1.2*box_width)+miny)
        if maxy > pheight:
            maxy = pheight-1

        box_height = maxy-miny

        replace = cv2.imread('coke.png')
        rheight, rwidth, rdepth = replace.shape
        replace_resize = cv2.resize(replace, (int(box_width) , int(box_height)))
        theight, twidth, tdepth = replace_resize.shape
        replace_transform = cv2.cvtColor(replace_resize, cv2.COLOR_BGR2HSV)

        ## Replace pixels in blob
        # s,w,z = img.shape
        # [xmin,xmax,ymin,ymax] = max_min_box(box)
        for x in range (minx, maxx):
            for y in range (miny, maxy):
                # if y > 0 and y < s and x > 0 and x < w :
                     # print img.shape, y, x
                px = img[y][x]
                if (px[0] >= LowRedlow and px[1] >= 100 and px[2] >= 0 and px[0] <= LowRedhigh-Offset and px[1] <= 255 and px[2] <= 255) or (px[0] >= UpRedlow+Offset and px[1] >= 100 and px[2] >= 0 and px[0] <= UpRedhigh and px[1] <= 255 and px[2] <= 255): 
                    img[y][x] = replace_transform[(theight/2)+((y-miny)-(theight/2))][(twidth/2)+((x-minx)-(twidth/2))]
        return img

def draw_box(largest_contour, img):
    ## Find the box excompassing the largest red blob
    rect = cv2.minAreaRect(largest_contour)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    box = np.int0(box)
    cv2.drawContours(img,[box], 0, (0, 0, 255), 2)
    return img


################################

if len(sys.argv) != 2:
    print "Usage: drunkreplace filename"
    sys.exit()

# Get image
orig_img = cv2.imread(sys.argv[1])
if orig_img is None:
    sys.exit("no file found")
height, width, depth = orig_img.shape

# Make directories
if not os.path.exists("debug_images"):
    os.makedirs("debug_images")
if not os.path.exists("output"):
    os.makedirs("output")

# Downsample image
while height > 1000 or width > 1000:
        orig_img = cv2.resize(orig_img, (int(width*.8) , int(height*.8)))
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
cv2.imwrite('debug_images/red_binary.png',red_binary)

# Find the sets of red blobs
contours, hierarchy = cv2.findContours(red_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# Discard possibly bad contours
## Too small
# for x, c in enumerate(contours): #repetitive loop???
#         if not_min_size(cv2.contourArea(contours[x]), height, width):
#                 del contours[x] #eliminate any irrelevant contours

## Doesn't fit cup dimensions
# for x, c in enumerate(contours): #repetitive loop???

#         if not_min_size(cv2.contourArea(contours[x]), height, width):
#                 del contours[x] #eliminate any irrelevant contours

## Cup doesnt fill box area
#
#

## Too little area in box

if not contours: 
    sys.exit("no contours")

# Sort contours by area
contoursSorted = sorted(contours, key = lambda (v): cv2.contourArea(v) , reverse = True)

# # Write contour lines
# for x in xrange(0,len(contours)):
#         cv2.drawContours(orig_img, contoursSorted, x, [x*10,0,100],thickness = 5)
# cv2.imwrite('debug_images/contours.png',orig_img)

# # Write freature boxes
# a = img
# for x in xrange(0,len(contours)):
#         a = draw_box(contoursSorted[x], a)
# a = cv2.cvtColor(a, cv2.COLOR_HSV2BGR)
# cv2.imwrite('debug_images/boxes.png',a)

# Replace image in cups
for x in xrange(0,len(contours)):
        img = replace_contour(contoursSorted[x], img)
out_img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
cv2.imwrite('output/cups.png',out_img)