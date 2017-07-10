import cv2
import numpy as np
from collections import deque

from picamera.array import PiRGBArray
from picamera import PiCamera
import time

HSV_THRESHOLD = np.array([15,170,150])
PATH_LENGTH = 10
SHOW_ALL_DETECTIONS = True	

color = ([84,10,255])
lb = np.array(color - HSV_THRESHOLD/2)
ub = np.array(color + HSV_THRESHOLD/2)

def on_mouse(event, x, y, flags, frame):
	# Use globals because callback functions are a pain.
	global color, lb, ub

	if event == cv2.EVENT_LBUTTONUP:
		color = frame[y,x].tolist()
		lb = np.array(color - HSV_THRESHOLD/2)
		ub = np.array(color + HSV_THRESHOLD/2)
		print 'Lower bound: ', lb
		print 'Upper bound: ', ub
		print


def main():	
	global color, lb, ub, HSV_THRESHOLD, PATH_LENGTH, SHOW_ALL_DETECTIONS
	
	# Turn on camera.
	# cap = cv2.VideoCapture(0)
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 32
	raw_capture = PiRGBArray(camera, size=(640,480))

	# Allow camera to warm up.
	time.sleep(0.1)

	# readable, im = cap.read()

	# Set up window.
	cv2.namedWindow('Frame')
	cv2.namedWindow('Results')
	cv2.moveWindow('Results', 0, 400)

	# Exit with error if camera couldn't turn on or read.
	# if not readable:
	# 	print 'ERROR: The camera could not be opened or read.'
	# 	print 'Exiting...'
	# 	return 0


	# Initialize path queue.
	path = deque(maxlen=PATH_LENGTH)

	# Loop for each frame.
	for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
		# Capture and format frame.
		im = frame.array
		im = cv2.pyrDown(im)
		# im = cv2.flip(im, 1)
		im_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

		# Callback if mouse action in frame.
		cv2.setMouseCallback('Frame', on_mouse, im_hsv)

		# Make mask from threshold, 3 channel version for display.
		mask = cv2.inRange(im_hsv, lb, ub)
		mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

		# Use mask to find and draw contour/hull.
		results = np.copy(im)
		contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]

		if len(contours)>0:
			max_contour = max(contours, key=cv2.contourArea)

			# Filter contours by size. Accomplishes morph opening without the computation!
			contours = [contour for contour in contours if len(contour)>25]

			# Make convex hulls for each contour, as well as max hull.
			hulls = [cv2.convexHull(contour) for contour in contours]
			max_hull = cv2.convexHull(max_contour)

			# Determine center of max contour using moment.
			max_M = cv2.moments(max_contour)
			if max_M['m00'] == 0:
				[cx,cy] = max_contour[0][0]
			else:
				cx = int(max_M['m10']/max_M['m00'])
				cy = int(max_M['m01']/max_M['m00'])

			# Append center to path.
			path.append((cx,cy))

			# Draw path.
			for i in range(len(path)-1):
				cv2.line(results, (path[i]), (path[i+1]), (255,170,86), 2)

			# Draw the center.
			cv2.circle(results, (cx, cy), 7, (255, 255, 255), -1)

			# Draw all hulls or just the biggest (depends on SHOW_ALL_DETECTIONS).
			# if SHOW_ALL_DETECTIONS:
			# 	cv2.drawContours(results, hulls, -1, (0,255,255), 2)
			cv2.drawContours(results, [max_hull], -1, (255,0,0), 2)

		# Display results.
		cv2.imshow('Results', results)

		# Add mask to frame.
		frame = np.concatenate((im,mask_3ch), axis=1)

		# Add text to frame, show frame.
		cv2.putText(frame, 'HSV: '+str(color), (30,30), 1, 1.5, (255,255,255), 2)
		cv2.imshow('Frame', frame)

		# Clear stream in preparation for the next frame.
		raw_capture.truncate(0)

		# Key commands.
		key = cv2.waitKey(10)
		if key == 27:
			print 'Exiting...'
			return 0
		elif key == ord('h'):
			SHOW_ALL_DETECTIONS = ~SHOW_ALL_DETECTIONS


if __name__ == '__main__':
	main()
