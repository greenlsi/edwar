from abc import ABC, abstractmethod

class FeaturesExtractor(ABC):

    def __init__(self,data,fs,window_size,window_overlap,features2extract):
        """_summary_

        Args:
            data (pd.DataFrame): 
            fs (float): 
            window_size (int): 
            window_overlap (int): 
            features2extract (list): 
        """
        super().__init__()

    @abstractmethod
    def run(self, data):
        pass

    