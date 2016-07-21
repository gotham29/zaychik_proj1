import csv, scipy.stats as stats, os, pandas as pd, re

mydir = "./Prediction_Results/"
reg = r"[0-9]{1,2}"
files = [x for x in os.listdir(mydir) if os.path.splitext(x)[1] == ".csv"]

data_dict = {}
for csv_file in files:
    df = pd.read_csv(os.path.join(mydir,csv_file))
    pred = df["prediction"]
    match = re.findall(reg, csv_file)
    base = match[0]
    target =  match[1]
    if base not in data_dict:
        data_dict[base] = {target:pred}
    else:
        if target not in data_dict[base]:
            data_dict[base][target] = pred

t_dict = {}
for key, value in data_dict.iteritems():
    base_df = data_dict[key][key]
    for subkey, subvalue in data_dict[key].iteritems():
        if subkey != key:
            t_value = stats.ttest_ind(base_df, data_dict[key][subkey])
            if key not in t_dict:
                t_dict[key] = {subkey: t_value}
            else:
                t_dict[key][subkey] = t_value
            
t_scores = pd.DataFrame.from_dict(t_dict)
t_scores.to_csv("T_Scores.csv")
        