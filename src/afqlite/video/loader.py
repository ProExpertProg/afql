import cv2
import os

class VideoLoader:
    
    def __init__(self, 
                 vid_data_path):
        """
            vid_data_path (str): path to video data object
            frame_write_path (str): path to write our returned frames
        """
        self.vid_data_path = vid_data_path
        self.cap = cv2.VideoCapture(self.vid_data_path)
        
        
    def getSingleFrame(self, frame_num, write_to_disk=False):
        """Returns a numpy array representing the frame in a video
        specified by frame_num.

        Args:
            frame_num (int): the frame of interest between 1 and number of frames in the video
            write_to_disk (boolean): whether or not to write the resulting numpy array to disk

        Returns:
            _type_: numpy array representing the 
        """
        
        #total_frames = self.getFrameCount() #open video capture object - this is EXPENSIVE!
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num) #set reader to appropriate frame number

        #Read the next frame from the video.
        ret, frame = self.cap.read() #ret is true or false depending on whether cap read anything

        if ret:
            #Set grayscale colorspace or RGB for the frame. 
            #color = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            color = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if write_to_disk:
                #Cut the video extension to have the name of the video
                self.writeJPGToDisk(frame_num, color)

        # When everything done, release the capture
        # cap.release()
        # cv2.destroyAllWindows()
        return color
    
    
    def writeJPGToDisk(self, frame_num, numpy_array):
        my_video_name = self.vid_data_path.split(".")[0]
        frame_path = my_video_name+'_frame_'+str(frame_num)+'.jpg'
        if not os.path.exists(frame_path):
            cv2.imwrite(frame_path,numpy_array)


    def getFrameCount(self):
        cap = cv2.VideoCapture(self.vid_data_path)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return length
        
        
# vl = VideoLoader("pexels-blue-bird-7189538.mp4", "myFrame", 50, 50)
# vl.getSingleFrame(100)