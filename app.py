from flask import Flask, render_template, redirect, request, url_for, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from _init_db_ import __init_data__

import os
import datetime
import time
import random

app = Flask(__name__)
app.secret_key = "butpaluck.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client = MongoClient('localhost', 27017)
db = client.but_paluck
stations = db.stations
around_bus = db.around_bus
tickets = db.tickets
paymented = db.paymented


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
    seat = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
            12, 13, 14, 15, 16, 17, 18, 19, 20]
    for s in station:
        name.append(s['station_name'])
    for i in range(len(__init_data__())):
        if __init_data__()[i] not in name:
            # print(__init_data__()[i])
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
        date_start = datetime.datetime.strptime(
            request.form['calendar-start'] + " " + "18:00", '%Y-%m-%d %H:%M')
        people = request.form['cout-people']

        around_bus_end = []

        if select == 'option1':
            date_return = 'none'
            around_bus_start = around_bus.find({'station_name': start})
            arbe_id = 0
        else:
            date_return = request.form['calendar-return']
            date_return = datetime.datetime.strptime(
                date_return + " " + "18:00", '%Y-%m-%d %H:%M')
            around_bus_start = around_bus.find({'station_name': start})
            around_bus_end = around_bus.find({'station_name': end})
            arbe_id = around_bus_end[0]['_id']

        _id = tickets.insert_one({
            'select': select, 'start': start, 'end': end, 'date_start': date_start,
            'date_return': date_return, 'people': int(people), 'position1': 0, 'position2': 0,
            'around_bus_start': around_bus_start[0]['_id'], 'around_bus_end': arbe_id,
            'price_start': 0, 'price_end': 0
        }).inserted_id
        # print(_id)

    return render_template('select_time.html',
                           option=select,
                           around_bus_start=around_bus_start,
                           around_bus_end=around_bus_end,
                           start=start,
                           end=end,
                           id=_id,
                           start_date=date_start,
                           end_date=date_return)


@app.route('/select/time/<id>/<time_im>/<r_time>/<start_id>/<end_id>', methods=['GET', 'POST'])
def select_time(id, time_im, r_time, start_id, end_id):


    obj = tickets.find_one({"_id": ObjectId(id)})
    select = obj['select']
    around_bus_end = []

    if select == 'option1':
        around_bus_start = around_bus.find({'station_name': obj['start']})
        if time_im != '0':
            st_time = time_im
            en_time = st_time
            # print(obj['date_start'].strftime("%Y-%m-%d"))
            date_start = datetime.datetime.strptime(
                obj['date_start'].strftime("%Y-%m-%d") + " " + time_im, '%Y-%m-%d %H:%M')
            tickets.find_one_and_update({"_id": ObjectId(id)}, {
                "$set": {'date_start': date_start, 'around_bus_start': start_id}})
        else:
            en_time = r_time
            date_end = datetime.datetime.strptime(obj['date_return'].strftime(
                "%Y-%m-%d") + " " + r_time, '%Y-%m-%d %H:%M')
            tickets.find_one_and_update({"_id": ObjectId(id)}, {
                "$set": {'date_return': date_end, 'around_bus_end': end_id}})
    else:
        around_bus_start = around_bus.find({'station_name': obj['start']})
        around_bus_end = around_bus.find({'station_name': obj['end']})
        if time_im != '0':
            st_time = time_im
            en_time = obj['date_return'].strftime("%H:%M")
            # print(obj['date_start'].strftime("%Y-%m-%d"))
            date_start = datetime.datetime.strptime(
                obj['date_start'].strftime("%Y-%m-%d") + " " + time_im, '%Y-%m-%d %H:%M')
            tickets.find_one_and_update({"_id": ObjectId(id)}, {
                "$set": {'date_start': date_start, 'around_bus_start': start_id}})
        else:
            en_time = r_time
            st_time = obj['date_start'].strftime("%H:%M")
            date_end = datetime.datetime.strptime(obj['date_return'].strftime(
                "%Y-%m-%d") + " " + r_time, '%Y-%m-%d %H:%M')
            tickets.find_one_and_update({"_id": ObjectId(id)}, {
                "$set": {'date_return': date_end, 'around_bus_end': end_id}})

    time.sleep(1)

    return render_template('select_time.html',
                           option=select,
                           around_bus_start=around_bus_start,
                           around_bus_end=around_bus_end,
                           start=obj['start'],
                           end=obj['end'],
                           id=id,
                           start_date=st_time,
                           end_date=en_time)


