import os
from sklearn.datasets import  load_files
import numpy as np
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from aistudio.model.model_utils import persist_ml_model
from exchelp.exception_helper import ReportObject, CoreException
from aistudio.data.meta.module_utils import object_from_module


#
############## Model Parameters ##################
#
main_report = ReportObject().adddata('_title_',os.path.basename(__file__)).\
    adddata('initialize_info',ReportObject().\
        adddata('source',r"examples/bbc4-articles/data/raw/bbc4").\
        adddata('extension','.txt').\
        adddata('type','text-document')
    ).\
    adddata('cleanse_info',ReportObject().\
        adddata('char_cleaner_function',ReportObject().\
            adddata('module','aistudio.data.text_utils').\
            adddata('object','clear_default_chars')

        ).\
        adddata('stemming_lemmatization_function',ReportObject().\
            adddata('module','aistudio.data.text_utils').\
            adddata('object','stemming_lematization')
        ).\
        adddata('stemmer_or_lemmatizer_instance',ReportObject().\
                adddata('module','nltk.stem').\
                adddata('object','WordNetLemmatizer')
            )
    ).\
    adddata('prepare_info',ReportObject().\
        adddata('vectorizer_instance',ReportObject().\
            adddata('module','sklearn.feature_extraction.text').\
            adddata('object','CountVectorizer').\
            adddata('hyper_params',ReportObject().\
                adddata('max_features',1500).\
                adddata('min_df',5).\
                adddata('max_df',0.7)
            ).\
            adddata('stop_words_function',ReportObject().\
                    adddata('module','nltk.corpus').\
                    adddata('object','stopwords').\
                    adddata('subObject','words')
            ).\
            adddata('language','english')
        ).\
        adddata('transformer_instance',ReportObject().\
            adddata('module','sklearn.feature_extraction.text').\
            adddata('object','TfidfTransformer')
        ).\
        adddata('test_size',0.2).\
        adddata('random_state',0)
    ).\
    adddata('execute_info',ReportObject().\
        adddata('model_instance',ReportObject().\
            adddata('module','sklearn.ensemble').
            adddata('object','RandomForestClassifier').\
            adddata('hyper_params',ReportObject().\
                adddata('n_estimators',1000).\
                adddata('random_state',0)
            )
        )
    )
#
#################################################################################
#

#
# Initialize
#
data_source = main_report.getdata('initialize_info')['source']
try:
    movie_data = load_files(data_source)
except Exception as e:
    CoreException('data load failed',e,logIt=True,dontThrow=True,shouldExit=True).act()
X, y = np.array(movie_data.data), np.array(movie_data.target)

main_report.getdata('initialize_info')['raw_number']=len(X)

#
# Cleanse
#

#char cleaning
moduleName = main_report.getdata('cleanse_info')['char_cleaner_function']['module']
objectName = main_report.getdata('cleanse_info')['char_cleaner_function']['object']
docs = object_from_module(moduleName=moduleName,objectName=objectName)(data=X)

#stemming-lemmatization cleaning
moduleName = main_report.getdata('cleanse_info')['stemmer_or_lemmatizer_instance']['module']
objectName = main_report.getdata('cleanse_info')['stemmer_or_lemmatizer_instance']['object']
stem_or_lemmatizer_instance = object_from_module(moduleName=moduleName,objectName=objectName)()

moduleName = main_report.getdata('cleanse_info')['stemming_lemmatization_function']['module']
objectName = main_report.getdata('cleanse_info')['stemming_lemmatization_function']['object']
docs = object_from_module(moduleName=moduleName,objectName=objectName)(stem_or_lemmatizer=stem_or_lemmatizer_instance,data=X)

#
# Prepare
#

#   stopwords
moduleName = main_report.getdata('prepare_info')['vectorizer_instance']['stop_words_function']['module']
objectName = main_report.getdata('prepare_info')['vectorizer_instance']['stop_words_function']['object']
subObjectName = main_report.getdata('prepare_info')['vectorizer_instance']['stop_words_function']['subObject']
stop_words_language = main_report.getdata('prepare_info')['vectorizer_instance']['language']
stop_words = object_from_module(moduleName=moduleName,objectName=objectName,subObjectName=subObjectName)(stop_words_language)

#   vectorizer
vectorizer_instance_params = main_report.getdata('prepare_info')['vectorizer_instance']['hyper_params']
moduleName = main_report.getdata('prepare_info')['vectorizer_instance']['module']
objectName = main_report.getdata('prepare_info')['vectorizer_instance']['object']
vectorizer_instance = object_from_module(moduleName,objectName)(**vectorizer_instance_params,stop_words = stop_words)
vectorized_count = vectorizer_instance.fit_transform(docs).toarray()

#   transformer
moduleName = main_report.getdata('prepare_info')['transformer_instance']['module']
objectName = main_report.getdata('prepare_info')['transformer_instance']['object']
transformer_instance = object_from_module(moduleName=moduleName,objectName=objectName)()
transformed_vector = transformer_instance.fit_transform(vectorized_count).toarray()

test_size = objectName = main_report.getdata('prepare_info')['test_size']
random_state = objectName = main_report.getdata('prepare_info')['random_state']
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(transformed_vector, y, test_size=test_size, random_state=random_state)


#
# Execute
#
moduleName = main_report.getdata('execute_info')['model_instance']['module']
objectName = main_report.getdata('execute_info')['model_instance']['object']
model_instance_parameters = main_report.getdata('execute_info')['model_instance']['hyper_params']
model_instance = object_from_module(moduleName=moduleName,objectName=objectName)(**model_instance_parameters)
model_instance.fit(X_train, y_train)

#
# Reportize
#
from sklearn.metrics import classification_report
y_pred = model_instance.predict(X_test)
target_names = ['business', 'entertainment', 'politics','sport','tech']
classification_performance = classification_report(y_test, y_pred, target_names=target_names,output_dict=True)
print(classification_report(y_test, y_pred, target_names=target_names))


model_name = main_report.getdata('execute_info')['model_instance']['object']+'.sav'
run_title = main_report.getdata('_title_')

main_report.adddata('metric_info',ReportObject().\
    adddata('model_name',model_name).\
    adddata('target_names',target_names).\
    adddata('summary',classification_performance)
    )

persist_ml_model(modelName=model_name,trainedModel = model_instance,runTitle=run_title,mainReport=main_report)


