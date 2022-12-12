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
        
        
    def getSingleFrame(self, frame_num):
        
        print('entered')
        #frame_no = (frame_num /(self.time_length*self.fps))
        total_frames = self.getFrameCount()
        print('total frames: ', total_frames)
        frame_no = frame_num / self.getFrameCount()
        cap = cv2.VideoCapture(self.vid_data_path)
        print(cap.isOpened())

        #print(cap.set(2,frame_no))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

        #Read the next frame from the video.
        ret, frame = cap.read()
        print(type(frame))

        #Set grayscale colorspace for the frame. 
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        color = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        #Cut the video extension to have the name of the video
        my_video_name = self.vid_data_path.split(".")[0]
        
        #Store this frame to an image
        frame_path = my_video_name+'_frame_'+str(frame_num)+'.jpg'
        if not os.path.exists(frame_path):
            cv2.imwrite(frame_path,color)

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
        return frame_path
        
        
        
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
            ret, frame = cap.read()
            if not ret:
                break
            if i > frame_skip - 1:
                frame_count += 1
                cv2.imwrite(self.frame_write_path+str(frame_count*frame_skip)+'.jpg', frame)
                i = 0
                continue
            i += 1
        return


    def getFrameCount(self):
        cap = cv2.VideoCapture(self.vid_data_path)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return length
        
        
# vl = VideoLoader("pexels-blue-bird-7189538.mp4", "myFrame", 50, 50)
# vl.getSingleFrame(100)