@app.route('/select/seat/<id>/', methods=['GET', 'POST'])
def select_seat(id):

    obj = tickets.find_one({"_id": ObjectId(id)})
    select = obj['select']
    around_bus_end = []
    s_id = obj['around_bus_start']
    people = obj['people']
    selected_e = []

    if select == 'option1':
        around_bus_start = around_bus.find_one({"_id": ObjectId(s_id)})
        ls = around_bus_start['backup_seat']
        selected = []
        for item in ls:
            if item != 0 and len(selected) < people:
                selected.append(item)
            else:
                pass
        tickets.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": {'price_start': around_bus_start['price']}})
    else:
        _id = obj['around_bus_end']
        around_bus_start = around_bus.find_one({"_id": ObjectId(s_id)})
        around_bus_end = around_bus.find_one({"_id": ObjectId(_id)})

        tickets.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": {'price_start': around_bus_start['price'],
                     'price_end': around_bus_end['price']}})

        ls = around_bus_start['backup_seat']
        selected = []
        ls_e = around_bus_end['backup_seat']

        for item in ls:
            if item != 0 and len(selected) < people:
                selected.append(item)
            else:
                pass
        for item in ls_e:
            if item != 0 and len(selected_e) < people:
                selected_e.append(item)
            else:
                pass

    return render_template('select_seat.html',
                           id=id,
                           option=select,
                           around_bus_start=around_bus_start,
                           around_bus_end=around_bus_end,
                           people=people,
                           people_check_s=selected,
                           people_check_e=selected_e)


