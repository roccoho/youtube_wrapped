import pandas as pd
from collections import Counter
import calendar
import glob
import numpy as np
import youtube_api
import data_col

AVG_WATCHTIME = 0.55  #https://uhurunetwork.com/the-50-rule-for-youtube/
FOLDER = './stats/'

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)


def save_to_csv(df, name, encoding='utf-8'):
    df.to_csv(f'{FOLDER}{name}.csv', encoding=encoding)


def top_tags(watch, num=20, to_print=False, to_save=False):
    watch = watch.dropna(subset=['tags'])
    string = watch['tags'].str.cat(sep=',')
    string = string.split(',')
    counter = Counter(string)
    ranking = counter.most_common(num)
    ranking_dict = {'tag':[], 'count':[]}
    for i in ranking:
        ranking_dict['tag'].append(i[0].strip("' "))
        ranking_dict['count'].append(i[1])
    ranking_df = pd.DataFrame.from_dict(ranking_dict)
    max_count = ranking_df['count'].max().item()
    ranking_df['size'] = (ranking_df['count']/max_count)*100
    temp_link_tags = ranking_df['tag'].str.replace(' ', '+', regex=True)
    ranking_df['link'] = "https://www.youtube.com/results?search_query=" + temp_link_tags

    if to_print:
        print(ranking_df.to_string())
    # if to_disp:
    #     plt.pie(ranking_df['count'], autopct='%1.1f%%', shadow=True, labels=ranking_df['tag'])
    #     plt.show()
    if to_save:
        save_to_csv(ranking_df, 'tags_hist')
    return ranking


def playlist_views(watch, to_save=False):
    playlists = glob.glob("takeout-20220328T180337Z-001 html/Takeout/YouTube and YouTube Music/playlists/*.csv")
    playlist_dict = {i: [] for i in ['playlist_id', 'playlist_name', 'playlist_views']}
    for val in playlists:
        playlist = pd.read_csv(val)
        playlist_dict['playlist_name'].append(playlist['Title'][0])
        playlist_dict['playlist_id'].append(playlist.iloc[0, 0])
        playlist.columns = playlist.iloc[1]  # get header row
        playlist = playlist[2:]  # get all rows after header
        playlist = playlist.iloc[:, 0:2]  # get first 2 columns
        playlist = watch[watch['videoId'].isin(playlist['Video ID'])]
        playlist_dict['playlist_views'].append(len(playlist))

    playlist_df = pd.DataFrame.from_dict(playlist_dict)
    playlist_df = playlist_df.set_index('playlist_id')
    playlist_df = playlist_df.sort_values(by='playlist_views', ascending=False)
    if to_save:
        save_to_csv(playlist_df, 'playlist_views')

    return playlist_df


def group_data(watch, groupby, num):
    ranking = watch.groupby(groupby).size().reset_index(name='count')
    ranking = ranking.sort_values(ascending=False, ignore_index=False, by='count')

    if num:
        ranking = ranking[:num]
    return ranking


def max_thumb(ranking, series, ascending=True):
    if ascending:
        series.reverse()

    for i, val in enumerate(series):
        if ranking[val] is not None:
            return ranking[val]


def fetch_channel_info(id_list, dev_key):
    string_list = data_col.get_append_string(id_list)
    # data_col.delete_file_if_exist(data_col.CHANNEL_RESPONSE_JSON)
    response = []
    for i in string_list:
        # youtube_api.channel_to_json(i, dev_key, data_col.CHANNEL_RESPONSE_JSON)
        response.append(youtube_api.channel_to_json(i, dev_key))

    data_col.channel_json_to_csv(response)
    channel_info = pd.read_csv(data_col.CHANNEL_INFO_CSV)
    channel_info = channel_info.drop_duplicates(subset=['channelId'], ignore_index=True)
    channel_info = channel_info[['channelId', 'chan_default_thumb', 'chan_medium_thumb', 'chan_high_thumb']]

    return channel_info


def top_video(watch, num=None, to_print=False, to_save=False, to_disp=False):
    ids = 'videoId'
    ranking = group_data(watch, ['title', ids, 'channelId', 'channelName', 'vid_default_thumb', 'vid_medium_thumb', 'vid_high_thumb', 'vid_standard_thumb', 'vid_maxres_thumb'], num)
    ranking['video_link'] = 'https://' + youtube_api.VIDEO_LINK_FRONT + ranking[ids].astype(str)
    ranking['chan_link'] = 'https://' + youtube_api.CHANNEL_LINK_FRONT + ranking['channelId'].astype(str)
    ranking['embed'] = 'https://www.youtube.com/embed/' + ranking[ids].astype(str)
    ranking['thumbnail'] = max_thumb(ranking, ['vid_default_thumb', 'vid_medium_thumb', 'vid_high_thumb', 'vid_standard_thumb', 'vid_maxres_thumb'])
    if to_save:
        to_save = 'video'

    to_do(ranking, to_save=to_save, to_print=to_print, to_disp=to_disp)
    return ranking


