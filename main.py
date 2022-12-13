import numpy as np
import re
import nltk
from sklearn.datasets import  load_files
nltk.download('stopwords')
nltk.download('wordnet')
import  pickle
from nltk.corpus import stopwords





movie_data = load_files(r"data/raw/bbc4/")
X, y = movie_data.data, movie_data.target


from sklearn.model_selection import train_test_split
X_trainData, X_testData, y_trainData, y_testData = train_test_split(X, y, test_size=0.2, random_state=0)



documents = []

from nltk.stem import WordNetLemmatizer

stemmer = WordNetLemmatizer()

for sen in range(0, len(X)):
    # Remove all the special characters
    document = re.sub(r'\W', ' ', str(X[sen]))

    # remove all single characters
    document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)

    # Remove single characters from the start
    document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)

    # Substituting multiple spaces with single space
    document = re.sub(r'\s+', ' ', document, flags=re.I)

    # Removing prefixed 'b'
    document = re.sub(r'^b\s+', '', document)

    # Converting to Lowercase
    document = document.lower()

    # Lemmatization
    document = document.split()

    document = [stemmer.lemmatize(word) for word in document]
    document = ' '.join(document)

    documents.append(document)


from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
countVectorized = vectorizer.fit_transform(documents).toarray()

from sklearn.feature_extraction.text import TfidfTransformer
tfidfconverter = TfidfTransformer()
tfidTransformed = tfidfconverter.fit_transform(countVectorized).toarray()


## alternative need search
#from sklearn.feature_extraction.text import TfidfVectorizer
#tfidfconverter = TfidfVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
#X = tfidfconverter.fit_transform(documents).toarray()

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(tfidTransformed, y, test_size=0.2, random_state=0)

from sklearn.ensemble import RandomForestClassifier

classifier = RandomForestClassifier(n_estimators=1000, random_state=0)
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)


from sklearn.metrics import classification_report
target_names = ['business', 'entertainment', 'politics','sport','tech']
print(classification_report(y_test, y_pred, target_names=target_names))

print(X_testData[0])
print(y_pred[0])

print("-------------------------------------------")
print(X_testData[1])
print(y_pred[1])