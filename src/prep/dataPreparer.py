import os,re,codecs

def create_multiclassifier_data(
    inputPath,
    targetPath,
    inputExtension,
    outputExtension,
    outputFolderName,
    separator,
    withHeader
):

    label = ""
    index = 0
    csvLine = ""
    processedDataList = ""
    fileName = ""
    addedHeader = False

    lastIndex = len(re.split("[\/\\\]", inputPath)) - 1
    fileName = re.split("[\/\\\]", inputPath)[lastIndex]

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(inputPath):
        for file in f:
            if "." + inputExtension in file:
                absfile = os.path.join(r, file)
                indexLast = len(re.split("[\/\\\]", absfile)) - 1
                label = re.split("[\/\\\]", absfile)[indexLast - 1]
                content = open(absfile, "rb").read()
                csvLine = "{0}{1}{2}{1}{3}".format(str(index), separator, content, label)
                if (withHeader):
                    if (not addedHeader):
                        processedDataList += "id{0}content{0}label\n".format(separator)
                        addedHeader = True

                if (not csvLine in processedDataList):
                    processedDataList += csvLine + ';;'
                    index = index + 1

    if len(outputFolderName)> 0:
        fileName = outputFolderName;
    outPath = os.path.join(targetPath, fileName)
    saveFile = "{0}.{1}".format(outPath, outputExtension)
    open(saveFile, "w").write(processedDataList)
    print("{0} data created with separator '{1}'.".format(os.path.abspath(saveFile),separator))