def top_channel(watch, dev_key, num=None, to_print=False, to_save=False, to_disp=False):
    ids = 'channelId'
    ranking = group_data(watch, ['channelName', ids], num)
    channel_info = fetch_channel_info(ranking[ids].to_list(), dev_key)
    ranking = ranking.merge(channel_info, on=ids, how='inner')
    ranking = remove_duplicate_columns(ranking)
    ranking['link'] = 'https://' + youtube_api.CHANNEL_LINK_FRONT + ranking[ids].astype(str)
    ranking['thumbnail'] = max_thumb(ranking, ['chan_default_thumb', 'chan_medium_thumb', 'chan_high_thumb'])
    if to_save:
        to_save = 'channel'

    to_do(ranking, to_save=to_save, to_print=to_print, to_disp=to_disp)
    return ranking


def top_category(watch, num=None, to_print=False, to_save=False, to_disp=False):
    data_type = 'category'
    ids = 'channelId'
    ranking = group_data(watch, [data_type, ids], num)

    if to_save:
        to_save = 'category'

    to_do(ranking, to_save=to_save, to_print=to_print, to_disp=to_disp)
    return ranking


def to_do(ranking, to_print, to_save, to_disp):
    if to_print:
        print(ranking)
    # if to_disp:
    #     plt.pie(ranking['count'], autopct='%1.1f%%', shadow=True, labels=ranking[data_type])
    #     plt.show()
    if to_save:
        save_to_csv(ranking, f'{to_save}_hist')


def week_hour_graph(watch, to_print=False, to_save=False):
    week_index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    watch['day'] = watch['date_time'].dt.day_name()
    watch['hour'] = watch['date_time'].dt.hour
    watch['duration'] = (watch['duration'] / 60).round(decimals=2)  # in minutes
    watch_count = watch.groupby(['hour', 'day']).size().reset_index(name='count')
    watch_sum = watch.groupby(['hour', 'day'])['duration'].sum().reset_index(name='duration')
    watch = pd.merge(watch_sum, watch_count, on=['day', 'hour'])

    new_rows = {'hour': [], 'day': []}
    for i in range(24):  # add missing rows
        temp_watch = watch[watch['hour'] == i]
        if temp_watch.empty:
            temp_day = []
        else:
            temp_day = temp_watch['day'].to_list()

        if len(temp_day) < 7 :
            for day in week_index:
                if day not in temp_day:
                    new_rows['day'].append(day)
                    new_rows['hour'].append(i)

    new_rows['count'] = [0] * len(new_rows['hour'])
    new_rows['duration'] = [0] * len(new_rows['hour'])
    new_watch = pd.DataFrame.from_dict(new_rows)
    new_watch = pd.concat([new_watch, watch], axis=0)

    count_percent = normalize(new_watch['count'])
    new_watch['video_color'] = 'rgba(189, 105, 242, ' + count_percent.astype(str) + ')'
    new_watch['day_short'] = new_watch['day'].str[:3]
    new_watch['x_axis'] = new_watch['hour'].astype('str')
    new_watch['x_axis'] = new_watch['x_axis'] + ':00'
    new_watch['x_axis'] = new_watch['x_axis'].apply(hour_format)

    duration_percent = normalize(new_watch['duration'])
    new_watch['duration_color'] = 'rgba(64, 181, 217, ' + duration_percent.astype(str) + ')'

    new_watch['day'] = pd.Categorical(new_watch['day'], categories=week_index, ordered=True)
    new_watch = new_watch.sort_values(['hour','day'], ascending=[True, True])

    if to_save:
        save_to_csv(new_watch, 'week_hour_hist')
    if to_print:
        print(new_watch)
    return new_watch


def normalize(col, decimals=2):
    max_val = col.max()
    min_val = col.min()
    return ((col-min_val)/(max_val-min_val)).round(decimals=decimals) #normalized=(df-df.mean())/df.std()


