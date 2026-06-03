import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

# Load dataset
data = pd.read_csv("data/financial_data.csv")

X = data['Description']
y = data['Category']

vectorizer = CountVectorizer()
X_vec = vectorizer.fit_transform(X)

model = MultinomialNB()
model.fit(X_vec, y)

with open('model.pkl', 'wb') as f:
    pickle.dump((vectorizer, model), f)

print("Model trained and saved as model.pkl")
