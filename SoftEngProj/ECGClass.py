#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
import numpy as np
import joblib
import tensorflow.keras as keras
import matplotlib.pyplot as plt
import sys
import os
import warnings
#import tensorflow as tf


# In[9]:


class ECGClassifier:
    def __init__(self):
        #self.filename = None
        self.dataframe = None
        self.model = None
        self.X_normalized = None
        self.class_labels = None
        #self.list_labels = None
        
    def load_data(self,filename):

        if not os.path.isfile(filename):
            print("File not found:", filename)
            sys.exit(1)
        self.dataframe = pd.read_csv(filename, index_col=None, header=None)
        self.preprocess_data()
    def preprocess_data(self):
        loaded_scaler = joblib.load('scaler.pkl')
        self.X_normalized = loaded_scaler.transform(self.dataframe)

    def load_model(self):
        with open("ecg_architecture.json", "r") as json_file:
            self.model = keras.models.model_from_json(json_file.read())
        self.model.load_weights("ecg_weights.h5")
    def predict(self):
        predictions = self.model.predict(self.X_normalized, verbose=0)
        self.class_labels = (predictions >= 0.5).astype(int)
        #return self.class_labels

    def print_predictions(self):
        list_labels =[]
        for i in range(self.dataframe.shape[0]):
            if self.class_labels[i][0] == 0:
                list_labels.append('Normal')
            else:
                list_labels.append('Abnormal')
            #list_labels.append(self.class_labels[i][0])
            #print(self.class_labels[i][0])
        return list_labels
            


# In[10]:


def main():
    #if len(sys.argv) != 2:
    #    print("Usage: %s [csv]" % (sys.argv[0]))
    #    sys.exit(1)
    #filename = sys.argv[1]
    filename = 'Test.csv'
    '''
    ecg_classifier = ECGClassifier()
    ecg_classifier.load_data(filename)
    ecg_classifier.preprocess_data()
    ecg_classifier.load_model()
    ecg_classifier.predict()
    ecg_classifier.print_predictions()
    
    '''
    ecg_classifier = ECGClassifier()
    ecg_classifier.load_model()
    ecg_classifier.load_data(filename)
    ecg_classifier.predict()
    ecg_classifier.print_predictions()


# In[11]:


if __name__ == '__main__':
    main()


# In[ ]:




