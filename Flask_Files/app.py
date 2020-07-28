from flask import Flask, redirect, url_for, render_template, request, jsonify
import numpy as np
import pandas as pd
import praw
import sklearn
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.externals import joblib
import emoji
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import re



app = Flask(__name__)

# --------------------------------------------------------------------------------
reddit = praw.Reddit(client_id = "#", 
                     client_secret = "#", 
                     user_agent = "#")

#nltk.download('punkt')
#nltk.download('stopwords')
stop=set(stopwords.words('english'))

def remove_stopwords(text):
        if text is not None:
            tokens = [x for x in word_tokenize(text) if x not in stop]
            return " ".join(tokens)
        else:
            return None
def remove_punct(text):
    exclude = set(string.punctuation)
    s = ''.join(ch for ch in text if ch not in exclude)
    return s
def remove_html(text):
    html=re.compile(r'<.*?>')
    return html.sub(r'',text)
def remove_URL(text):
    url = re.compile(r'https?://\S+|www\.\S+')
    return url.sub(r'',text)
def remove_emoji(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  
                           u"\U0001F680-\U0001F6FF"  
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)
def clean_df(test_data, train=True):
    test_data["dirty_title"] = test_data['title']
    test_data["dirty_body"] = test_data['body']
    
    test_data["title"] = test_data['title'].apply(lambda x : x.lower())
    test_data["title"] = test_data['title'].apply(lambda x: remove_emoji(x))
    test_data["title"] = test_data['title'].apply(lambda x : remove_URL(x))
    test_data["title"] = test_data['title'].apply(lambda x : remove_html(x))
    test_data["title"] = test_data['title'].apply(lambda x : remove_stopwords(x))     
    test_data["title"] = test_data['title'].apply(lambda x : remove_punct(x))    
    test_data.title = test_data.title.replace('\s+', ' ', regex=True)
    
    test_data["body"] = test_data['body'].apply(lambda x : x.lower())
    test_data["body"] = test_data['body'].apply(lambda x: remove_emoji(x))
    test_data["body"] = test_data['body'].apply(lambda x : remove_URL(x))
    test_data["body"] = test_data['body'].apply(lambda x : remove_html(x))
    test_data["body"] = test_data['body'].apply(lambda x : remove_stopwords(x))     
    test_data["body"] = test_data['body'].apply(lambda x : remove_punct(x))    
    test_data.body = test_data.body.replace('\s+', ' ', regex=True)
    return test_data    
# --------------------------------------------------------------------------------
def predict(link):
    
    
    submission = reddit.submission(url=link)
    
    test = {"title":[],  "body":[]}
    test['title'].append(submission.title)
    test['body'].append(submission.selftext)
    test_data = pd.DataFrame(test)
    
    test_data = clean_df(test_data)
    input_features = test_data["title"] + " "+ test_data["body"]
    test_data = test_data.assign(input_features = input_features)

    random_model = open('linear-svm.pkl','rb')
    random = joblib.load(random_model)

    y_pred = random.predict(test_data['input_features'])
    return y_pred[0]
    
    return link
# --------------------------------------------------------------------------------


@app.route("/automated_testing", methods=['POST'])
def automated_testing():
    link = request.files['upload_file'].read().decode("utf-8")
    
    predicted_flare = predict(link)
    return {link:predicted_flare}

@app.route("/", methods=['POST', 'GET'])
def login():
    if(request.method == 'POST'):
        url = request.form['link']
        submission = reddit.submission(url=url)
        
        test = {"title":[],  "body":[]}
        test['title'].append(submission.title)
        test['body'].append(submission.selftext)
        test_data = pd.DataFrame(test)
        
        test_data = clean_df(test_data)
        input_features = test_data["title"] + " "+ test_data["body"]
        test_data = test_data.assign(input_features = input_features)

        random_model = open('linear-svm.pkl','rb')
        random = joblib.load(random_model)

        y_pred = random.predict(test_data['input_features'])
        final_resut = y_pred[0]

        return render_template("login.html", final=final_resut)
    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
