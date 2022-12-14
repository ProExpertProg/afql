import cv2
import os
from afqlite.video.loader import VideoLoader

class VideoCreator():

    def __init__(self):
        pass
    
    def createAnnotatedVid(self, ls_df, path_to_vid, image_store):
        """This function returns the path to a .avi file that has annotated video from the frames selected
        The annotations in each df run consecutively, seperated by a span of black frames

        Args:
            ls_df(list[dataframes]): list of dataframes containing annotations
            path_to_vid (string): path to video
            image_store (string): path to images
            
            
        """
        vl = VideoLoader(path_to_vid)
        seen_frames = {}
        imgs, pred, files = [], [], [] #list of images as numpy arrays, (xyxy, conf, cls), image filenames
        
        for df in ls_df:
            for i in range(len(df)):
                row = df.iloc[i]
                timestamp, obj_class = row["timestamp"], row["class"]
                if timestamp not in seen_frames:
                    np_im = vl.getSingleFrame(timestamp, write_to_disk=image_store)
                    file = image_store + str(timestamp) + ".jpg"
                else:
                    np_im = vl.getSingleFrame(timestamp)
        
        #create a Detection object
        
        #use mergeFramesIntoVid

    def mergeFramesIntoVid(self, dir_path, video_name, fps):
        """merge the frames into a video file and write the video file

        Args:
            frames (list[str]): list of paths to frames
            video_name: name of output video
            fps (int): 
        """

        frames_dir = os.listdir(dir_path[:len(dir_path) - 1])
        frames = []
        iter_word = "exp"
        for dir in frames_dir:
            if dir == iter_word:
                indx1 = 0
            else:
                indx1 = int(dir[len(iter_word):])
            frames = frames + [(dir_path+dir+"/"+img, indx1) for img in os.listdir(dir_path+dir) if any(img.endswith(e) for e in ["png", "jpeg", "jpg"])]
        first_frame = cv2.imread(frames[0][0])
        height, width, layers = first_frame.shape

        video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width,height))

        frames = sorted(frames, key=lambda t:t[1])
        for frame in frames:
            video.write(cv2.imread(frame[0]))

        # #video.save()
        cv2.destroyAllWindows()
        video.release()
