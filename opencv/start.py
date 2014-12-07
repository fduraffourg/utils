#!/usr/bin/python
import cv #Import functions from OpenCV

cv.NamedWindow('a_window', cv.CV_WINDOW_AUTOSIZE)
storage=cv.CreateMemStorage()

image=cv.LoadImage('amundi.jpg', cv.CV_LOAD_IMAGE_COLOR) #Load the image

grey = cv.CreateImage(cv.GetSize(image), 8, 1)
cv.CvtColor(image, grey, cv.CV_BGR2GRAY)

#cv.EqualizeHist(grey, grey)
cv.Laplace(grey, grey, 3)

#clone = cv.CloneImage(image)
#contours = cv.FindContours(grey, storage, cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_SIMPLE, (0,0))

#cv.DrawContours(image, contours, -1, (255,0,0), 5)

cv.ShowImage('a_window', grey) #Show the image
cv.WaitKey(10000)

