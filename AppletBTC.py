#!/usr/bin/python3

import time
import threading
import gi
import requests
import json
import sqlite3
import os

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk as gtk
from datetime import datetime

database = 'DataBase.sqlite'
tabla = 'BTC_VALUES'


def get_datetime():
    now_datetime = datetime.today()
    return now_datetime.strftime('%Y-%m-%d'), now_datetime.strftime('%H:%M')


def create_database():
    conn = sqlite3.connect(database)
    conn.commit()
    conn.close()


def create_table():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE {tabla} (
        'id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'fecha' VARCHAR(25),
        'hora' VARCHAR(25),
        'valor' VARCHAR(25)
    )''')
    conn.commit()
    conn.close()


def insert_value(value):
    now = get_datetime()
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cmd = f'''INSERT INTO {tabla}(fecha, hora, valor) VALUES ('{now[0]}', '{now[1]}', '{value}')'''
    cursor.execute(cmd)
    conn.commit()
    conn.close()


def end_element():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cmd = f'SELECT * FROM {tabla} ORDER BY id DESC LIMIT 1'
    cursor.execute(cmd)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    if len(datos) != 0:
        return datos[0][3]
    else:
        return 'Conectando...'


def start_database():
    if not os.path.isfile(database):
        create_database()
        create_table()


# CLIENTE DE API DE COINBASE


url = 'https://api.coinbase.com/v2/prices/BTC-USD/buy'


def btc_value():
    start_database()
    try:
        res = requests.get(url)
        if res.status_code == 200:
            btc = json.loads(res.content)['data']['amount']
            insert_value(btc)
            return f' {btc}$'
        else:
            return f' {end_element()}$ L'
    except:
        return f' {end_element()}$ E'


# APPLET BTC


id = 'AppletBTC'
icon = '/home/oswaldo/Escritorio/AppletBTC/bitcoin.svg'
applet = appindicator.Indicator.new(id, icon, appindicator.IndicatorCategory.APPLICATION_STATUS)


def update_services():
    while True:
        time.sleep(60)
        applet.set_label(btc_value(), '')


def main():
    update_btc = threading.Thread(target=update_services)
    update_btc.daemon = True
    applet.set_status(appindicator.IndicatorStatus.ACTIVE)
    applet.set_label(btc_value(), '')
    applet.set_menu(_menu())
    update_btc.start()
    gtk.main()


def _menu():
    menu = gtk.Menu()

    coinbase = gtk.MenuItem(label='CoinBase')
    coinbase.connect('activate', lambda _: os.system("x-www-browser https://www.coinbase.com/es/price/bitcoin"))
    menu.append(coinbase)

    Separator = gtk.SeparatorMenuItem()
    menu.append(Separator)

    exit_applet = gtk.MenuItem(label='Salir')
    exit_applet.connect('activate', lambda _: gtk.main_quit())
    menu.append(exit_applet)

    menu.show_all()
    return menu


if __name__ == "__main__":
    main()
