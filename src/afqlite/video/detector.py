import torch
import pandas
# from afqlite.video.loader import VideoLoader
# from afqlite.video.utils import *
# from afqlite.video.quantizer import KMeansQuantizer
from loader import VideoLoader
import torchvision.models as models

# xmin, ymin, xmax, ymax, confidence, class, timestamp, classifier_hash
#DetectionTuple = tuple[float, float, float, float, float, int, int, str] #<- confused by this line
# from typing import NewType
# DetectionTuple = NewType('DetectionTuple', [float, float, float, float, float, int, int, str])

class Detector:
    
    def __init__(self, 
                 model_path,
                 name):
        """
        model_path (str): path to model
        vid_data_path (str): path to video objects in our database
        vid_data_ls (tuple): (video_id (str), timestramp)
        name (str): name chosen by user to identify this detector
        """
        self.model_path = model_path
        self.name = name
        self.model = None
        self.classifer_hash = None #?
        
        self.load()
    
    def load(self):
        """
        loads model given the path
        """
        self.model = torch.hub.load(self.model_path, self.name)
        #self.model = torch.load(self.model_path)
        
        
    def detect(self, timestamp, classes, confidence, vid_data_path):
        self.model.conf = confidence
        self.model.classes = classes
        
        vid_loader = VideoLoader(vid_data_path, 'myFrame')
        img = vid_loader.getSingleFrame(timestamp, False)
        return self.getResultFromImg(img, timestamp)
        
    def getResultFromImg(self, img, timestamp):
        """
        img: jpg? file
        Returns: xmin, ymin, xmax,ymax,confidence,class, timestamp, classifier hash, Instance_id?
        """
        result = self.model(img)
        #result.show()
        temp = result.pandas().xyxy[0] #convert from YOLOOutput class to pandas dataframe
        temp = temp.drop(columns=['name']) #name is redundant with class integer
        temp["timestamp"] = [timestamp for _ in range(len(temp))] #concat timestamp
        temp["classifier"] = self.name #concat classifier
        return DetectionTuple(temp.values.tolist()) #return as a Python list
    
    def getDataFrameFromBatch(self,
                              frame_start,
                              frame_end,
                              frame_jump,
                              classes,
                              confidence,
                              vid_data_path):
        all_values = []
        
        for i in range(frame_start, frame_end, frame_jump):
            res = self.detect(i, classes, confidence, vid_data_path)
            all_values.extend(res)
        df_to_ret = pandas.DataFrame(all_values)
        df_to_ret.columns = ["xmin","ymin","xmax","ymax", "confidence","class","name","timestamp"]
        return df_to_ret
    
if __name__ == "__main__":
    
    # #dtc = Detector('ultralytics/yolov5', 'pexels-blue-bird-7189538.mp4', None, 'yolov5s')
    # dtc = Detector('ultralytics/yolov5', 'yolov5s')

    # for i in range(0, 36, 12):
    #     base = "runs"
    #     ans = dtc.detect(i, [0, 16], 0.7, 'pexels-blue-bird-7189538.mp4')
    #     print(type(ans))
        
    # print('made it here')

    # # vc = VideoCreator()
    # # vc.mergeFramesIntoVid("runs/detect/", "testVid.avi")
    df = pandas.read_pickle("testy_test.pkl")
    print(df.head())
    
    #test that detect works
    #implement a cli command for loading a detector
    #write a skeleton for paper



    
    
        