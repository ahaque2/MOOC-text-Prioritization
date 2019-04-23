# -*- coding: utf-8 -*-
#
# author: Amanul Haque
#
# File Description: This code impkements Model 1 (filtering model) with 10-fold cross-validation

#
from sklearn.model_selection import StratifiedKFold
from semi_supervised_classification import semi_supervised_classification

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from supervised_models import classification
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

from sklearn.base import BaseEstimator, TransformerMixin
from collections import Counter

from sklearn.pipeline import Pipeline, FeatureUnion
import sys
import sklearn
import numpy as np

class Custom_features_2(BaseEstimator, TransformerMixin):
    #normalise = True - devide all values by a total number of tags in the sentence
    #tokenizer - take a custom tokenizer function
    def __init__(self, key):        
        self.key = key
        
    # fit() doesn't do anything, this is a transformer class
    def fit(self, X, y = None):
        return self

    #all the work is done here
    def transform(self, X):
        return np.transpose(np.matrix(X[self.key]))
    
    
class Custom_features(BaseEstimator, TransformerMixin):
    #normalise = True - devide all values by a total number of tags in the sentence
    #tokenizer - take a custom tokenizer function
    def __init__(self, key):        
        self.key = key
        
    # fit() doesn't do anything, this is a transformer class
    def fit(self, X, y = None):
        return self

    #all the work is done here
    def transform(self, X):
        return X[self.key]  
    

