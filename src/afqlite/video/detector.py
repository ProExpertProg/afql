import torch
import pandas
from afqlite.video.loader import VideoLoader
from afqlite.video.utils import *
from afqlite.video.quantizer import KMeansQuantizer
import torchvision.models as models

# xmin, ymin, xmax, ymax, confidence, class, timestamp, classifier hash
DetectionTuple = tuple[float, float, float, float, float, int, int, str]

class Detector:
    
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
        #self.model = torch.load(self.model_path)
        
        full_model_size = get_model_size(self.model, 32)
        print(f"    {32}-bit k-means quantized model has size={full_model_size/MiB:.2f} MiB")
        
        bitwidth = 8
        quantizer = KMeansQuantizer(self.model, 8)
        quantized_model_size = get_model_size(self.model, bitwidth)
        print(f"    {bitwidth}-bit k-means quantized model has size={quantized_model_size/MiB:.2f} MiB")
        #prune(self.model, 0.3)
        
    def detect(self, timestamp, classes, confidence):
        self.model.conf = confidence
        self.model.classes = classes
        
        vid_loader = VideoLoader(self.vid_data_path, 'myFrame')
        img = vid_loader.getSingleFrame(timestamp)
        return self.getResultFromImg(img, timestamp)
        
    def getResultFromImg(self, img, timestamp):
        """
        img: jpg? file
        Returns: xmin, ymin, xmax,ymax,confidence,class, timestamp, classifier hash, Instance_id?
        """
        result = self.model(img)
        result.show()
        temp = result.pandas().xyxy[0]
        temp["timestamp"] = [timestamp for _ in range(len(temp))]
        return temp.values.tolist()
    
    def getDataFrameFromBatch(self,
                              frame_start,
                              frame_end,
                              frame_jump,
                              classes,
                              confidence):
        all_values = []
        
        for i in range(frame_start, frame_end, frame_jump):
            res = self.detect(i, classes, confidence)
            all_values.extend(res)
        df_to_ret = pandas.DataFrame(all_values)
        df_to_ret.columns = ["xmin","ymin","xmax","ymax", "confidence","class","name","timestamp"]
        return df_to_ret
    
if __name__ == "__main__":
    
    #dtc = Detector('ultralytics/yolov5', 'pexels-blue-bird-7189538.mp4', None, 'yolov5s')
    dtc = Detector('ultralytics/yolov5', 'pexels-blue-bird-7189538.mp4', None, 'yolov5s')

    for i in range(0, 36, 12):
        base = "runs"
        dtc.detect(i, [0, 16], 0.7)
        
    print('made it here')

    # vc = VideoCreator()
    # vc.mergeFramesIntoVid("runs/detect/", "testVid.avi")
    
    #test that detect works
    #implement a cli command for loading a detector
    #write a skeleton for paper



    
    
        