import csv, scipy.stats as stats, os, pandas as pd

mydir = "./Prediction_Results/"

for csv_file in os.listdir(mydir):
    df = pd.read_csv(csv_file, header=True)
    
        