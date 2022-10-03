from googleapiclient.discovery import build
import json

VIDEO_LINK_FRONT = 'youtube.com/watch?v='
CHANNEL_LINK_FRONT = 'youtube.com/channel/'
TOPIC_CATEGORIES_FRONT = 'en.wikipedia.org/wiki/'
VIDEO_THUMBNAIL_FRONT = 'i.ytimg.com/vi/'  # f'i.ytimg.com/vi/{video_id}/{size}'
PLAYLIST_FRONT = 'youtube.com/playlist?list='
CHANNEL_THUMBNAIL_FRONT = 'yt3.ggpht.com/' # f'yt3.ggpht.com/{channel_thumbnail_id}{size}'
VIDEO_PART = 'contentDetails, id, liveStreamingDetails, snippet, topicDetails'  # , statistics, status, localizations, player, recordingDetails'
CHANNEL_PART = 'id, snippet'  #, brandingSettings, contentDetails, contentOwnerDetails, localizations, statistics, status, topicDetails'

category = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '18': 'Short Movies',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '21': 'Videoblogging',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Technology',
    '29': 'Nonprofits & Activism',
    '30': 'Movies',
    '31': 'Anime/Animation',
    '32': 'Action/Adventure',
    '33': 'Classics',
    '34': 'Comedy',
    '35': 'Documentary',
    '36': 'Drama',
    '37': 'Family',
    '38': 'Foreign',
    '39': 'Horror',
    '40': 'Sci-Fi/Fantasy',
    '41': 'Thriller',
    '42': 'Shorts',
    '43': 'Shows',
    '44': 'Trailers'}

video_thumb_size = {'default': '/default.jpg',
                    'medium': '/mqdefault.jpg',
                    'high': '/hqdefault.jpg',
                    'standard': '/sddefault.jpg',
                    'maxres': '/maxresdefault.jpg'}

channel_thumb_size = {'default': '=s88-c-k-c0x00ffffff-no-rj',
                      'medium': '=s240-c-k-c0x00ffffff-no-rj',
                      'high': '=s800-c-k-c0x00ffffff-no-rj'}


def video_to_json(fifty_id, dev_key, file_name=None):
    try:
        youtube = build('youtube', 'v3', developerKey=dev_key)
        request = youtube.videos().list(part=VIDEO_PART, id=fifty_id)
        response = request.execute()

        if file_name:
            with open(file_name, 'a') as f:
                json.dump(response, f)
                f.write('\n')

        return response

    except Exception as e:
        print(e)
        return False


def channel_to_json(fifty_id, dev_key, file_name=None):
    youtube = build('youtube', 'v3', developerKey=dev_key)
    request = youtube.channels().list(part=CHANNEL_PART, id=fifty_id)
    response = request.execute()

    if file_name:
        with open(file_name, 'a') as f:
            json.dump(response, f)
            f.write('\n')

    return response
