import cv2
import os

class VideoCreator():

    def __init__(self):
        pass

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
