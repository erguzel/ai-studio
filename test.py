import os,re,codecs
import numpy

a = numpy.array([[1, 2, 3]])

asd = a[0]

zerro = numpy.zeros(10)

newasd = numpy.concatenate([asd,zerro])

a = numpy.array([newasd])

print(newasd)


withHeader = False
inputPath = "data/raw/bbc 4"
targetPath = "data/processed"
inputExtension= 'txt'
outputExtension='csv'
outputFolderName='bbc4'
label=""
index=0
separator=">>"

from src.prep import dataPreparer

dataPreparer.create_multiclassifier_data(inputPath,
                                         targetPath,
                                         inputExtension,
                                         outputExtension,
                                         outputFolderName,
                                         separator,
                                         withHeader)

