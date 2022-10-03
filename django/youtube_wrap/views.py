from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from werkzeug.utils import secure_filename
from django.core.files.storage import default_storage
import shutil
import os
from . import data_col
from . import panda_man
from . import youtube_api
import pandas as pd

UPLOAD_FOLDER = './youtube_wrap/uploads/'
RESULTS_FOLDER = './youtube_wrap/stats/'


def index(request):
    print("deleted folder and recreated to clear folder contents")
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    shutil.rmtree(RESULTS_FOLDER, ignore_errors=True)
    os.mkdir(UPLOAD_FOLDER)
    os.mkdir(RESULTS_FOLDER)
    return render(request, 'intro.html')


def display(request):
    error = None
    if request.method == 'POST':
        file_object = request.FILES['file']
        filename = secure_filename(file_object.name)
        file_type = filename.split('.').pop()
        if file_type == 'json':
            final_filename = UPLOAD_FOLDER + filename

            with open(final_filename, 'wb+') as ff:
                ff.write(file_object.read())

            dates = data_col.watch_hist_json_to_csv(final_filename)
            if dates:
                    return render(request, 'api_key.html', {'dates': dates, 'error': error})
            else:
                error = 'Wrong json file'

        else:
            error = 'Incorrect file type'

    return render(request, 'intro.html', {'error': error})


def result(request):
    error = None
    if request.method == 'POST':
        api_key = request.POST['api_key']
        datefrom = request.POST['datefrom']
        dateto = request.POST['dateto']
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
                return render(request, 'result.html', {'data': data})
            else:
                error = "Date error"
        else:
            error = "Invalid API key"

    else:
        return render(request, 'intro.html', {'error':'wrong JSON file'})

    return render(request, 'api_key.html', {'dates':dates, 'error': error})


def csv_to_json(csv_name, folder=''):
    dicts = {}
    for i in csv_name:
        csv = f'{folder}{i}.csv'
        df = pd.read_csv(csv)
        dict = df.to_dict(orient='list')
        dicts[i] = dict
    return dicts

