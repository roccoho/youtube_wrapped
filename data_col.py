from bs4 import BeautifulSoup
import pandas as pd
import isodate
import json
import datetime
import youtube_api
import os
import pytz

WATCH_HIST_CSV = 'watch_hist.csv'
VIDEO_RESPONSE_JSON = 'video_response.json'
CHANNEL_RESPONSE_JSON = 'channel_response.json'
VIDEO_INFO_CSV = 'video_info.csv'
CHANNEL_INFO_CSV = 'channel_info.csv'
YEAR = 2021


# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', 1000)
# pd.set_option('display.max_colwidth', None)
# pd.set_option('display.max_rows', None)


def parse_time(time):
    time = time[:19]  # dropped milliseconds and UTC timezone: inconsistent format for milliseconds
    time = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")

    utc_tz = pytz.timezone("UTC")
    timezone = datetime.datetime.now().astimezone().tzinfo  # get local timezone

    time = time.replace(tzinfo=utc_tz)
    time = time.astimezone(timezone).replace(tzinfo=None)
    return time


def watch_hist_json_to_csv(path):
    try:
        f = open(path, encoding='utf-8')
        data = json.load(f)
        df = pd.json_normalize(data)

        if 'details' in df.columns:  # remove ads but sometimes this column doesn't exist????
            df = df[df['details'].isna()]

        df = df[df['subtitles'].notna()].reset_index(drop=True)  # unavailable videos
        df[['channelName','channelId']] = pd.json_normalize(pd.json_normalize(df['subtitles'])[0])  # because of list of dictionary in subtitles column
        df['channelId'] = df['channelId'].str[32:]  # only id for api calls
        df['titleUrl'] = df['titleUrl'].str[32:]
        df['title'] = df['title'].str[8:]  # remove "Watched" in title
        df = df[['title', 'titleUrl', 'time', 'channelName', 'channelId']]
        df['time'] = df['time'].apply(parse_time)
        # df = df[df['time'].dt.year == YEAR]
        df = df.rename({'titleUrl': 'videoId', 'time': 'date_time'}, axis=1)
        df.to_csv(WATCH_HIST_CSV, encoding='utf-8-sig', index=False)

        string_dates = df['date_time'].dt.strftime('%Y-%m-%d')
        earliest = string_dates.tail(1).item()
        latest = string_dates.head(1).item()
        return [earliest, latest]

    except Exception as e:
        print(e)
        return None


def filter_watch_hist_date(earliest, latest):
    try:
        df = pd.read_csv(WATCH_HIST_CSV)
        latest = datetime.datetime.strptime(latest, '%Y-%m-%d') + datetime.timedelta(days=1)  # needs an extra day to be inclusive
        latest = latest.strftime('%Y-%m-%d')
        df = df[(df['date_time']>=earliest) & (df['date_time']<=latest)]
        df.to_csv(WATCH_HIST_CSV, encoding='utf-8-sig', index=False)
        print(len(df))
        return True

    except Exception as e:
        print(e)
        return False


def html_to_csv(path): # watch_hist html to csv (unused as only json is accepted, but html dates further back?)
    soup = BeautifulSoup(open(path, encoding='utf-8'), 'lxml')  # html.parser
    a = soup.find_all('div', attrs={'class':'content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1'})
    watched = {'videoId': [], 'title': [], 'channelId': [], 'channelName': [], 'date_time': []}

    for vid in a:
        link = vid.find_all('a', href=True)
        if link:
            final_line = vid.findAll('br')
            date_time = final_line[len(final_line)-1].nextSibling[:-4]  # country/timezone dropped: already in naive local time
            date_time = date_time.replace('Sept', 'Sep') # reformat sept to sep
            date_time = datetime.datetime.strptime(date_time, '%d %b %Y, %H:%M:%S')  # seems inconsistent for different files '%b %d, %Y, %I:%M:%S %p')#
            if date_time.year == YEAR:
                watched['date_time'].append(date_time)

                video_link = link[0]['href'][32:]  # only get unique vid id
                watched['videoId'].append(video_link)
                title = link[0].contents[0]
                watched['title'].append(title)
                if len(link) > 1:  # has channel link (not ads)
                    channel_link = link[1]['href'][32:]  # only get unique chan id
                    watched['channelId'].append(channel_link)
                    channel_name = link[1].contents[0]
                    watched['channelName'].append(channel_name)
                else:
                    watched['channelId'].append(None)
                    watched['channelName'].append(None)

    df = pd.DataFrame.from_dict(watched)
    print(len(df))
    print(df)
    df.to_csv(WATCH_HIST_CSV, encoding='utf-8-sig')


def get_append_string(string_list, step=50):
    combined_string_list = []
    for i in range(0, len(string_list), step):
        combined_string_list.append(','.join(string_list[i:i+step]))

    return combined_string_list


