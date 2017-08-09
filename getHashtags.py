from TwitterSearch import *
import matplotlib.pyplot as plt
import collections
import sys
import math


def FindHashHags(tweet):
    """
    This function takes the twittersearch output tweet,
    cleans up the text and the format, and returns
    the set of all hastags in the tweet
    """
    # First get the tweet text
    tweettxt = tweet['text'].encode('ascii', 'ignore')
    # People sometimes stack hashtags with no spacing
    # Add spacing before the hashtag symbol
    tweettxt = tweettxt.replace('#', ' #')
    # Clean all punctuation which sometimes
    # get cluttered in with the tag
    for punct in '.!",;:%<>/~`()[]{}?':
        tweettxt = tweettxt.replace(punct, '')
    # Split the tweet string into a list of words,
    # some of which will be hastagged
    # print tweettxt
    tweettxt = tweettxt.split()
    # Initiate list of hashtags
    hashtags = []
    # Loop over the words in the tweet
    for word in tweettxt:
        # Find words beginning with hashtag
        if word[0] == '#':
            # Lower-case the word
            hashtag = word.lower()
            # Correct the possisives
            hashtag = hashtag.split('\'')[0]
            # Get rid of the hastag symbol
            hashtag = hashtag.replace('#', '')
            # Make sure there is text left, append to list
            if len(hashtag) > 0:
                hashtags.append(hashtag)
    # Return clean list of hashtags
    return hashtags


def HashSearch(hashtag):
    """
    This is the master function which will perform the twitter
    search for the hashtag, and fin all other hashtags in those
    tweets. It will return a histogram of the frequency of other
    hashtags in tweets.
    """
    # Everything in lower case for semplicity
    hashtag = hashtag.lower()
    # CoTags will be the list of shared tags in tweets
    CoTags = []
    # Total number of tweets discovered
    ntweets = 0
    # This is the hashtag with no case or hash symbol
    basictag = hashtag.replace('#', '')
    # Load the twitter credentials
    credentials = dict()
    credential_file = file('credentials.txt')
    for line in file.readlines(credential_file):
        token = line.split('=')
        credentials[token[0]] = token[1].replace('\n', '')
    ts = TwitterSearch(
        consumer_key=credentials['APP_KEY'],
        consumer_secret=credentials['APP_SECRET'],
        access_token=credentials['OAUTH_TOKEN'],
        access_token_secret=credentials['OAUTH_TOKEN_SECRET'])
    # Create twitter search order for our hashtag in english
    # With setCount 1000 (1000 results)
    tso = TwitterSearchOrder()
    tso.set_keywords([hashtag])
    tso.set_language('en')
    tso.set_count(100)
    tso.set_include_entities(False)

    # Loop over tweets in results
    for tweet in ts.search_tweets_iterable(tso):
        # Use our cleaning/prasing function to get hashtags in tweet
        hashtags = FindHashHags(tweet)
        # Loop over hashtags
        for atag in hashtags:
            # Ignore our target hashtag!
            if basictag not in atag:
                # Add each hashtag to list of CoTags
                CoTags.append(atag)
        # Sto at 1000, that's enough
        if ntweets == 1000:
            break
        ntweets += 1

    # Get histogram of values
    taghisto = collections.Counter(CoTags)
    # Convert histogram to basic list like [['tag1', n1], ['tag2', n2]]
    taghisto = [list(x) for x in sorted(taghisto.items(), key=lambda x: -x[1])]
    # Let's normalize everything to percentage, and get uncertainties
    ntweets = float(ntweets)
    # Loop over histogram bars
    for ibin in range(len(taghisto)):
        # The poisson uncertainty is the square root of counts for each tag
        uncertainty = math.sqrt(taghisto[ibin][1])
        # Set counts to a percentage of total tweets in which tag occurs
        taghisto[ibin][1] = 100. * taghisto[ibin][1] / ntweets
        # Same for the uncertainty
        taghisto[ibin].append(100. * uncertainty / ntweets)
    # Return just the histogram information
    return taghisto


def DrawHisto(taghisto, atag):
    """
    This function is for drawing a png histogram of the 
    output of the HashSearch function.
    """
    # Let's get ideal number of bins. This is a cosmetic
    # choice. I choose all bins where the error bar is less
    # than 30% of the bin content. After all, there is little
    # insight from single-events. No more than 10.
    N = 0
    for t in taghisto:
        if t[2] < 0.3 * t[1]:
            N += 1
        if N == 10:
            break
    # Get the list of labels, bin content, and bin errors
    # for the first N tweets.
    labels = ['#' + taghisto[n][0] for n in range(N)]
    content = [taghisto[n][1] for n in range(N)]
    errors = [taghisto[n][2] for n in range(N)]

    # Horizontal bar plot with error bars
    plt.barh(range(N), content, xerr=errors, align='center', alpha=0.4)
    # Set the y labels as the hashtags
    plt.yticks(range(N), labels)
    # Set x label and title
    plt.xlabel('Percent shared hashtags')
    plt.title('Shared hashtags for #' + mytag)
    # Cosmetic choice to adjust x axis
    plt.xlim(0.0, max(content) * 1.2)
    # Labels can be big, auto-fix the layout
    plt.tight_layout()
    # Save to png
    plt.savefig(atag + '.png')

# This is the hashtag (system argument)
mytag = sys.argv[1]
# Now get raw data for co-tags of the hashtag "mytag"
myhisto = HashSearch('#' + mytag)
# Draw the histogram
DrawHisto(myhisto, mytag)
