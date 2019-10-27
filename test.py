import os,re,codecs

withHeader = False
inputPath = "data/raw/bbc 4"
targetPath = "data/processed"
inputExtension= 'txt'
outputExtension='csv'
label=""
index=0
separator=">>"

from src.prep import dataPreparer

dataPreparer.create_multiclassifier_data(inputPath,
                                         targetPath,
                                         inputExtension,
                                         outputExtension,
                                         separator,
                                         withHeader)

