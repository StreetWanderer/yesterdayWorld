from datetime import date, timedelta
import json, requests
import config

def getImagesInfo(date):
    #Get the list of images that DSCOVR took at the given date
    path = config.DSCOVR_API_PATH.format(date=date)
    path = config.DSCOVR_BASE_URL + path


    imagesList = requests.get(config.DSCOVR_BASE_URL + config.DSCOVR_API_PATH, params={'date':date})
    jsonImages = json.loads(imagesList.text)

    parsedData = []
    for img in jsonImages:
        parsedImages.append(img['image'])

    return parsedData;

def downloadImages(imageNames, format):
    gifBytes = []
    for img in imageNames:
        path = config.DSCOVR_BASE_URL + config.DSCOVR_IMG_PATH.format(format=format, image=img)
        imgBytes = requests.get(path)
        gifBytes.append(imgBytes.content)

    return gifBytes




yesterday = date.today() - timedelta(1)
imageData = getImagesInfo(yesterday.strftime('%Y%m%d'))
gifBytesArray = downloadImages(imageData, 'png')
#transform gifBytesArray to .gif
#get yesterday headline from TheGuardian
#combine the gif and headlines to upload to Tumblr
