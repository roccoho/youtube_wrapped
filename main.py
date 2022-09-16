from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
import urllib.request
import os
import pandas as pd
import json
from werkzeug.utils import secure_filename
import data_col
import youtube_api
import panda_man
import time
import shutil
import os

# fix empty x axis
# x axis offset
# create executable
# bottleneck: API calls?
# oauth for project id?
# better way to parse response
# maybe remove read write of json/csv files
# handle different dates in html file: ignore

app = Flask(__name__)
UPLOAD_FOLDER = './uploads/'
RESULTS_FOLDER = './stats/'


def csv_to_json(csv_name, folder=''):
    dicts = {}
    for i in csv_name:
        csv = f'{folder}{i}.csv'
        df = pd.read_csv(csv)
        dict = df.to_dict(orient='list')
        dicts[i] = dict
    return dicts


@app.route('/')
def intro():
    print("deleted folder and recreated to clear folder contents")
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    shutil.rmtree(RESULTS_FOLDER, ignore_errors=True)
    os.mkdir(UPLOAD_FOLDER)
    os.mkdir(RESULTS_FOLDER)
    return render_template('intro.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    error = None
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
                print("pandas manipulation")
                panda_man.manipulate_data(api_key)
                data = csv_to_json(
                    csv_name=['stats', 'video_hist', 'channel_hist', 'tags_hist', 'hour_hist',
                              'month_hist', 'day_hist', 'week_hist', 'week_hour_hist'],
                    folder=RESULTS_FOLDER)
                print(data['stats'])
                return render_template('result.html', data=data)
            else:
                error = "Date error"
        else:
            error = "Invalid API key"

    else:
        return render_template('intro.html', error='wrong JSON file')

    return render_template('api_key.html', dates=dates, error=error)


@app.route('/display', methods=['POST'])
def save_file():
    error = None
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        file_type = filename.split('.').pop()
        if file_type == 'json':
            final_filename = UPLOAD_FOLDER + filename
            f.save(final_filename)
            print(final_filename)
            dates = data_col.watch_hist_json_to_csv(final_filename)
            if dates:
                return render_template('api_key.html', dates=dates, error=error)
            else:
                error = 'Wrong json file'
        else:
            error = 'Incorrect file type'

    return render_template('intro.html', error=error)


# @app.route('/')
# def intro():
#     data = csv_to_json(
#         csv_name=['stats', 'video_hist', 'channel_hist', 'tags_hist', 'hour_hist',
#                   'month_hist', 'day_hist', 'week_hist', 'week_hour_hist'], folder=RESULTS_FOLDER)
#     return render_template('result.html', data=data)


# if __name__ == "__main__":
#     app.secret_key = 'super secret key'
#     app.config['SESSION_TYPE'] = 'filesystem'
#     app.run(debug=True)

