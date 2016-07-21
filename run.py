#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
"""
Groups together code used for creating a NuPIC model and dealing with IO.
(This is a component of the One Hot Gym Prediction Tutorial.)
"""
import os
import importlib
import sys
import csv
import datetime
from os import path
from os import listdir
from os.path import isfile, join

from nupic.data.inference_shifter import InferenceShifter
from nupic.frameworks.opf.metrics import MetricSpec
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.predictionmetricsmanager import MetricsManager
from nupic.frameworks.opf.model import Model

import nupic_output


DESCRIPTION = (
  "Starts a NuPIC model from the model params returned by the swarm\n"
  "and pushes each line of input from the gym into the model. Results\n"
  "are written to an output file (default) or plotted dynamically if\n"
  "the --plot option is specified.\n"
  "NOTE: You must run ./swarm.py before this, because model parameters\n"
  "are required to run NuPIC.\n"
)
mypath = './Dr_Zaychik_Data/selectedData'
only_csv_files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and os.path.splitext(f)[1] == '.csv']
for file in only_csv_files:
  print file

GYM_NAME = "subj_3"  # or use "rec-center-every-15m-large"
DATA_DIR = "./Dr_Zaychik_Data/selectedData"
MODEL_PARAMS_DIR = "./model_params"
# '7/2/10 0:00'
DATE_FORMAT = "%m/%d/%y %H:%M"

_METRIC_SPECS = (
    MetricSpec(field='Error', metric='multiStep',
               inferenceElement='multiStepBestPredictions',
               params={'errorMetric': 'aae', 'window': 1000, 'steps': 1}),
    MetricSpec(field='Error', metric='trivial',
               inferenceElement='prediction',
               params={'errorMetric': 'aae', 'window': 1000, 'steps': 1}),
    MetricSpec(field='Error', metric='multiStep',
               inferenceElement='multiStepBestPredictions',
               params={'errorMetric': 'altMAPE', 'window': 1000, 'steps': 1}),
    MetricSpec(field='Error', metric='trivial',
               inferenceElement='prediction',
               params={'errorMetric': 'altMAPE', 'window': 1000, 'steps': 1}),
)

def createModel(modelParams):
  model = ModelFactory.create(modelParams)
  model.enableInference({"predictedField": "Error"})
  return model



def getModelParamsFromName(gymName):
  importName = "model_params.%s_model_params" % (
    gymName.replace(" ", "_").replace("-", "_")
  )
  print "Importing model params from %s" % importName
  try:
    importedModelParams = importlib.import_module(importName).MODEL_PARAMS
  except ImportError:
    raise Exception("No model params exist for '%s'. Run swarm first!"
                    % gymName)
  return importedModelParams



def runIoThroughNupic(inputData, model, gymName, plot):
  inputFile = open(inputData, "rb")
  csvReader = csv.reader(inputFile)
  # skip header rows
  csvReader.next()
  csvReader.next()
  csvReader.next()

  shifter = InferenceShifter()
  if plot:
    output = nupic_output.NuPICPlotOutput([gymName])
  else:
    output = nupic_output.NuPICFileOutput([gymName])

  metricsManager = MetricsManager(_METRIC_SPECS, model.getFieldInfo(),
                                  model.getInferenceType())

  counter = 0
  for row in csvReader:
    counter += 1
    timestamp = datetime.datetime.strptime(row[0], DATE_FORMAT)
    consumption = float(row[1])
    result = model.run({
      "timestamp": timestamp,
      "Error": consumption
    })
    result.metrics = metricsManager.update(result)

    if counter % 100 == 0:
      print "Read %i lines..." % counter
      print ("After %i records, 1-step altMAPE=%f" % (counter,
              result.metrics["multiStepBestPredictions:multiStep:"
                             "errorMetric='altMAPE':steps=1:window=1000:"
                             "field=Error"]))

    if plot:
      result = shifter.shift(result)

    prediction = result.inferences["multiStepBestPredictions"][1]
    output.write([timestamp], [consumption], [prediction])

  inputFile.close()
  output.close()



def runModel(file_list, plot=False):
  for file1 in file_list:
    save = False
    file_name = os.path.splitext(file1)[0]
    path = '/home/sheiser1/nupic-master/examples/opf/clients/hotgym/prediction/one_gym/' + file_name
    model = None
    if os.path.exists(path):
      model = Model.load(path)
    else:
      model = createModel(getModelParamsFromName(GYM_NAME))
      save = True
      
    print "Creating model from %s..." % file_name
    inputData = "%s/%s.csv" % (DATA_DIR, file_name.replace(" ", "_"))
    runIoThroughNupic(inputData, model, file_name, plot)
    if save:
      model.save(path)

    for file2 in file_list:
      file2_name = os.path.splitext(file2)[0]
      model.disableLearning()    
      print "Running model" + file_name + 'on' + file2_name 
      inputData = "%s/%s.csv" % (DATA_DIR, file2_name.replace(" ", "_"))
      runIoThroughNupic(inputData, model, file2_name, plot)
      os.rename(file2_name+'_out.csv',file_name + '_'+file2_name + '_out.csv')  

if __name__ == "__main__":
  print DESCRIPTION
  plot = False
  new_model = False
  args = sys.argv[1:]
  if "--plot" in args:
    plot = True
  runModel(only_csv_files,plot=plot)
  
