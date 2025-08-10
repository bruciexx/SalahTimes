#!/usr/bin/env python
from os import get_terminal_size as get_tsize
from time import time as tnow
from pytz import timezone as tz
from suncalc import get_position as spos, get_times as sphases
from datetime import datetime as dt, timezone as dtz
from timezonefinder import TimezoneFinder as tzf
from geopy.geocoders import Photon
import pandas as pd

'''initializing global variables'''
geolocator = Photon(user_agent="measurements")  # init geocoder user agent
lon = 39.826155
lat = 21.4224609
local_tz = None

'''setting pandas options'''
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 20)


def line():
    t_size = get_tsize()
    t_width = t_size.columns
    print(t_width * "-")


def flush():
    print('\033c', end="")


def main_menu():
    line()
    print('Main menu')
    line()
    print('commands:')
    print('loca, l - change location')
    print('help, h - print this menu to list available commands')
    print('clear, c - clear the screen')
    print('quit, q, exit - exit the CLI')


def localization():
    '''get locale/timezone'''
    global lon, lat, local_tz

    # default
    lad = "Amsterdam"
    lon = 4.9138
    lat = 52.36386

    try:
        loca = geolocator.geocode(lad)
        if loca:
            lon = loca.longitude
            lat = loca.latitude
        else:
            lon = lon
            lat = lat
    except Exception as e:
        print(f"Geocoding error: {e}")
        lon = lon
        lat = lat
    # get timezone
    lc = tzf()
    tz_name = lc.timezone_at(lng=lon, lat=lat)
    local_tz = tz(tz_name) if tz_name else tz('UTC')

    # ask user
    while True:
        q1 = input("do you want to change location? (y/N): ").lower().strip()
        if q1 != 'y':
            break
        q2 = input("use device location? (y/N): ").lower().strip()
        if q2 == 'y':
            # TODO add location services
            print("we are working on this feature! using default location.")
            break
        elif q2 == 'n':
            print("1. provide coordinates")
            print("2. provide city name")
            q3 = int(input("choose localization method: "))
            if q3 == 1:
                try:
                    lon = float(input("provide a longtitude (ex: 21.426): "))
                    lat = float(input("provide a latitude (ex: 39.825): "))
                    # update timezone
                    tz_name = lc.timezone_at(lng=lon, lat=lat)
                    local_tz = tz(tz_name) if tz_name else tz('UTC')
                    break
                except ValueError:
                    print("please enter numbers only...")
            elif q3 == 2:
                try:
                    city = input("cite name (ex: Mecca): ")
                    loca = geolocator.geocode(city)
                    lon = loca.longitude
                    lat = loca.latitude
                    tz_name = lc.timezone_at(lng=lon, lat=lat)
                    local_tz = tz(tz_name) if tz_name else tz('UTC')
                    break
                except Exception:
                    print("invalid city name")
            else:
                print("please choose a valid option")
        else:
            print("please answer 'y' or 'n'...")


def main():
    flush()
    main_menu()

    while True:
        command = input('>').strip().lower()
        if command in ('help', 'h'):
            main_menu()
        elif command in ('clear', 'c'):
            flush()
        elif command in ('quit', 'q', 'exit'):
            flush()
            exit()
        elif command in ('location', 'loca', 'l'):
            localization()
        elif command == 'insert':
            line()
            eval(input('>'))
        elif not command:
            continue
        else:
            print(f"Command '{command}' was not recognized")
            print("type h or help to see a list of commands")


if __name__ == "__main__":
    main()
