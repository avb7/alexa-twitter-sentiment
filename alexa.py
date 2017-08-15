#For Alexa skill implementation
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

#For Twitter sentiment analysis
import tweepy
from textblob import TextBlob
import re

#Authenticate Twitter
consumer_key = 'NxbbnbRHnlLkuBZhBrChfkcJr'
consumer_secret = 'AbxZoeCNGbJAqZfxizTN3Cxei8kfovGjoaujG3tHmsZl6UqT7m'
access_token = '247244419-q3JnRzCO24LiHPCrQGmOvRumFZRnK72zvNHuwyKf'
access_secret = 'pxCdTqDpxCxJr5PvEZkZtNCOhEnpiFyZrNzsApVDWpdDY'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#Initialize flask and flask-ask
app = Flask(__name__)
ask = Ask(app, "/")

def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w +:\ / \ / \S +)", " ", tweet).split())

def get_sentiment(topic):
    '''
    Function to scrape twitter
    :return: sentiment string that is passed as an alexa statement 
    '''
    # Code for sentiment analysis on twitter
    # Collect tweets for the asked topic
    tweet_count = 200
    public_tweets = api.search(topic, count=tweet_count)

    number_of_positives = 0
    number_of_negatives = 0
    number_of_neutrals = 0

    for tweet in public_tweets:
        analysis = TextBlob(clean_tweet(tweet.text))
        if (analysis.sentiment.polarity > 0):
            number_of_positives = number_of_positives + 1
        elif (analysis.sentiment.polarity < 0):
            number_of_negatives = number_of_negatives + 1
        else:
            number_of_neutrals = number_of_neutrals + 1

    positive_percent = (number_of_positives * 100) / tweet_count
    negative_percent = (number_of_negatives * 100) / tweet_count

    # Decide the general opinion
    opinion = 'positive'
    if (positive_percent < negative_percent):
        opinion = 'negative'
    elif (positive_percent == negative_percent):
        opinion = 'neutral'

    #convert all variables to string
    positive_str = str(positive_percent)
    negative_str = str(negative_percent)

    # Return the statement with the sentiment msg
    sentiment_msg = render_template('sentiment_review', opinion=opinion, topic=topic,
                                    positive_percent=positive_str, negative_percent=negative_str)

    return sentiment_msg

@ask.launch
def start_skill():
    welcome = render_template('welcome')
    reprompt = render_template('reprompt')
    return question(welcome)\
        .reprompt(reprompt)

@ask.intent("ShareSentimentIntent")
def share_sentiment(topic):
    if (topic is None):
        reprompt_topic = render_template("reprompt_topic")
        return question(reprompt_topic)
    else:
        sentiment_msg = str(get_sentiment(topic))
        return statement(sentiment_msg)


if __name__ == '__main__':
    app.run(debug=True)
