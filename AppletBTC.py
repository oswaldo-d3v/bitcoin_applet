#!/usr/bin/python3

from concurrent.futures import thread
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
from datetime import datetime as dt

database = 'DataBase.sqlite'
tabla = 'BTC_VALUES'


def get_datetime():
    now_datetime = dt.today()
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
    fecha, hora = get_datetime()
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cmd = f'INSERT INTO {tabla}(fecha, hora, valor) VALUES (?, ?, ?)'
    cursor.execute(cmd, (fecha, hora, value))
    conn.commit()
    conn.close()


def end_element():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cmd = f'SELECT * FROM {tabla} ORDER BY id DESC LIMIT 1'
    cursor.execute(cmd)
    datos = cursor.fetchone()
    conn.commit()
    conn.close()
    return datos[3] if datos else 'Conectando...'


def start_database():
    if not os.path.isfile(database):
        create_database()
        create_table()


# CLIENTE DE API DE COINBASE


url = 'https://api.coinbase.com/v2/prices/BTC-USD/buy'


def btc_value():
    start_database()
    btc = end_element()
    try:
        res = requests.get(url)
        if res.status_code == requests.codes.ok:
            btc = json.loads(res.content)['data']['amount']
            insert_value(btc)
            return f'{btc}$'
    except requests.exceptions.ConnectionError:
      return f'{btc}$ D'
    except requests.exceptions.HTTPError:
      return f'{btc}$ H'
    except requests.exceptions.Timeout:
      return f'{btc}$ T'
    except requests.exceptions.TooManyRedirects:
      return f'{btc}$ R'
    return f'{btc}$ L'


# APPLET BTC


id = 'AppletBTC'
icon = '/home/oswaldo/Documentos/Programacion/Python/AppletBTC/bitcoin.svg'
applet = appindicator.Indicator.new(id, icon, appindicator.IndicatorCategory.APPLICATION_STATUS)


def update_services():
    while True:
        applet.set_label(btc_value(), '')
        time.sleep(60)


def main():
    update_btc = threading.Thread(name='Actualizar valor BTC', target=update_services)
    update_btc.setDaemon(True)
    applet.set_status(appindicator.IndicatorStatus.ACTIVE)
    update_btc.start()
    applet.set_menu(_menu())
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
