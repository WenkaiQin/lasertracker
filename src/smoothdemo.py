import cv2
import numpy as np


N_ITER = 10

held_down = False
im = np.empty([1,1], np.uint8)
path = np.empty([1,2])


# Mouse callback function.
def on_mouse(event, x, y, flags, param):
	global held_down, im, path

	if event == cv2.EVENT_LBUTTONDOWN:
		im = np.zeros((512,512,3), np.uint8)
		cv2.circle(im,(x,y), 2, (0,255,0), -1)
		held_down = True
		path = np.array([[x,y]])
		print ' Beginning path input...'

	elif event == cv2.EVENT_MOUSEMOVE and held_down:
		cv2.line(im, tuple(path[-1]), (x,y), (255,255,255))
		path = np.append(path, [[x,y]], axis=0)

	elif event == cv2.EVENT_LBUTTONUP:
		cv2.line(im, tuple(path[-1]), (x,y), (255,255,255))
		cv2.circle(im, (x,y), 2, (0,0,255), -1)
		held_down = False
		path = np.append(path, [[x,y]], axis=0)

		print ' Smoothing path...'
		spath = smooth_path(path, N_ITER)

		print ' Showing results...'
		draw_path(im, spath)



# Smooth out jagged path.
def smooth_path(path, n_iter):
	for i in range(n_iter):
		# Generate temporary smoothed path, same beginning and end point as original path.
		tpath = np.array([path[0]])
		for j in range(1, path.shape[0]-1):
			tpath = np.append(tpath, [0.3*path[j-1] + 0.4*path[j] + 0.3*path[j+1]], axis=0)
		tpath = np.append(tpath, [path[-1]], axis=0)
		
		path = tpath.astype(int)

	return path


# Draw path.
def draw_path(im, path):
	for i in range(1, path.shape[0]):
			cv2.line(im, tuple(path[i-1]), tuple(path[i]), (255,170,86))


# Save image.

def save_image():
	user_in = raw_input('Save image? (Y/n)')
	if user_in=='Y' or user_in=='y' or user_in=='':
		filename = raw_input('Enter file name: ')
		path = 'images/' + filename + '.jpg'
		print ' Saving image as ', path, '...'
		cv2.imwrite(path, im)
		print ' Finished.'
	else:
		print ' Cancelled.'


# Main function.
def main():
	global held_down, im, path

	# Create a black image, a window and bind the function to window
	im = np.zeros((512,512,3), np.uint8)
	cv2.namedWindow('image')
	cv2.setMouseCallback('image', on_mouse)

	while(1):
		cv2.imshow('image',im)
		key = cv2.waitKey(1)

		if key == ord('s'):
			save_image()

		if key == 27:
			print ' Exiting...'
			cv2.destroyAllWindows()
			break

if __name__ == '__main__':
	main()