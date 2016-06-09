import pandas as pd
from os import path
import os
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import re
import scipy as sp
import numpy as np
from scipy.stats import pearsonr
#matplotlib.style.use('ggplot')


def process(df,file_name):
  f = os.path.splitext(file_name)[0]
  f.replace('out','')
  f = f + '_err'
  print 'LENGTH DATA:',len(df['kw_energy_consumption']), 'LENGTH PREDICTIONS',len(df['prediction'])
  df[f] = sp.stats.pearsonr(df['kw_energy_consumption'],df['prediction'])
  #df[f] = df['kw_energy_consumption'] - df['prediction']
  #df['abs_err'] = df['error'].abs()
  #df[f] = df['abs_err'].rolling(window=30,center=False).mean()
  return df,f

mypath = '/home/sheiser1/nupic-master/examples/opf/clients/hotgym/prediction/one_gym/Dr_Zaychik_Data/selectedData'
only_csv_files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and os.path.splitext(f)[1] == '.csv']
root_path = './'
root_files = [f for f in listdir(root_path) if isfile(join(root_path, f)) and os.path.splitext(f)[1] == '.csv']
#only_csv_files.remove(base_model)
for file in only_csv_files:
  print file


#print '\n','DIFFERENCE___','\n'


#for file in root_files:
#  print file

# DO
prefix_sets = []
for name in only_csv_files:
	file_no_ext = os.path.splitext(name)[0] + '_'
	prefix_set = []
	for file_name in root_files:
		prefix = file_name[0:len(file_no_ext)]
		if prefix == file_no_ext:
	 		prefix_set.append(file_name)
	tup = (file_no_ext,prefix_set)
	prefix_sets.append(tup)

print "PREFIX SETS: ",prefix_sets
#data = None
#column_list = []
for prefix_set in prefix_sets:
	column_list = []
	base_model = ''	
	for file_name in prefix_set[1]:
		name = os.path.splitext(file_name)[0]
		if len(name)-3 == 2*(len(prefix_set[0])) and name.count(prefix_set[0]) == 2:
			base_model = prefix_set[1].pop(prefix_set[1].index(file_name))
			break

	data = pd.read_csv(base_model)
	data,base_f = process(data,base_model)
	column_list.append(base_f)
	for file in prefix_set[1]:
		df = pd.read_csv(file)
		df,f = process(df,file)
		data[f] = df[f]
		column_list.append(f)


	p = re.compile('\d+')
	col_labels = [p.findall(x)[1] for x in column_list]
	data.to_csv('All_Compared_'+base_f+'.csv')
	data_plot = data[column_list]

	ax= data_plot.plot.box()
	ax.set_xticklabels(col_labels)
	plt.title('Error of All Subjects -- Base Model ' + p.findall(base_model)[0])
	plt.xlabel('Subjects')
	plt.ylabel('Error')
	plt.savefig('All_Compared_'+base_f+'.png')
	#plt.show()