def month_graph(watch, to_print=False, to_save=False):
    unique_val = watch['month'].unique().tolist()
    new_month = []
    for i in range(12, 1, 1):
        if i not in unique_val:
            new_month.append(i)
    new_rows = {'month': new_month, 'duration': [0] * len(new_month)}
    temp_watch = pd.DataFrame.from_dict(new_rows)
    watch = pd.concat([watch, temp_watch])
    watch['month'] = watch['month'].astype('int')

    month_duration = watch.groupby(['month'])['duration'].sum().reset_index()
    month_count = watch.groupby(['month']).size().reset_index(name='count')
    month_merged = pd.merge(month_count, month_duration)  # pd.concat([month_duration, month_count], join='inner', axis=1, ignore_index=True)
    month_merged['x_axis'] = month_merged['month'].apply(lambda x: calendar.month_abbr[x])
    month_merged['duration'] = convert_seconds_to(month_merged['duration'], 'm', 2)

    if to_save:
        save_to_csv(month_merged, 'month_hist')
    if to_print:
        print(month_merged)
    return month_merged


def hour_graph(watch, to_print=False, to_save=False):
    watch['hour'] = watch['date_time'].dt.hour
    unique_val = watch['hour'].unique().tolist()
    new_hours = []
    for i in range(24):
        if i not in unique_val:
            new_hours.append(i)
    new_rows = {'hour': new_hours, 'duration': [0] * len(new_hours)}
    temp_watch = pd.DataFrame.from_dict(new_rows)
    watch = pd.concat([watch, temp_watch])

    hour_duration = watch.groupby(['hour'])['duration'].sum().reset_index()
    hour_count = watch.groupby(['hour']).size().reset_index(name='count')
    hour_merged = pd.merge(hour_count, hour_duration)  # pd.concat([month_duration, month_count], join='inner', axis=1, ignore_index=True)
    hour_merged['duration'] = convert_seconds_to(hour_merged['duration'], 'm', 2)
    hour_merged['hour'] = hour_merged['hour'].astype('int').astype('str')
    hour_merged['x_axis'] = hour_merged['hour'] + ':00'
    hour_merged['x_axis'] = hour_merged['x_axis'].apply(hour_format)

    if to_print:
        print(hour_merged)
    if to_save:
        save_to_csv(hour_merged, 'hour_hist')

    return hour_merged


def day_graph(watch, to_print=False, to_save=False):
    watch['date'] = watch['date_time'].dt.strftime('%Y-%m-%d')
    day_duration = watch.groupby(['date'])['duration'].sum().reset_index()
    day_count = watch.groupby(['date']).size().reset_index(name='count')
    day_merged = pd.merge(day_count, day_duration)  # pd.concat([month_duration, month_count], join='inner', axis=1, ignore_index=True)
    day_merged['duration'] = convert_seconds_to(day_merged['duration'], 'm', 2)
    day_merged['x_axis'] = day_merged['date']

    if to_save:
        save_to_csv(day_merged, 'day_hist')
    if to_print:
        print(day_merged)
    # if to_disp:
    #     line_chart(day_merged['date'], day_merged['duration'], day_merged['count'], '2021 Daily statistics', '2021', 'Duration watched (minutes)', 'Total videos watched', None)
    return day_merged


def hour_format(hour):
    if len(hour) < 5:
        hour = '0' + hour
    return hour

def week_graph(watch, to_print=False, to_save=False):
    watch['day'] = watch['date_time'].dt.day_name()
    week_duration = watch.groupby(['day'])['duration'].sum().reset_index()
    week_count = watch.groupby(['day']).size().reset_index(name='count')
    week_merged = pd.merge(week_count, week_duration)  # pd.concat([month_duration, month_count], join='inner', axis=1, ignore_index=True)
    week_merged['duration'] = convert_seconds_to(week_duration['duration'], 'm', 2)
    week_index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    week_merged['day'] = pd.Categorical(week_merged['day'], categories=week_index, ordered=True)
    week_merged = week_merged.sort_values('day')
    week_merged['x_axis'] = week_merged['day']

    if to_save:
        save_to_csv(week_merged, 'week_hist')
    if to_print:
        print(week_merged)
    # if to_disp:
    #     line_chart(day_merged['date'], day_merged['duration'], day_merged['count'], '2021 Daily statistics', '2021', 'Duration watched (minutes)', 'Total videos watched', None)
    return week_merged


def convert_seconds_to(column, time, precision=None):
    time = time.lower()
    if time == 'h':
        column = (column / 60 * 60)
    elif time == 'm':
        column = (column / 60)

    if precision:
        column = column.round(precision)

    return column


