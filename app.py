from flask import Flask, render_template, redirect, request, url_for, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from _init_db_ import __init_data__

import os
import datetime
import time

app = Flask(__name__)
app.secret_key = "butpaluck.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client = MongoClient('localhost', 27017)
db = client.but_paluck
stations = db.stations
around_bus = db.around_bus
tickets = db.tickets


def _init_db_():
    name = []
    station = stations.find()
    date = datetime.datetime.today()
    time_1 = datetime.time(18, 0, 0)
    time_2 = datetime.time(19, 0, 0)
    time_3 = datetime.time(20, 0, 0)
    datetime_1 = datetime.datetime.combine(date, time_1)
    datetime_2 = datetime.datetime.combine(date, time_2)
    datetime_3 = datetime.datetime.combine(date, time_3)
    time = [datetime_1, datetime_2, datetime_3]
    seat = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
            12, 13, 14, 15, 16, 17, 18, 19, 20]
    for s in station:
        name.append(s['station_name'])
    for i in range(len(__init_data__())):
        # print(station[i]['station_name'])
        if __init_data__()[i] not in name:
            stations.insert_one(
                {'station_name': __init_data__()[i], 'start_time': date})
            around_bus.insert_one({
                'station_name': __init_data__()[i], 'start_time': datetime_1, 'seat': seat, 'count_seat': 20, 'backup_seat': seat, 'price': 650
            })
            around_bus.insert_one({
                'station_name': __init_data__()[i], 'start_time': datetime_2, 'seat': seat, 'count_seat': 20, 'backup_seat': seat, 'price': 700
            })
            around_bus.insert_one({
                'station_name': __init_data__()[i], 'start_time': datetime_3, 'seat': seat, 'count_seat': 20, 'backup_seat': seat, 'price': 700
            })
        else:
            pass


_init_db_()


@app.route('/')
def home():
    print(__init_data__())
    return render_template('index.html')


@app.route('/search')
def search():
    location = stations.find()
    location2 = stations.find()

    return render_template('search.html', stations=location, stations2=location2)


@app.route('/choose/time', methods=['GET', 'POST'])
def choose_time():
    if request.method == 'POST':

        select = request.form['select']
        start = request.form['start']
        end = request.form['end']
        date_start = datetime.datetime.strptime(request.form['calendar-start'] + " " + "18:00", '%Y-%m-%d %H:%M')
        people = request.form['cout-people']

        around_bus_end = []

        if select == 'option1':
            date_return = 'none'
            around_bus_start = around_bus.find({'station_name': start})
        else:
            date_return = request.form['calendar-return']
            date_return = datetime.datetime.strptime(date_return + " " + "18:00", '%Y-%m-%d %H:%M')
            around_bus_start = around_bus.find({'station_name': start})
            around_bus_end = around_bus.find({'station_name': end})

        _id = tickets.insert_one({
            'select': select, 'start': start, 'end': end, 'date_start': date_start, 'date_return': date_return, 'people': people, 'position': 0
        }).inserted_id
        print(_id)

    return render_template('select_time.html',
                           option=select,
                           around_bus_start=around_bus_start,
                           around_bus_end=around_bus_end,
                           start=start,
                           end=end,
                           id=_id,
                           start_date = date_start,
                           end_date = date_return)


@app.route('/select/time/<id>/<time_im>/<r_time>', methods=['GET', 'POST'])
def select_time(id,time_im,r_time):

    obj = tickets.find_one({"_id": ObjectId(id)})
    print(r_time)
    select = obj['select']
    around_bus_end = []

    if time_im != '0':
        st_time = time_im
        en_time = obj['date_return'].strftime("%H:%M")
        print(obj['date_start'].strftime("%Y-%m-%d"))
        date_start = datetime.datetime.strptime(obj['date_start'].strftime("%Y-%m-%d") + " " + time_im, '%Y-%m-%d %H:%M')
        tickets.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": {'date_start': date_start}})
    else:
        en_time = r_time
        st_time = obj['date_start'].strftime("%H:%M")
        # print(obj['date_start'])
        date_end = datetime.datetime.strptime(obj['date_return'].strftime("%Y-%m-%d") + " " + r_time, '%Y-%m-%d %H:%M')
        tickets.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": {'date_return': date_end}})

    if select == 'option1':
        around_bus_start = around_bus.find({'station_name': obj['start']})
    else:
        around_bus_start = around_bus.find({'station_name': obj['start']})
        around_bus_end = around_bus.find({'station_name': obj['end']})

    time.sleep(1)

    return render_template('select_time.html',
                           option=select,
                           around_bus_start=around_bus_start,
                           around_bus_end=around_bus_end,
                           start=obj['start'],
                           end= obj['end'],
                           id=id,
                           start_date = st_time,
                           end_date = en_time)

@app.route('/position/<id>/<time>/', methods=['GET', 'POST'])
def select_position(id,time):
    print(id,time)
    return id


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/admin/add/bus/station', methods=['GET', 'POST'])
def addStation():
    if request.method == 'POST':
        print(request.form['station'])
        stations.insert_one({'station_name': request.form['station']})
    return redirect(url_for('admin'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