class filtering_model:
    
    def __init__(self):
        self.x = 0
        self.cl = classification()
        
    def classification_rep(self, X_test, y_true, clf):
        y_pred = clf.predict(X_test)
        target_names = ['Non_Urgent', 'Urgent']
        return classification_report(y_true, y_pred, target_names=target_names)
    
    def confusion_mat(self, X_test, y_true, clf):
        y_pred = clf.predict(X_test)
        return confusion_matrix(y_true, y_pred, labels=[0, 1])  

        
    def stratified_cross_validation(self, X_labelled, y_labelled, X_unlabelled, y, labelled_set, unlabelled_set):
        skf = StratifiedKFold(n_splits=10, random_state=None, shuffle=False)
        labels = np.copy(y)
        final_confusion_matrix = [[0,0],[0,0]] 
        for train_index, test_index in skf.split(X_labelled, y_labelled):
            y = np.copy(labels)
            print("TRAIN:", train_index, "TEST:", test_index)
            X_train, X_test = X_labelled[train_index], X_labelled[test_index]
            y_train, y_test = y_labelled[train_index], y_labelled[test_index]
            labelled_set = train_index
            print("y shape before ", y.shape)
            print("Y before ", y)
            y = np.delete(y, test_index)
            print("y shape after ", y.shape)
            print("y after ", y)
            sample_rate=0.2
            print("Y before ", labels)
            print("X train ", X_train.shape)
            print("X test ", X_test.shape)
            final_labels, clf = semi_supervised_classification().pseudo_labelling(y, X_train, y_train, X_unlabelled, labelled_set, unlabelled_set, sample_rate)
            #final_labels, clf = self.cl.expectation_maximization(X_train, y_train, X_unlabelled)
            #final_labels, clf = self.cl.label_spreading(X_train, y, X_unlabelled)
            print("Y after ", labels)
            pred_labels = clf.predict(X_test)
            print("pred_labels :", pred_labels, "\tReal labels: ", y_test)
            print(self.classification_rep(X_train, y_train, clf))
            confusion_matrix = self.confusion_mat(X_test, y_test, clf)
            print(confusion_matrix)
            tn, fp, fn, tp = confusion_matrix.ravel()
            print(tn, fp, fn, tp)
            final_confusion_matrix[0][0] += tn
            final_confusion_matrix[0][1] += fp
            final_confusion_matrix[1][0] += fn
            final_confusion_matrix[1][1] += tp

            print("Final confiusion matrix ", final_confusion_matrix)  
        
        tp, fp, fn, tp = final_confusion_matrix[0][0], final_confusion_matrix[0][1], final_confusion_matrix[1][0], final_confusion_matrix[1][1]
        overall_precision = tp/(tp + fp)
        overall_recall = tp/(tp + fn)
        overall_accuracy = (tp + tn)/(tp + tn + fp + fn)
        overall_f1_score = 2 * overall_precision * overall_recall / (overall_precision + overall_recall)
        return np.array(final_confusion_matrix), overall_precision, overall_recall, overall_accuracy, overall_f1_score
    
    
    def skfold_cv(self, X1, y1, X2, y2, response_labels, labelled_set, unlabelled_set, ppl, data, ngrams, semi_clf):
        
        skf = StratifiedKFold(n_splits=10, random_state=None, shuffle=False)
        labels = np.copy(y2)
        final_confusion_matrix = [[0,0],[0,0]] 
        X_labelled = X2[labelled_set]
        y_labelled = y2[labelled_set]
        X_unlabelled = X2[unlabelled_set]
        y_unlabelled = y2[unlabelled_set]
        
        for train_index, test_index in skf.split(X_labelled, y_labelled):
            y2 = np.copy(labels)
            #print("TRAIN:", train_index, "TEST:", test_index)
            print("Train_index_shape ", train_index.shape, "\t Test index shape ", test_index.shape)
            X_train, X_test = X_labelled[train_index], X_labelled[test_index]
            y_train, y_test = y_labelled[train_index], y_labelled[test_index]
            response_labels_train = response_labels[train_index]
            
            X_train_clf1 = np.concatenate((X1, X_train),axis=0)
            y_train_clf1 = np.concatenate((y1, response_labels_train),axis=0)
            y_train_clf1 = y_train_clf1.astype(int)
                        
            ppl.fit(X_train_clf1, y_train_clf1)
            y_unlabelled_pred = ppl.predict(X_unlabelled)
            filtered_index = np.where(y_unlabelled_pred == 1)[0]
            filtered_index_orig = unlabelled_set[filtered_index]
            #print(filtered_index)
            print("Filtered index shape", filtered_index_orig.shape)
            y_test_new = y2[filtered_index_orig]
            y_ = np.concatenate((y_train, y_test_new), axis=0)
            
            
            cl = classification()
            X_current_unlabelled = X_unlabelled[filtered_index]
            
            train_index_orig = labelled_set[train_index]
            test_index_orig = labelled_set[test_index]
            d = data.iloc[filtered_index_orig,:]
            #print(d['Label'])
            for l, d in zip(d['Urgency'],d):
                if(l == 1 or l==0):
                    print("yes")
                    print(d)
                    sys.exit()
            combined_train_index_orig = np.concatenate((train_index_orig, test_index_orig, filtered_index_orig),axis=0)
            #print("combined_train_index_orig : ",combined_train_index_orig.shape)
            train_df_clf2 = data.iloc[combined_train_index_orig,:]
            print("train_df_clf2", train_df_clf2.shape)
            
            pipeline = Pipeline([
                # Use FeatureUnion to combine the features from subject and body
                ('union', FeatureUnion(
                    transformer_list=[
            
                        # Pipeline for pulling features from the post's subject line
                        ('deadline_ppl', Pipeline([
                            ('selector', Custom_features_2(key = 'deadline_weight')),
                        ])),
            
                        # Pipeline for standard bag-of-words model for body
                        ('text_ppl', Pipeline([
                            ('selector', Custom_features(key = 'Text')),
                            ('tfidf', TfidfVectorizer(ngram_range = ngrams, use_idf=True, smooth_idf=True, norm='l2')),
                        ]))
            
                    ],
            
                    # weight components in FeatureUnion
                    transformer_weights={
                        'deadline_ppl': 1.0,
                        'text_ppl': 1.0,
                    },
                )),
            ])
                
            X_vec = pipeline.fit_transform(train_df_clf2)
            print(X_vec.shape)
            
            
            X_train_vec = X_vec[0:train_index.shape[0]]
            X_test_vec = X_vec[train_index.shape[0]:(train_index.shape[0]+test_index.shape[0])]
            X_unlabelled_vec = X_vec[-X_current_unlabelled.shape[0]:]
            print(X_vec.shape, X_train_vec.shape, X_unlabelled_vec.shape, X_test_vec.shape)  
            
           
            if(semi_clf == 'LS'):
                predicted_labels, clf = cl.label_spreading(X_train_vec, y_, X_unlabelled_vec)
            elif(semi_clf == 'EM'):
                predicted_labels, clf = cl.expectation_maximization(X_train_vec, y_train, X_unlabelled_vec)
            
            unique, counts = np.unique(predicted_labels, return_counts=True)
            print("Predicted label summary ", dict(zip(unique, counts)))
            y_pred = clf.predict(X_test_vec)
            print("pred_labels :", y_pred, "\tReal labels: ", y_test)
            confusion_matrix = sklearn.metrics.confusion_matrix(y_test, y_pred)
            print(confusion_matrix)
            tn, fp, fn, tp = confusion_matrix.ravel()
            final_confusion_matrix[0][0] += tn
            final_confusion_matrix[0][1] += fp
            final_confusion_matrix[1][0] += fn
            final_confusion_matrix[1][1] += tp

        tn, fp, fn, tp = np.array(final_confusion_matrix).ravel()
        
        u_precision = tp/(tp + fp)
        u_recall = tp/(tp + fn)
        u_f1_score = 2 * u_precision * u_recall / (u_precision + u_recall)
        
        non_u_precision = tn/(tn + fn)
        non_u_recall = tn/(tn + fp)
        non_u_f1_score = 2 * non_u_precision * non_u_recall / (non_u_precision + non_u_recall)
        
        
        accuracy = (tp + tn)/(tp + tn + fp + fn)
        
        return np.array(final_confusion_matrix), u_precision, u_recall, u_f1_score, non_u_precision, non_u_recall, non_u_f1_score, accuracy