def safe_get(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


def video_json_to_csv(response):  # there has to be a better way
    vid_header = ['videoId', 'duration', 'vid_default_thumb', 'vid_medium_thumb', 'vid_high_thumb',
                  'vid_standard_thumb', 'vid_maxres_thumb', 'topicCategories', 'liveStreamingDetails',
                  'categoryId', 'category', 'tags']
                  # 'etag', 'channelTitle', 'title', 'description', 'channelId', 'publishedAt',
                  # 'liveBroadcastContent', 'dimension', 'definition', 'caption',
                  # 'licensedContent', 'contentRating', 'projection',
                  # 'uploadStatus', 'privacyStatus', 'license', 'embeddable', 'publicStatsViewable', 'madeForKids',
                  # 'viewCount', 'likeCount', 'favoriteCount', 'commentCount',
                  # 'embedHtml', 'recordingDetails']

    vid = {i: [] for i in vid_header}

    # response = []
    # with open(VIDEO_RESPONSE_JSON) as f:
    #     for line in f:
    #         response.append(json.loads(line))  # append to dictionary)

    for j in response:
        for i in j['items']:
            # vid['etag'].append(safe_get(i, 'etag'))
            vid['videoId'].append(safe_get(i, 'id'))

            # publishedAt = safe_get(i, 'snippet', 'publishedAt')
            # publishedAt = datetime.datetime.strptime(publishedAt, '%Y-%m-%dT%H:%M:%SZ')
            # vid['publishedAt'].append(publishedAt)
            # vid['channelId'].append(safe_get(i, 'snippet', 'channelId'))
            # vid['title'].append(safe_get(i, 'snippet', 'title'))
            # vid['description'].append(safe_get(i, 'snippet', 'description'))
            # vid['channelTitle'].append(safe_get(i, 'snippet', 'channelTitle'))
            # vid['liveBroadcastContent'].append(safe_get(i, 'snippet', 'liveBroadcastContent'))
            # if(safe_get(i, 'snippet', 'liveBroadcastContent')!='none'):
            #     print(safe_get(i, 'snippet', 'liveBroadcastContent'))

            vid['vid_default_thumb'].append(safe_get(i, 'snippet', 'thumbnails', 'default', 'url'))
            vid['vid_medium_thumb'].append(safe_get(i, 'snippet', 'thumbnails', 'medium', 'url'))
            vid['vid_high_thumb'].append(safe_get(i, 'snippet', 'thumbnails', 'high', 'url'))
            vid['vid_standard_thumb'].append(safe_get(i, 'snippet', 'thumbnails', 'standard', 'url'))
            vid['vid_maxres_thumb'].append(safe_get(i, 'snippet', 'thumbnails', 'maxres', 'url'))

            # for qual in youtube_api.video_thumb_size.keys():
            #     if safe_get(i, 'snippet', 'thumbnails', qual):
            #         width = str(safe_get(i, 'snippet', 'thumbnails', qual, 'width'))
            #         height = str(safe_get(i, 'snippet', 'thumbnails', qual, 'height'))
            #         vid[f'{qual}_thumb'].append(f'{width}x{height}')
            #     else:
            #         vid[f'{qual}_thumb'].append(None)

            vid['tags'].append(safe_get(i, 'snippet', 'tags'))

            category_id = safe_get(i, 'snippet', 'categoryId')
            vid['categoryId'].append(category_id)
            vid['category'].append(youtube_api.category[category_id])

            # length = isodate.parse_duration(content_details['duration'])
            vid['duration'].append(safe_get(i, 'contentDetails', 'duration'))
            # vid['dimension'].append(safe_get(i, 'contentDetails', 'dimension'))
            # vid['definition'].append(safe_get(i, 'contentDetails', 'definition'))
            # vid['caption'].append(safe_get(i, 'contentDetails', 'caption'))
            # vid['licensedContent'].append(safe_get(i, 'contentDetails', 'licensedContent'))
            # vid['projection'].append(safe_get(i, 'contentDetails', 'projection'))
            # vid['contentRating'].append(safe_get(i, 'contentDetails', 'contentRating'))

            # status
            # vid['uploadStatus'].append(safe_get(i, 'status', 'uploadStatus'))
            # vid['privacyStatus'].append(safe_get(i, 'status', 'privacyStatus'))
            # vid['license'].append(safe_get(i, 'status', 'license'))
            # vid['embeddable'].append(safe_get(i, 'status', 'embeddable'))
            # vid['publicStatsViewable'].append(safe_get(i, 'status', 'publicStatsViewable'))
            # vid['madeForKids'].append(safe_get(i, 'status', 'madeForKids'))

            # statistics
            # vid['likeCount'].append(safe_get(i, 'statistics', 'likeCount'))
            # vid['viewCount'].append(safe_get(i, 'statistics', 'viewCount'))
            # vid['favoriteCount'].append(safe_get(i, 'statistics', 'favoriteCount'))
            # vid['commentCount'].append(safe_get(i, 'statistics', 'commentCount'))

            # player
            # vid['embedHtml'].append(safe_get(i, 'player', 'embedHtml'))
            vid['topicCategories'].append(safe_get(i, 'topicDetails', 'topicCategories'))
            # vid['recordingDetails'].append(safe_get(i, 'recordingDetails'))
            vid['liveStreamingDetails'].append(safe_get(i, 'liveStreamingDetails'))

    df = pd.DataFrame.from_dict(vid)
    df.to_csv(VIDEO_INFO_CSV, encoding='utf-8-sig')


def channel_json_to_csv(response):
    channel_header = ['channelId', 'title', 'chan_default_thumb', 'chan_medium_thumb', 'chan_high_thumb']
                      # 'localized_title', 'description', 'localized_description',
                      # 'etag', 'publishedAt', 'viewCount', 'subscriberCount', 'hiddenSubscriberCount',
                      # 'videoCount', 'topicIds', 'topicCategories', 'privacyStatus', 'isLinked', 'longUploadsStatus',
                      # 'brandingTitle', 'unsubscribedTrailer', 'bannerExternalUrl']

    channel = {i: [] for i in channel_header}

    # response = []
    # with open(CHANNEL_RESPONSE_JSON) as f:
    #     for line in f:
    #         response.append(json.loads(line))  # append to dictionary

    for j in response:
        for i in j['items']:
            # channel['etag'].append(safe_get(i, 'etag'))
            channel['channelId'].append(safe_get(i, 'id'))

            # channel['publishedAt'].append(safe_get(i, 'snippet', 'publishedAt'))
            channel['title'].append(safe_get(i, 'snippet', 'title'))
            # channel['localized_title'].append(safe_get(i, 'snippet', 'localized', 'title'))
            # channel['description'].append(safe_get(i, 'snippet', 'description'))
            # channel['localized_description'].append(safe_get(i, 'snippet', 'localized', 'description'))

            channel['chan_default_thumb'].append(safe_get(i, 'snippet', 'thumbnails', 'default', 'url'))
            channel['chan_medium_thumb'].append(safe_get(i, 'snippet', 'thumbnails', 'medium', 'url'))
            channel['chan_high_thumb'].append(safe_get(i, 'snippet', 'thumbnails', 'high', 'url'))
            # if thumbnail:
            #     channel['thumbnail'].append(thumbnail[22:-26])
            # else:
            #     channel['thumbnail'].append(None)
            # for qual in youtube_api.channel_thumb_size.keys():
            #     if safe_get(i, 'snippet', 'thumbnails', qual):
            #         width = str(safe_get(i, 'snippet', 'thumbnails', qual, 'width'))
            #         height = str(safe_get(i, 'snippet', 'thumbnails', qual, 'height'))
            #         channel[f'{qual}_thumb'].append(f'{width}x{height}')
            #     else:
            #         channel[f'{qual}_thumb'].append(None)

            # channel['viewCount'].append(safe_get(i, 'statistics', 'viewCount'))
            # channel['subscriberCount'].append(safe_get(i, 'statistics', 'subscriberCount'))
            # channel['hiddenSubscriberCount'].append(safe_get(i, 'statistics', 'hiddenSubscriberCount'))
            # channel['videoCount'].append(safe_get(i, 'statistics', 'videoCount'))

            # channel['topicIds'].append(safe_get(i, 'topicDetails', 'topicIds'))
            # channel['topicCategories'].append(safe_get(i, 'topicDetails', 'topicCategories'))

            # channel['privacyStatus'].append(safe_get(i, 'status', 'privacyStatus'))
            # channel['isLinked'].append(safe_get(i, 'status', 'isLinked'))
            # channel['longUploadsStatus'].append(safe_get(i, 'status', 'longUploadsStatus'))

            # channel['brandingTitle'].append(safe_get(i, 'brandingSettings', 'channel', 'title'))
            # channel['unsubscribedTrailer'].append(safe_get(i, 'brandingSettings', 'channel', 'unsubscribedTrailer'))
            # channel['bannerExternalUrl'].append(safe_get(i, 'brandingSettings', 'image', 'bannerExternalUrl'))

    df = pd.DataFrame.from_dict(channel)
    df.to_csv(CHANNEL_INFO_CSV, encoding='utf-8-sig')


def parse_duration(a):
    return isodate.parse_duration(a)


def delete_file_if_exist(path):
    if os.path.exists(path): os.remove(path)


def get_info(dev_key):
    try:
        watch_hist = pd.read_csv(WATCH_HIST_CSV)
        watch_hist = watch_hist.drop_duplicates(subset=['videoId'], ignore_index=True)
        watch_hist = watch_hist[watch_hist['videoId'].notna()]
        watch_hist = watch_hist[watch_hist['channelId'].notna()]
        print(len(watch_hist))

        string_list = get_append_string(watch_hist['videoId'].to_list())
        print(len(string_list))
        # delete_file_if_exist(VIDEO_RESPONSE_JSON)
        response_list = []
        for i in string_list:
            response_list.append(youtube_api.video_to_json(i, dev_key))
            # youtube_api.video_to_json(i, dev_key, VIDEO_RESPONSE_JSON)
        return response_list

    except Exception as e:
        print(e)