def number_of_days(year):
    return 366 if calendar.isleap(year) else 365


def avg_stats(watch_hist_ori, watch_hist, to_save=False, to_print=False):
    days = number_of_days(2021)
    total_vids = len(watch_hist_ori)
    total_vids_out = "{:,}".format(total_vids)
    total_active_vids = len(watch_hist)
    total_duration = watch_hist['duration'].sum()
    total_duration_out = "{:,}".format(int(total_duration/60))  # in minutes
    vids_per_day = int(total_vids / days)
    optimal_length = total_duration / total_active_vids
    optimal_length_out = str(int(optimal_length/60)) + ":" + str(int(optimal_length % 60))
    watchtime_per_day = int((total_duration / days) / 60)

    if to_print:
        print(total_vids_out)
        print(total_duration_out)
        print(vids_per_day)
        print(optimal_length_out)
        print(watchtime_per_day)

    if to_save:
        stats_dict = {'stats': ['total_vids', 'total_duration', 'avg_vids_per_day', 'avg_video_length', 'watchtime_per_day'],
                      'value': [total_vids_out, total_duration_out, vids_per_day, optimal_length_out, watchtime_per_day]}
        stats_df = pd.DataFrame.from_dict(stats_dict)
        save_to_csv(stats_df, 'stats')


def min_max_date(watch):
#     watch['publishedAt'] = pd.to_datetime(watch['publishedAt']).dt.tz_convert(None)
#     print(f'oldest vid watched:{min(watch["publishedAt"])}')
#     print(f'latest vid watched:{max(watch["publishedAt"])}')

    temp_dt = min(watch["date_time"])
    temp_watch = watch[watch['date_time'] == temp_dt]
    print(f"first vid watched in 2021: {temp_watch['title_x']}")

    temp_dt = max(watch["date_time"])
    temp_watch = watch[watch['date_time'] == temp_dt]
    print(f"last vid watched in 2021: {temp_watch['title_x']}")


def remove_duplicate_columns(df):
    for col in df:
        if col.endswith('_x'):
            df = df.rename(columns={col: col.rstrip('_x')})
        elif col.endswith('_y'):
            to_drop = [col for col in df if col.endswith('_y')]
            df = df.drop(to_drop, axis=1)
    return df


def date_range(watch, col_name, start_date, end_date):
    mask = (watch[col_name] >= start_date) & (watch[col_name] < end_date)
    return watch.loc[mask]


def merge_df(watch_hist, video_info):
    watch_hist = watch_hist.merge(video_info, on='videoId', how='inner')
    watch_hist = remove_duplicate_columns(watch_hist)
    watch_hist = watch_hist[watch_hist['liveStreamingDetails'].isna()]  # drop livestream videos: skews results
    watch_hist['date_time'] = pd.to_datetime(watch_hist['date_time'])
    watch_hist['month'] = watch_hist['date_time'].dt.month
    watch_hist['duration'] = pd.to_timedelta(watch_hist['duration'], errors='raise') * AVG_WATCHTIME / (np.timedelta64(1, 's')) # in seconds
    watch_hist['duration'] = watch_hist['duration'].astype('float64')
    return watch_hist


def manipulate_data(dev_key):
    try:
        video_info = pd.read_csv(data_col.VIDEO_INFO_CSV)
        watch_hist_ori = pd.read_csv(data_col.WATCH_HIST_CSV)

        watch_hist_ori = watch_hist_ori[watch_hist_ori['channelId'].notna()]
        # watch_hist_ori = date_range(watch_hist_ori, 'date_time', start_date='2021-01-01', end_date='2022-01-01')
        watch_hist = merge_df(watch_hist_ori, video_info)

        avg_stats(watch_hist_ori, watch_hist, to_save=True)  # used ori here: some videos may be unavailable at the time of calling video API
        # playlist = playlist_views(watch_hist, to_save=True)
        hour_graph(watch_hist, to_save=True)
        week_graph(watch_hist, to_save=True)
        month_graph(watch_hist, to_save=True)
        day_graph(watch_hist, to_save=True)
        week_hour_graph(watch_hist, to_print=False, to_save=True)
        top_video(watch_hist, 5, to_save=True)
        top_channel(watch_hist, dev_key, 5, to_save=True)
        top_tags(watch_hist, num=100, to_save=True)
        # top_category(watch_hist, to_save=True, to_print=False)
        # min_max_date(watch_hist)
        return True

    except Exception as e:
        print(e)
        return False


