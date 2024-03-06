import pandas as pd 


class FeaturesExtractor:
    ''' Father class to extract features from a given data type. 
    The extractor for each feature is a class that inherits from this one.
    '''

    def __init__(self,data,fs):
        """Constructor

        Args:
            data (pd.DataFrame): Input data from which the features will be extracted
            fs (float): Sampling frequency of the data
        """
        self.data = data
        self.fs = fs

        class_funcs = [ f for f in dir(self) if '__' not in f and f not in ['data','fs','run']]
        self.preprocessing= dict()
        for c in class_funcs:
            self.preprocessing[c] = getattr(self,c)
        
    

    def run(self,window_size,window_overlap,features2extract):
        """ Method to extract specified features from the data in certain time window

        Args:
            window_size (int): Seconds to window the data
            window_overlap (int): Seconds to overlap the windows
            features2extract (list): List of features to extract

        Raises:
            NameError: If the preprocessing function does not exist

        Returns:
            pd.DataFrame: features extracted
        """
        
        features = pd.DataFrame()
        print(self.preprocessing.keys())
        for step in features2extract:
            if step not in self.preprocessing.keys():
                raise NameError(f"{step} function does not exist")
            act_features = self.preprocessing[step](window_size,window_overlap)
            features = pd.concat([features,act_features],axis=1)
        return features
    
    #@preprocessing
    def statistics(self,window_size,window_overlap):
        """ Method to extract statistics features from the data

        Args:
            window_size (int): Seconds to window the data
            window_overlap (int): Seconds to overlap the windows
        Returns:
            pd.DataFrame: statistics features extracted
        """

        window_size = int(window_size/self.fs)
        window_step = int((window_size - window_overlap) / self.fs)
        stats2apply = ['mean','std','median','var','min','max']
        output = self.data.rolling(window_size,step=window_step).agg(stats2apply)

        return output
    
'''
class example(FeaturesExtractor):
    def __init__(self,data,fs):
        super().__init__(data,fs)


    # @preprocessing
    def count(self,window_size,window_overlap):
        return self.data.count()

import numpy as np 
data= pd.DataFrame(dict(a=np.zeros(10),b=np.arange(10)),
                   index= pd.date_range("2018-01-01", periods=10, freq="s"))
fe = FeaturesExtractor(data,fs=1)
r = fe.run(2,0,['statistics'])

fe = example(data,fs=1)
r = fe.run(2,0,['statistics','count'])

fe = FeaturesExtractor(data,fs=1)
r = fe.run(2,0,['statistics','count'])
print(r)
'''

