# -*- coding: utf-8 -*-
#
## author: amanul haque
#

import numpy as np
import pandas as pd
import sys
from word_to_vec_vectorizer import vectorization
from data_preprocessing_1 import data_preprocessing_1
from data_preprocessing_2 import data_preprocessing_2
from data_preprocessing_3 import data_preprocessing_3
from semi_supervised_classification import semi_supervised_classification

class main_file:
    
    def __init__(self):
        
        self.input_file_path = "input_file.xlsx"
        self.output_file_path = "output_file_3.csv"
        
    def get_input_text_and_label(self, df):
        #print(data['text'])
        X = np.array(df['text'])
        y = np.array(df['label'])
        
        return X, y
    
    def get_test_train_split(self, X, y):
        labelled_set = np.array(range(6))
        unlabelled_set = np.array(range(6,len(y)))
        y[unlabelled_set] = -1
        
        return y, labelled_set, unlabelled_set

    
    def get_vectorized_data(self, X, y, labelled_set, unlabelled_set):
        vectorizor = vectorization()
        #X, y = vectorizor.get_data(filepath)
        X_train, y_train, X_test = vectorizor.vectorize_text(X, y, labelled_set, unlabelled_set)
        return  X_train, y_train, X_test
    
    def update_dataframe(self, df, X):
        
        i = 0
        column_headers = df.columns.values
        df_new = pd.DataFrame(columns=column_headers)
        
        for index, row in df.iterrows():
            row['text'] = X[i]
            df_new.loc[i] = row
            i += 1
        return df_new
    
if __name__ == '__main__':
    
    mf = main_file()
    df = pd.read_excel(mf.input_file_path, sep=',')
    X, y = mf.get_input_text_and_label(df)
    X = data_preprocessing_1().process_data(X)
    X = data_preprocessing_2().process_data(X)    
    X = data_preprocessing_3().preprocess_text(X)
    df = mf.update_dataframe(df, X)
    df.to_csv(mf.output_file_path)
    
    y, labelled_set, unlabelled_set = mf.get_test_train_split(X, y)
    X_train, y_train, X_test = mf.get_vectorized_data(X, y, labelled_set, unlabelled_set)
    
    sample_rate=0.2
    final_labels = semi_supervised_classification().pseudo_labelling(y, X_train, y_train, X_test, labelled_set, unlabelled_set, sample_rate)
    
    print("y : ", y)
    print("labelled_set : ", labelled_set)
    print("unlablled_set : ", unlabelled_set)
    
    print(X_train.shape)
    print(y_train.shape)
    print(X_test.shape)
    print("final_labels :", final_labels)
    
    #df = mf.update_dataframe(df, X)
    #df.to_csv(mf.output_file_path)
    
    
        
    