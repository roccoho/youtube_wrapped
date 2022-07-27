from flask import Flask, render_template, url_for, request, flash, redirect
import urllib.request
import os
import pandas as pd
import json
from werkzeug.utils import secure_filename
import data_col
import youtube_api
import panda_man

# fix empty x axis
# create executable
# bottleneck: API calls?
# loading screen when requesting
# setup server?
# oauth for project id?
# wordcloud for video tags/categories & search history:
#  https://github.com/jasondavies/d3-cloud
#  https://observablehq.com/@contervis/clickable-word-cloud
# matrix chart for hour & dayofweek:
#  https://github.com/kurkle/chartjs-chart-matrix
# better way to parse response
# maybe remove read write of json/csv files
# handle different dates in html file: ignore

UPLOAD_FOLDER = '/uploads/'
app = Flask(__name__)

def csv_to_json(csv_name, folder=''):
    dicts = {}
    for i in csv_name:
        csv = f'{folder}/{i}.csv'
        df = pd.read_csv(csv)
        dict = df.to_dict(orient='list')
        dicts[i] = dict
    return dicts


@app.route('/')
def intro():
    return render_template('intro.html')


@app.route('/api_key_date', methods=['POST'])
def api_key():
    if request.method == 'POST':
        api_key = request.form['api_key']
        datefrom = request.form['datefrom']
        dateto = request.form['dateto']
        dates = [datefrom, dateto]
        print(dates)
        test_id = youtube_api.video_to_json('dQw4w9WgXcQ', api_key)
        if test_id:  # test if project id works
            dates = data_col.filter_watch_hist_date(datefrom, dateto)
            if dates:
                response = data_col.get_info(api_key)
                data_col.video_json_to_csv(response)
                panda_man.manipulate_data(api_key)
                data = csv_to_json(
                    csv_name=['stats', 'video_hist', 'channel_hist', 'tags_hist', 'hour_hist',
                              'month_hist', 'day_hist', 'week_hist', 'week_hour_hist'], folder='stats')
                return render_template('result.html', data=data)
            else:
                error = "Date error"
        else:
            error = "Invalid API key"

    return render_template('api_key.html', dates=dates, error=error)


@app.route('/display', methods=['POST'])
def save_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        file_type = filename.split('.').pop();
        if file_type == 'json':
            f.save(UPLOAD_FOLDER + filename)
            dates = data_col.watch_hist_json_to_csv(f'{UPLOAD_FOLDER}{filename}')

            if dates:
                return render_template('api_key.html', dates=dates)
            else:
                error = 'Wrong JSON file'

        else:
            error = 'Incorrect file type'

    return render_template('intro.html', error=error)


# @app.route('/')
# def intro():
#     data = csv_to_json(
#         csv_name=['stats', 'video_hist', 'channel_hist', 'tags_hist', 'hour_hist',
#                   'month_hist', 'day_hist', 'week_hist', 'week_hour_hist'], folder='stats')
#     return render_template('.html', data=data)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=False)

