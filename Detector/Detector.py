import torch
import pandas
from VideoLoader.VideoLoader.VideoLoader import VideoLoader

class Detector():
    
    def __init__(self, 
                 model_path, 
                 vid_data_path, 
                 vid_data_ls,
                 classes,
                 confidence, 
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
        self.classes = classes
        self.confidence = confidence
        self.name = name
        
        self.model = None
        self.classifer_hash = None #?
        
        self.load()
    
    def load(self):
        """
        loads model given the path
        """
        self.model = torch.hub.load(self.model_path, self.name)
        self.model.conf = self.confidence
        self.model.classes = self.classes
        
    def detect(self, timestamp, classes, confidence):
        self.model.conf = self.confidence
        self.model.classes = self.classes
        
        vid_loader = VideoLoader(self.vid_data_path, 'myFrame')
        img = vid_loader.getSingleFrame(timestamp)
        self.getResultFromImg(img)
        
    def getResultFromImg(self, img):
        """
        img: jpg? file
        Returns: xmin, ymin, xmax,ymax,confidence,class, timestamp, classifier hash, Instance_id?
        """
        result = self.model(img)
        print(type(result))
        
        print(result.pandas().xyxy[0])
        result.show()
        #check which of return params are missing, add them as needed
        return
    
im = 'https://ultralytics.com/images/zidane.jpg'
    
dtc = Detector('ultralytics/yolov5', 'pexels-blue-bird-7189538.mp4', None, [16], 0.1,'yolov5s')
dtc.detect(10, [16], 0.1)


    
    
        