import cv2
import numpy as np
from collections import deque

HSV_THRESHOLD = np.array([15,170,150])
PATH_LENGTH = 11
SHOW_ALL_DETECTIONS = True
SELECT_MODE = True

ref_point = (0,0)
color = ([79,188,118])
lb = np.array(color - HSV_THRESHOLD/2)
ub = np.array(color + HSV_THRESHOLD/2)


# On mouse event callback function. Locks on selected color.
def on_mouse(event, x, y, flags, frame):
	# Use globals because callback functions are a pain.
	global ref_point, color, lb, ub, SELECT_MODE

	if event == cv2.EVENT_LBUTTONUP:
		if SELECT_MODE:
			ref_point = (x,y)
			print ' Visible laser reference point: ', ref_point
		else:
			color = frame[y,x].tolist()
			lb = np.array(color - HSV_THRESHOLD/2)
			ub = np.array(color + HSV_THRESHOLD/2)
			print ' Lower bound: ', lb
			print ' Upper bound: ', ub


def filter_path(path, dfilter = [
	0.0024, 0.0162, 0.0553, 
	0.1224, 0.1923, 0.2226,	
	0.1923, 0.1224, 0.0553, 
	0.0162,	0.0024]):

	if len(path) < len(dfilter):
		return path[len(path)/2]
	elif len(path) > len(dfilter):
		print ' Path length too long.'
		print ' Current length:', len(path), '.'
		print ' Required length:', len(dfilter), '.'
		return -1
	else:
		return tuple(np.dot(dfilter, path).astype(int))


# Finds mass center of contour.
def find_center(contour):
	moment = cv2.moments(contour)
	if moment['m00'] == 0:
		[cx,cy] = contour[0][0]
	else:
		cx = int(moment['m10']/moment['m00'])
		cy = int(moment['m01']/moment['m00'])

	return cx, cy


# Draws path on image.
def draw_path(im, path, color=(255,170,86), thickness=2):
	for i in range(len(path)-1):
		cv2.line(im, (path[i]), (path[i+1]), color, thickness)
	return im


def main():
	global ref_point, color, lb, ub, HSV_THRESHOLD, PATH_LENGTH, SHOW_ALL_DETECTIONS, SELECT_MODE

	# Turn on camera.
	cap = cv2.VideoCapture(0)
	readable, im = cap.read()

	# Set up window.
	cv2.namedWindow('Frame')
	cv2.namedWindow('Results')
	cv2.moveWindow('Results', 0, 400)

	# Exit with error if camera couldn't turn on or read.
	if not readable:
		print ' ERROR: The camera could not be opened or read.'
		print ' Exiting...'
		return 0


	# Initialize path queue.
	raw_path = deque(maxlen=PATH_LENGTH)
	fil_path = deque(maxlen=PATH_LENGTH)

	# Print initial system state.
	print ' Visible laser reference point: ', ref_point
	print ' Lower bound: ', lb
	print ' Upper bound: ', ub

	# Loop for each frame.
	while True:
		# Capture and format frame.
		im = cap.read()[1]
		im = cv2.pyrDown(im)
		im = cv2.flip(im, 1)
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
			cx,cy = find_center(max_contour)
			
			# Append center to path. Calculate and append new filtered path point.
			raw_path.append((cx,cy))
			fil_path.append((filter_path(raw_path)))

			# Draw path.
			# draw_path(results, raw_path)
			draw_path(results, fil_path, color=(51,204,51))

			# Draw the center.
			cv2.circle(results, (cx, cy), 7, (255, 255, 255), -1)

			# Draw all hulls or just the biggest (depends on SHOW_ALL_DETECTIONS).
			if SHOW_ALL_DETECTIONS:
				cv2.drawContours(results, hulls, -1, (0,255,255), 2)
			cv2.drawContours(results, [max_hull], 0, (255,0,0), 2)

		# Display results.
		cv2.imshow('Results', results)

		# Add mask to frame.
		frame = np.concatenate((im,mask_3ch), axis=1)

		# Add text to frame, show frame.
		cv2.putText(frame, 'HSV: '+str(color), (30,30), 1, 1.5, (255,255,255), 2)
		cv2.putText(frame, 'Ref: '+str(ref_point), (30,60), 1, 1.5, (255,255,255), 2)
		cv2.imshow('Frame', frame)

		# Key commands.
		key = cv2.waitKey(10)
		if key == 27:
			print ' Exiting...'
			cap.release()
			return 0
		elif key == ord('0'):
			SHOW_ALL_DETECTIONS = not SHOW_ALL_DETECTIONS
			if SHOW_ALL_DETECTIONS:
				print ' Showing only largest contour...'
			else:
				print ' Showing all contours...'
		elif key == ord('1'):
			SELECT_MODE = not SELECT_MODE
			if SELECT_MODE:
				print ' Selecting visible laser point reference point...'
			else:
				print ' Selecting invisible laser point color...'



if __name__ == '__main__':
	main()