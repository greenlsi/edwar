
# IBI VARIABLES

MAX_HR = 220        # Haskell & Fox based
MIN_HR = 40         # U.S. Department of Health and Human Services - National Ites of Health // Bradycardia record limit
MAX_DIFF_IBI = 0.2  # maximum ibi gradient value in seconds: theoretically 0.1s as
MAX_ERROR_MARGIN_TS = 0.01  # error in seconds allowed in IBI file clock
MAX_CORRECTION_TIME = 60  # seconds
MAX_VAR = 0.05      # artificial variability of added IBIs
MIN_SAMPLES = 1     # min samples to calculate HR
HR_FREQ = 1         # sample frequency of HR in seconds

MAX_IBI = 60 / MIN_HR
MIN_IBI = 60 / MAX_HR