@app.route('/selected/seat/<id>/', methods=['GET', 'POST'])
def selected_seat(id):

    obj = tickets.find_one({"_id": ObjectId(id)})
    people = obj['people']

    if request.method == 'POST':
        form = request.form
        seat_srart = form.getlist('seat_start')
        seat_return = form.getlist('seat_end')

        # print(len(seat_srart))
        if obj['select'] == 'option2':
            s_id = obj['around_bus_start']
            _id = obj['around_bus_end']
            around_bus_start = around_bus.find_one({"_id": ObjectId(s_id)})
            around_bus_end = around_bus.find_one({"_id": ObjectId(_id)})

            if len(seat_srart) == people and len(seat_return) == people:
                # print('seat', seat_srart, seat_return)
                tickets.find_one_and_update({"_id": ObjectId(id)}, {
                    "$set": {'position1': seat_srart, 'position2': seat_return}})

                for s in seat_srart:
                    around_bus_start['backup_seat'][int(s)-1] = 0
                around_bus.find_one_and_update({"_id": ObjectId(s_id)}, {
                    "$set": {'backup_seat': around_bus_start['backup_seat']}})
                for e in seat_srart:
                    around_bus_end['backup_seat'][int(e)-1] = 0
                around_bus.find_one_and_update({"_id": ObjectId(_id)}, {
                    "$set": {'backup_seat': around_bus_end['backup_seat']}})

            else:
                ls_e = around_bus_end['backup_seat']
                ls = around_bus_start['backup_seat']
                selected_e = []
                selected = []
                for item in ls:
                    if item != 0 and len(selected) < people:
                        selected.append(item)
                    else:
                        pass
                for item in ls_e:
                    if item != 0 and len(selected_e) < people:
                        selected_e.append(item)
                    else:
                        pass
                tickets.find_one_and_update({"_id": ObjectId(id)}, {
                    "$set": {'position1': selected, 'position2': selected_e}})
                for s in selected:
                    around_bus_start['backup_seat'][int(s)-1] = 0
                around_bus.find_one_and_update({"_id": ObjectId(s_id)}, {
                    "$set": {'backup_seat': around_bus_start['backup_seat']}})
                for e in selected_e:
                    around_bus_end['backup_seat'][int(e)-1] = 0
                around_bus.find_one_and_update({"_id": ObjectId(_id)}, {
                    "$set": {'backup_seat': around_bus_end['backup_seat']}})
        else:
            s_id = obj['around_bus_start']
            around_bus_start = around_bus.find_one({"_id": ObjectId(s_id)})
            if len(seat_srart) == people:
                tickets.find_one_and_update({"_id": ObjectId(id)}, {
                    "$set": {'position1': seat_srart}})
                for s in seat_srart:
                    around_bus_start['backup_seat'][int(s)-1] = 0
                around_bus.find_one_and_update({"_id": ObjectId(s_id)}, {
                    "$set": {'backup_seat': around_bus_start['backup_seat']}})
            else:
                selected = []
                ls = around_bus_start['backup_seat']
                for item in ls:
                    if item != 0 and len(selected) < people:
                        selected.append(item)
                    else:
                        pass
                tickets.find_one_and_update({"_id": ObjectId(id)}, {
                    "$set": {'position1': selected}})
                for s in selected:
                    around_bus_start['backup_seat'][int(s)-1] = 0
                around_bus.find_one_and_update({"_id": ObjectId(s_id)}, {
                    "$set": {'backup_seat': around_bus_start['backup_seat']}})

    return render_template('bus_passenger.html', ticket=obj)


@app.route('/ticket/payment/<id>/', methods=['GET', 'POST'])
def payment(id):
    # print(id)
    if request.method == 'POST':
        ticket_no = random.randint(0, 10000000000)
        card_id = request.form['card_id']
        name = request.form['name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        ticket_id = id

        paymented.insert_one({
            'ticket_no': ticket_no,
            'card_id': card_id,
            'name': name,
            'phone_number': phone_number,
            'email': email,
            'ticket_id': ticket_id
        })

    return render_template('payment.html', ticket_no=ticket_no)


@app.route('/Return/tickets', methods=['GET', 'POST'])
def return_tickets():

    if request.method == 'POST':
        id = request.form['ticket-no-2']
        obj = paymented.find_one({'ticket_no': int(id)})
    return render_template('return_tickets.html', no=id)


@app.route('/postpone/tickets', methods=['GET', 'POST'])
def postpone_tickets():

    if request.method == 'POST':
        id = request.form['ticket-no-1']
        obj = paymented.find_one({'ticket_no': int(id)})
        ticket = tickets.find_one({'_id': ObjectId(obj['ticket_id'])})
    return render_template('postpone_tickets.html', no=id, ticket=ticket)


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/admin/add/bus/station', methods=['GET', 'POST'])
def addStation():
    if request.method == 'POST':
        date = datetime.datetime.today()
        time = request.form['start_time'].split(':')
        ftime = datetime.time(int(time[0]), int(time[1]), 0)
        count_seat = request.form['seat']
        price = request.form['price']
        seat = []
        for i in range(int(count_seat)):
            seat.append(i+1)
        station = request.form['station']

        stations.insert_one(
            {'station_name': station, 'start_time': date})
        
        around_bus.insert_one({
            'station_name': station, 'start_time': datetime.datetime.combine(date, ftime), 'seat': seat, 'count_seat': int(count_seat), 'backup_seat': seat, 'price': int(price)
        })
        flash('เพิ่มข้อูลสำเร็จ')
    return redirect(url_for('admin'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
