import cv2
import os
from afqlite.video.loader import VideoLoader
import pandas as pd
import torch
from torchvision.utils import draw_bounding_boxes, save_image
from torchvision.transforms import transforms
import numpy as np

class VideoCreator():

    def __init__(self):
        pass
    
    def createAnnotatedVid(self, ls_df, path_to_vid, image_store):
        """This function returns the path to a .avi file that has annotated video from the frames selected
        The annotations in each df run consecutively, seperated by a span of black frames

        Args:
            ls_df(list[dataframes]): list of dataframes containing annotations
            path_to_vid (string): path to video we're scanning
            image_store (string): path to which we write image frames we obtain from the video
            
            
        """
        print('path to vid: ', path_to_vid)
        vl = VideoLoader(path_to_vid)
        seen_frames = {}
        frame_boxes = {}
        
        for df in ls_df:
            for i in range(len(df) - 1):
                if i%10==0:print('i: ', i)
                row = df.iloc[i]
                timestamp, obj_class = row["timestamp"], row["class"]
                if timestamp not in seen_frames:
                    np_im = vl.getSingleFrame(timestamp).astype(np.uint8)
                    mytensor = torch.tensor(np_im).permute(2, 0, 1)
                    seen_frames[timestamp] = mytensor
                    
                    frame_boxes[timestamp] = [self.prepareBox(row[["xmin", "ymin", "xmax", "ymax"]].values.tolist(), np_im.shape)]
                else:
                    frame_boxes[timestamp].append(self.prepareBox(row[["xmin", "ymin", "xmax", "ymax"]].values.tolist(), np_im.shape))
                
        
        #merge into video object
        for frame in seen_frames:
            stacked_tensor = torch.cat(frame_boxes[frame])
            tnsr = draw_bounding_boxes(seen_frames[frame], stacked_tensor,  colors=["green" for _ in range(stacked_tensor.shape[0])], fill=True, width=5)
            tnsr = tnsr.permute(1, 2, 0).numpy().astype(np.float32)
            ret = cv2.imwrite(image_store+str(frame)+".png", tnsr) #tnsr.reshape(tnsr.shape[1], tnsr.shape[2], tnsr.shape[0])
        
        self.mergeFramesIntoVid(image_store, image_store+"demo.avi", 1)

    def mergeFramesIntoVid(self, dir_path, video_name, fps):
        """merge the frames into a video file and write the video file

        Args:
            frames (list[str]): list of paths to frames
            video_name: name of output video
            fps (int): fps at which we write the video .avi
        """

        
        frames = os.listdir(dir_path)
        frames = [(int(frames[i].split(".")[-2]), frames[i]) for i in range(len(frames))]
        frames.sort()
        # iter_word = "exp"
        # for dir in frames_dir:
        #     if dir == iter_word:
        #         indx1 = 0
        #     else:
        #         indx1 = int(dir[len(iter_word):])
        #     frames = frames + [(dir_path+dir+"/"+img, indx1) for img in os.listdir(dir_path+dir) if any(img.endswith(e) for e in ["png", "jpeg", "jpg"])]
        first_frame = cv2.imread(dir_path + frames[0][1])
        height, width, layers = first_frame.shape

        video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width,height))

        for frame in frames:
            video.write(cv2.imread(dir_path + frame[1]))

        # #video.save()
        cv2.destroyAllWindows()
        video.release()
        
    def prepareBox(self,ls, border):
        ls[0] *= border[1]/640
        ls[2] *= border[1]/640
        ans = torch.tensor(ls).unsqueeze(0)
        #print(type(ans))
        return ans

if __name__ == "__main__":
    
    cr = VideoCreator()
    path_to_vid = "zebra/zebra_giraffe_human.mp4"
    df = pd.read_csv("zebra/zebra_tuples.csv")
    cr.createAnnotatedVid([df], path_to_vid, "res_img/")