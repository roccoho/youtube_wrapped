from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
import urllib.request
import os
import pandas as pd
import json
from werkzeug.utils import secure_filename
import data_col
import youtube_api
import panda_man
from threading import Thread
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

finished = False
finished1 = False
th = Thread()
th1 = Thread()
UPLOAD_FOLDER = 'uploads/'
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
    global finished1
    finished1 = False
    global finished
    finished = False
    return render_template('intro.html')


def get_api(api_key):
    global finished
    response = data_col.get_info(api_key)
    data_col.video_json_to_csv(response)
    panda_man.manipulate_data(api_key)
    finished = True


@app.route('/result')
def result():
    global finished
    finished = False
    # delete folder and recreate to clear folder contents
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.mkdir(UPLOAD_FOLDER)

    data = csv_to_json(
        csv_name=['stats', 'video_hist', 'channel_hist', 'tags_hist', 'hour_hist',
                  'month_hist', 'day_hist', 'week_hist', 'week_hour_hist'], folder='stats')
    return render_template('result.html', data=data)


@app.route('/status1')
def thread_status1():
    if finished1 is not False:
        cur_status = 'finished'
    else:
        cur_status = 'running'
    return jsonify(dict(status=cur_status))


@app.route('/status')
def thread_status():
    # Return the status of the worker thread
    return jsonify(dict(status=('finished' if finished else 'running')))


@app.route('/api_key_date', methods=['GET', 'POST'])
def api_key_date():
    error = None
    if request.method == 'POST':
        global finished1
        finished1 = False
        api_key = request.form['api_key']
        datefrom = request.form['datefrom']
        dateto = request.form['dateto']
        dates = [datefrom, dateto]
        print(dates)
        test_id = youtube_api.video_to_json('dQw4w9WgXcQ', api_key)
        if test_id:  # test if project id works
            dates = data_col.filter_watch_hist_date(datefrom, dateto)
            if dates:
                global th
                global finished
                finished = False
                th = Thread(target=get_api, args=(api_key,))
                th.start()
                return render_template('loading.html')
            else:
                error = "Date error"
        else:
            error = "Invalid API key"

    else:
        dates = finished1
        if not dates:
            return render_template('intro.html', error='wrong JSON file')

    return render_template('api_key.html', dates=dates, error=error)


def get_dates(filename):
    global finished1
    finished1 = data_col.watch_hist_json_to_csv(filename)


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
            global th1
            global finished1
            finished1 = False
            th1 = Thread(target=get_dates, args=(final_filename,))
            th1.start()
            return render_template('upload_loading.html')
        else:
            error = 'Incorrect file type'

    return render_template('intro.html', error=error)


# @app.route('/')
# def intro():
#     data = csv_to_json(
#         csv_name=['stats', 'video_hist', 'channel_hist', 'tags_hist', 'hour_hist',
#                   'month_hist', 'day_hist', 'week_hist', 'week_hour_hist'], folder='stats')
#     return render_template('result.html', data=data)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

