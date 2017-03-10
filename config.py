DSCOVR_BASE_URL = 'https://epic.gsfc.nasa.gov'
DSCOVR_API_PATH = '/api/enhanced/'
DSCOVR_IMG_PATH = '/archive/enhanced/{date}/{format}/{image}.{format}'

#GUARDIAN
GUARDIAN_APIKEY = ''
GUARDIAN_REQUEST = 'http://content.guardianapis.com/world?section=world&from-date={date}&to-date={date}&order-by=relevance&use-date=newspaper-edition&show-fields=trailText%2Cheadline%2CnewspaperPageNumber%2Cstandfirst&page-size=100&api-key={api_key}'

#TUMBLR
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_SECRET = ''
#TWITTER
#regenerate for each bot using https://github.com/hugovk/twitter-tools/blob/master/bot_authorise.py
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_OAUTH_TOKEN = ''
TWITTER_OAUTH_SECRET = ''

#SYSTEM
GIF_PATH = './earth.gif'


#DATE
DATE_LONGFORM = '%A, %B %d, %Y'
DATE_SHORTFORM = '%Y-%m-%d'
DATE_PATH = '%Y/%m/%d'

#METAPHORS
EARTH_METAPHORS = [
                    'on a pale blue dot suspended in a sunbeam',
                    'aboard Spaceship Earth',
                    'on the blue marble',
                    'aboard a mote of dust suspended in a sunbeam',
                    'on Earth'
                  ]
