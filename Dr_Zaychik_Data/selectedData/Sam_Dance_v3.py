import xlrd
import csv
import os
from os import listdir
from os.path import isfile, join
import datetime
from datetime import timedelta

mypath = './'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and os.path.splitext(f)[1] == '.csv']

	
                
