import xlrd
import csv
import os
from os import listdir
from os.path import isfile, join
import datetime
from datetime import timedelta

mypath = './'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for file in onlyfiles:
    filename, file_extension = os.path.splitext(file)
    if file_extension == '.xls':
        xl_workbook = xlrd.open_workbook(file)
        sheet_names = xl_workbook.sheet_names()
        print('Sheet Names', sheet_names)
        
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])       
        data = []
        for row_idx in range(0, xl_sheet.nrows):    # Iterate through rows
            data_row = []
            for col_idx in range(0, xl_sheet.ncols):  # Iterate through columns
                data_row.append(xl_sheet.cell(row_idx, col_idx).value)  # Get cell object by row, col
            data.append(data_row)
        
        for row in data:
            row[0] *= 100
            
        #csv_file = join(filename,'.csv')
        csv_file = filename+'.csv'
        with open(csv_file,'wb') as w:
            writer = csv.writer(w)
            date = datetime.datetime.now()
            first = True
            for row in data:
                time = row[0]
                error = row[1] + row[2]
                row.append(error)
                if first:
                    writer.writerow(['Time','Error'])
                    writer.writerow(['datetime','float'])
                    writer.writerow(['T','','',''])
                    writer.writerow([date.strftime('%m/%d/%y %H:0')] + [row[1]])
                    first = False
                    continue
                next_date = date + timedelta(time,0)
                writer.writerow([next_date.strftime('%m/%d/%y %H:0')] + [row[1]])
                
                
