import cv2
import os

class VideoLoader():
    
    def __init__(self, 
                 vid_data_path,
                 frame_write_path):
        """
            vid_data_path (str): path to video data object
            frame_write_path (str): path to write our returned frames
        """
        self.vid_data_path = vid_data_path
        self.frame_write_path = frame_write_path
        
        
    def getSingleFrame(self, frame_num, write_to_disk=False):
        """Returns a numpy array representing the frame in a video
        specified by frame_num.

        Args:
            frame_num (int): the frame of interest between 1 and number of frames in the video
            write_to_disk (boolean): whether or not to write the resulting numpy array to disk

        Returns:
            _type_: numpy array representing the 
        """
        
        #total_frames = self.getFrameCount()
        cap = cv2.VideoCapture(self.vid_data_path) #open video capture object - this is EXPENSIVE!
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num) #set reader to appropriate frame number

        #Read the next frame from the video.
        ret, frame = cap.read() #ret is true or false depending on whether cap read anything

        if ret:
            #Set grayscale colorspace or RGB for the frame. 
            #color = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            color = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if write_to_disk:
                #Cut the video extension to have the name of the video
                my_video_name = self.vid_data_path.split(".")[0]
                frame_path = my_video_name+'_frame_'+str(frame_num)+'.jpg'
                self.writeJPGToDisk(frame_path, color)

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
        return color
        
        
        
    def getFrameSeq(self, start_time, end_time, frame_skip):
        """
            Extracts a sequence of frames bounded by start to end time
            start_time (int): time at which to start extracting frames
            end_time (int): time at which to end extraction of frames
            frame_rate (int): how many frames (jpgs) we want to generate from video. 
        """
        cap = cv2.VideoCapture(self.vid_data_path)
        i = 0
        # a variable to keep track of the frame to be saved
        frame_count = 0
        while cap.isOpened():
          if frame_count%100==0: print('frame_count: ', frame_count)
          if i > frame_skip - 1 and frame_count >= start_time and frame_count <= end_time:
            i = 0
            frame_count += 1

            ret, frame = cap.read()
            if not ret:
                break
            #print('frame_count: ', frame_count)
            cv2.imwrite(self.frame_write_path+str(frame_count)+'.jpg', frame)
            
          elif frame_count > end_time:
            break
          else:
            i += 1
            frame_count += 1
        return
    
    
    def writeNumpyArraysToDisk(self, path, numpy_arrays):
        pass
    
    def writeJPGToDisk(self, path, numpy_array):
        if not os.path.exists(path):
            cv2.imwrite(path,numpy_array)


    def getFrameCount(self):
        cap = cv2.VideoCapture(self.vid_data_path)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return length
        
        
# vl = VideoLoader("pexels-blue-bird-7189538.mp4", "myFrame", 50, 50)
# vl.getSingleFrame(100)