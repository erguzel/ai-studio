
import aistudio.textprocess.text_prepare as tp

withHeader = False
inputPath = "examples/bbc4-articles/data/raw/bbc4"
targetPath = "examples/bbc4-articles/data/processed"
inputExtension= 'txt'
outputExtension='csv'
outputFolderName='bbc4'
label=""
index=0
separator=">>"

tp.merge_folder_labelled_text(inputPath,
                                         targetPath,
                                         inputExtension,
                                         outputExtension,
                                         outputFolderName,
                                         separator,
                                         withHeader)

