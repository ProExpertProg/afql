import torch
import pandas
from VideoLoader import VideoLoader
from VideoCreator import VideoCreator
from myUtils import prune
from Quantizer import KMeansQuantizer

class Detector():
    
    def __init__(self, 
                 model_path, 
                 vid_data_path, 
                 vid_data_ls,
                 name):
        """
        model_path (str): path to model
        vid_data_path (str): path to video objects in our database
        vid_data_ls (tuple): (video_id (str), timestramp)
        name (str): name chosen by user to identify this detector
        """
        self.model_path = model_path
        self.vid_data_path = vid_data_path #this might not be an argument but a variable global to proj
        self.vid_data_ls = vid_data_ls
        self.name = name        
        self.model = None
        self.classifer_hash = None #?
        
        self.load()
    
    def load(self):
        """
        loads model given the path
        """
        self.model = torch.hub.load(self.model_path, self.name)
        bitwidth = 8
        quantizer = KMeansQuantizer(self.model, 8)
        #prune(self.model, 0.3)
        
    def detect(self, timestamp, classes, confidence, save_dir):
        self.model.conf = confidence
        self.model.classes = classes
        
        vid_loader = VideoLoader(self.vid_data_path, 'myFrame')
        img = vid_loader.getSingleFrame(timestamp)
        self.getResultFromImg(img, save_dir)
        
    def getResultFromImg(self, img, save_dir):
        """
        img: jpg? file
        Returns: xmin, ymin, xmax,ymax,confidence,class, timestamp, classifier hash, Instance_id?
        """
        result = self.model(img)
        temp = result.pandas().xyxy[0]
        temp["timestamp"] = [self.count for _ in range(len(temp))]
        return temp.values.tolist()
    
    def getDataFrameFromBatch(self, 
                            frame_start, 
                            frame_end, 
                            frame_jump, 
                            classes, 
                            confidence, 
                            save_dir):
        all_values = []
        
        for i in range(frame_start, frame_end, frame_jump):
            res = dtc.detect(i, classes, confidence, save_dir)
            all_values.extend(res)
        df_to_ret = pandas.DataFrame(all_values)
        df_to_ret.columns = ["xmin","ymin","xmax","ymax", "confidence","class","name","timestamp"]
        return df_to_ret
    
if __name__ == "__main__":
    
    dtc = Detector('ultralytics/yolov5', 'pexels-blue-bird-7189538.mp4', None, 'yolov5s')

    for i in range(0, 600, 12):
        base = "runs"
        dtc.detect(i, [0, 16], 0.7, base)
        
    print('made it here')

    vc = VideoCreator()
    vc.mergeFramesIntoVid("runs/detect/", "testVid.avi")
    
    #test that detect works
    #implement a cli command for loading a detector
    #write a skeleton for paper



    
    
        