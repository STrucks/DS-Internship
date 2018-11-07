# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 09:32:12 2018

@author: Christopher
"""

import numpy as np
from load_data import load_hyp_spectral

def extract_simple_features():
    """
    Before we use more complicated methods, like pretrained NN, lets start with simple features:
    - simply the average over 50 channels (400-405, 406-410 ect)
    """
    # load the data
#    from scipy.io import loadmat
#    
#    f = loadmat("data/indian_pines.mat")
#    raw_data = f['indian_pines']
#    
#    f = loadmat("data/indian_pines_gt.mat")
#    GT = f['indian_pines_gt']
#    
#    data = {}
#    
#    for row in range(len(GT)):
#        for col in range(len(GT[row,:])):
#            if str(GT[row,col]) in data:
#                data[str(GT[row,col])].append(raw_data[row, col, :])
#            else:
#                data[str(GT[row, col])] = []
#                data[str(GT[row, col])].append(raw_data[row, col, :])
    data = load_hyp_spectral()
    features = []
    for key in data.keys():
        averages = sum(data[key])
        averages = np.dot(averages, 1/len(data[key]))
        channels = np.split(averages, 20)
        row = [sum(c)/len(c) for c in channels]
        features.append([key] + row)
        
    print(features)
    with open("hyp_simple_features.txt", 'w') as f:
        for row in features:
            f.write(row[0] + ":")
            for nr in row[1:-1]:
                f.write(str(nr) + ",")
            f.write(str(row[-1]) + "\n")



def extract_abstract_features():
    """
    We can use pretrained networks to kinda extract more abstract features. The 
    problem is that they have a very specific input format: (3 x H x W), where 
    H and W are expected to be at least 224. The 3 obviously stands for the 3 rgb 
    channels.
    Thus we neet to restructure our hyp-spec data into that format.
    Idea 1: just use all bandwidths of one class and put them under each other
    Idea 2: put the average of a class N times under each other
    Idea 3: multiply the average bandwith of a class with itself, sothat a matrix 
    results.
    Idea 4: work in progress
    """
    # load data:
    data = load_hyp_spectral()
    # load the pre trained model, in this case we take VVG16, 
    # because it is trained on a wide range of different objects. We remove 
    # the last layer to get the high level features
    from keras.preprocessing import image
    from keras.applications.vgg16 import VGG16
    from keras.applications.vgg16 import preprocess_input
    model = VGG16(weights='imagenet', include_top=False)
    
#    img_path = 'IMG_8352.jpg'
#    img = image.load_img(img_path, target_size=(224, 224))
#    img_data = image.img_to_array(img)
#    print(img_data.shape)
#    img_data = np.expand_dims(img_data, axis=0)
#    print(img_data.shape)
#    img_data = preprocess_input(img_data)
#    print(img_data.shape)
#    vgg16_feature = model.predict(img_data)
    
    # Idea 1:
    if True:
        print("Idea 1")
        with open("abstract_features_idea1.txt", 'w') as f:
            for c in range(17):
                img = data[str(c)]
                # fill every bandwidth with 4 zeros to get a width of at leatst 224:
                img = [list(row) + [0]*4 for row in img]
                # we restrict ourselves on 500 samples, because using all crashed my pc really hard
                # also we will extend to 500 samples if there are not enough, otherwise the feature vector is empty
                if len(img) < 500:
                    img = [[row, row, row] for row in img] * int(500/len(img))
                else:
                    img = [[row, row, row] for row in img[0:500]]
                
                img_data = np.asarray(img)
                img_data = np.swapaxes(img_data, 1, 2)
                img_data = np.expand_dims(img_data, axis=0)
                img_data = preprocess_input(img_data)
                vgg16_feature = model.predict(img_data)
                vgg16_feature = np.reshape(vgg16_feature,(1,-1))
                f.write(str(c) + ":" + str(vgg16_feature[0][0]))
                for value in vgg16_feature[0][1:]:
                    f.write("," + str(value))
                f.write("\n")
    # Idea 2: this might be better, since Idea 1 maybe gave convolutional 
    # information between the sample, which is not there
    if True:
        print("Idea 2")
        with open("abstract_features_idea2.txt", 'w') as f:
            for c in range(17):
                img = data[str(c)]
                img = np.average(img, 0)
                # fill every bandwidth with 4 zeros to get a width of at leatst 224:
                img = np.append(img, [0,0,0,0])
                # we restrict ourselves on 500 samples, because using all crashed my pc really hard
                img = np.asarray([[img,img,img]] * 500)
                # rest: same as above
                img_data = np.asarray(img)
                img_data = np.swapaxes(img_data, 1, 2)
                img_data = np.expand_dims(img_data, axis=0)
                img_data = preprocess_input(img_data)
                vgg16_feature = model.predict(img_data)
                vgg16_feature = np.reshape(vgg16_feature,(1,-1))
                f.write(str(c) + ":" + str(vgg16_feature[0][0]))
                for value in vgg16_feature[0][1:]:
                    f.write("," + str(value))
                f.write("\n")
    # Idea 3: this is just a random idea, maybe some kind of de-composition is involved
    if True:
        print("Idea 3")
        with open("abstract_features_idea3.txt", 'w') as f:
            for c in range(17):
                img = data[str(c)]
                img = np.average(img, 0)
                # fill every bandwidth with 4 zeros to get a width of at leatst 224:
                img = np.append(img, [0,0,0,0])
                # now do weird vector multiplication:
                img = np.expand_dims(img, axis=0)
                img = np.matmul(np.transpose(img), img)
                # now add rgb channel:
                
                copy = np.zeros(shape=(224,224,3))
                copy[:,:,0] = img
                copy[:,:,1] = img
                copy[:,:,2] = img
                img_data = copy
                
                # rest: same as above
                img_data = np.expand_dims(img_data, axis=0)
                img_data = preprocess_input(img_data)
                vgg16_feature = model.predict(img_data)
                vgg16_feature = np.reshape(vgg16_feature,(1,-1))
                f.write(str(c) + ":" + str(vgg16_feature[0][0]))
                for value in vgg16_feature[0][1:]:
                    f.write("," + str(value))
                f.write("\n")
    



extract_abstract_features()    