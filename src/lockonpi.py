import cv2
import numpy as np
from collections import deque

from picamera.array import PiRGBArray
from picamera import PiCamera
from Adafruit_PWM_Servo_Driver import PWM
import time


HSV_THRESHOLD = np.array([15,170,150])
PATH_LENGTH = 11
SHOW_ALL_DETECTIONS = True
SHOW_ALL_PATHS = True
SELECT_MODE = True
REF_POINT = (159,144)
COLOR = ([84,10,255])
HSV_LOW = np.array(COLOR - HSV_THRESHOLD/2)
HSV_HIGH = np.array(COLOR + HSV_THRESHOLD/2)


# On mouse event callback function. Locks on selected color.
def on_mouse(event, x, y, flags, frame):
	# Use globals because callback functions are a pain.
	global HSV_THRESHOLD, SELECT_MODE, REF_POINT, COLOR, HSV_LOW, HSV_HIGH

	if event == cv2.EVENT_LBUTTONUP:
		if SELECT_MODE:
			REF_POINT = (x,y)
			print ' Visible laser reference point:', REF_POINT
		else:
			COLOR = frame[y,x].tolist()
			HSV_LOW = np.array(COLOR - HSV_THRESHOLD/2)
			HSV_HIGH = np.array(COLOR + HSV_THRESHOLD/2)
			print ' Lower bound:', HSV_LOW
			print ' Upper bound:', HSV_HIGH


# Uses a digital filter to return a single point from a path.
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


# Updates all coordinates of a path with movement.
def update_path(path, rel):
	path_L = [ tuple(np.subtract(coord,rel)) for coord in path ]
	return deque(path_L)

# Updates all coordinates of a path using a reference point to a destination point.
def update_path_dst(path, ref, dst):
	rel = np.subtract(dst, ref)
	return update_path(path, rel)


# Finds mass center of contour.
def find_center(contour):
	moment = cv2.moments(contour)
	if moment['m00'] == 0:
		[cx,cy] = contour[0][0]
	else:
		cx = int(moment['m10']/moment['m00'])
		cy = int(moment['m01']/moment['m00'])
	return (cx, cy)


# Draws path on image. Skips points that are outside of window.
def draw_path(im, path, color=(255,170,86), thickness=2, window_size=(640,480)):
	for i in range(len(path)-1):
		if (0<=path[i][0]<window_size[0] and 0<path[i][1]<window_size[1]) and (0<=path[i+1][0]<window_size[0] and 0<path[i+1][1]<window_size[1]):
			cv2.line(im, (path[i]), (path[i+1]), color, thickness)
	return im


# Set pwm in x and y directions.
def set_pwm(pwm, x, y):
	pwm.setPWM(0, 0, x)
	pwm.setPWM(0, 0, y)
	return (x, y)


# Moves servos to neutral position.
def move_neut(pwm):
	return set_pwm(pwm, 307, 307)


# Moves x, y pixels in either direction.
def move_rel(pwm, rel, curr_pwm):
	x_pwm, y_pwm = curr_pwm
	x_pwm -= int(round(rel[0]*1952/16875))	# 1 pixel is about 0.1157 ticks
	y_pwm -= int(round(rel[1]*1952/16875))
	return set_pwm(pwm, x_pwm, y_pwm)


# Moves motor to move reference point to destination point.
def move_ref(pwm, ref, dst, curr_pwm):
	rel = np.subtract(dst,ref)
	return move_rel(pwm, rel, curr_pwm)


def main():
	global HSV_THRESHOLD, PATH_LENGTH, SHOW_ALL_DETECTIONS, SHOW_ALL_PATHS, SELECT_MODE, REF_POINT, COLOR, HSV_LOW, HSV_HIGH

	curr_pwm = (0,0)

	# Turn on camera.
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 32
	raw_capture = PiRGBArray(camera, size=(640,480))

	# Allow camera to warm up.
	time.sleep(0.1)

	# Initialize PWM motor drivers and set motors to neutral position.
	pwm = PWM(0x40)
	pwm.setPWMFreq(50)
	curr_pwm = move_neut(pwm)

	# Set up window.
	cv2.namedWindow('Frame')
	cv2.namedWindow('Results')
	cv2.moveWindow('Results', 0, 400)

	# Initialize path queue.
	raw_path = deque(maxlen=PATH_LENGTH)
	fil_path = deque(maxlen=PATH_LENGTH)

	# Print initial system state.
	print ' Visible laser reference point: ', REF_POINT
	print ' Lower bound: ', HSV_LOW
	print ' Upper bound: ', HSV_HIGH

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
		mask = cv2.inRange(im_hsv, HSV_LOW, HSV_HIGH)
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
			center = find_center(max_contour)

			# Append center to path. Calculate and append new filtered path point.
			raw_path.append(center)
			fil_path.append((filter_path(raw_path)))

			# Draw path.
			if SHOW_ALL_PATHS:
				draw_path(results, raw_path)
			draw_path(results, fil_path, color=(51,204,51))

			# Move the reference point to the center, then update paths to match.
			curr_pwm = move_ref(pwm, REF_POINT, fil_path[-1], curr_pwm)
			cv2.line(results, REF_POINT, fil_path[-1], (255, 255, 255))
			raw_path = update_path_dst(raw_path, REF_POINT, fil_path[-1])
			test_path = update_path_dst(raw_path, REF_POINT, fil_path[-1])
			fil_path = update_path_dst(fil_path, REF_POINT, fil_path[-1])

			# Draw the center.
			cv2.circle(results, center, 7, (255, 255, 255), -1)

			# Draw all hulls or just the biggest (depends on SHOW_ALL_DETECTIONS).
			if SHOW_ALL_DETECTIONS:
				cv2.drawContours(results, hulls, -1, (0,255,255), 2)
			cv2.drawContours(results, [max_hull], -1, (255,0,0), 2)

		# Display results.
		cv2.imshow('Results', results)

		# Add mask to frame.
		frame = np.concatenate((im,mask_3ch), axis=1)

		# Add text to frame, show frame.
		cv2.putText(frame, 'HSV: '+str(COLOR), (30,30), 1, 1.5, (255,255,255), 2)
		cv2.putText(frame, 'Ref: '+str(REF_POINT), (30,60), 1, 1.5, (255,255,255), 2)
		cv2.imshow('Frame', frame)

		# Clear stream in preparation for the next frame.
		raw_capture.truncate(0)

		# Key commands.
		key = cv2.waitKey(10)
		if key == 27:
			print ' Exiting...'
			return 0
		if key == ord('0'):
			SHOW_ALL_DETECTIONS = not SHOW_ALL_DETECTIONS
			if SHOW_ALL_DETECTIONS:
				print ' Showing only largest contour...'
			else:
				print ' Showing all contours...'
		if key == ord('1'):
			SELECT_MODE = not SELECT_MODE
			if SELECT_MODE:
				print ' Selecting visible laser point reference point...'
			else:
				print ' Selecting invisible laser point color...'
		if key == ord('2'):
			print ' PWM status:', curr_pwm
		if key == ord('3'):
			SHOW_ALL_PATHS = not SHOW_ALL_PATHS
			if SHOW_ALL_PATHS:
				print ' Showing only filtered path...'
			else:
				print ' Showing both raw and filtered paths...'
		if key == ord('q'):
			print ' Testing motor function...'
			curr_pwm = move_rel(pwm, (-50,-50), curr_pwm)
		if key == ord('p'):
			print ' Pausing...'
			cv2.waitKey()
			print ' Resuming...'


if __name__ == '__main__':
	main()
