import torch
import numpy as np
from torchvision import models,transforms
import torch.nn as nn
import cv2
import base64
from PIL import Image
from io import BytesIO

device='cuda:0' if torch.cuda.is_available() else 'cpu'

model_pre = models.densenet121()
for param in model_pre.features.parameters():
    param.required_grad = False

num_features = model_pre.classifier.in_features
features = list(model_pre.classifier.children())[:-1] 
features.extend([nn.Linear(num_features, 2)])
model_pre.classifier = nn.Sequential(*features)
model_pre = model_pre.to(device)

if torch.cuda.is_available()==False:
    model_pre.load_state_dict(torch.load("models/pneumonia/weights/pne.pt", map_location=lambda storage, loc: storage))
else:
    model_pre.load_state_dict(torch.load("models/pneumonia/weights/pne.pt"))

transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

class predict_img(object):
    def __init__(self,image_code):
        self.image_code=image_code

    def predict_pneumonia(self):
        img=cv2.imdecode(self.image_code,cv2.IMREAD_COLOR)
        imgo = Image.fromarray(img.astype("uint8"))
        img=np.array(imgo)
        img=transform(img)
        try:
            img=img.reshape((1,img.shape[0],img.shape[1],img.shape[2]))
        except:
            img=img.reshape((1,img.shape[0],img.shape[1]))
        model_pre.eval()
        with torch.no_grad():
            pred=model_pre(img.to(device))
        
        _,predicted = torch.max(pred.data, 1)

        predicted="Pneumonia" if predicted==1 else "Normal"
        return predicted,imgo

# if __name__=="__main__":
    
#     m=predict_img("./models/pneumonia/data/test/NORMAL/IM-0001-0001.jpeg")
#     print(m.predict_pneumonia())
#     m=predict_img("./models/pneumonia/data/test/PNEUMONIA/person100_bacteria_481.jpeg")
#     print(m.predict_pneumonia())
