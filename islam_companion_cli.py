#!/usr/bin/env python
from os import get_terminal_size as get_tsize
from time import time as tnow
from pytz import timezone as tz
from suncalc import get_position as spos, get_times as sphases
from datetime import datetime as dt, timezone as dtz
import pandas as pd

'''setting pandas options'''
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 20)


def line():
    t_size = get_tsize()
    t_width = t_size.columns
    print(t_width * "-")


def flush_screen():
    print('\033c', end="")


def main_menu():
    line()
    print('Main menu')
    line()
    print('commands:')
    print('help, h - print this menu to list available commands')
    print('clear, c - clear the screen')
    print('quit, q, exit - exit the CLI')


'''get locale/timezone'''
def localization():
    lon = 4.9138
    lat = 52.36386
    local_tz = tz('Europe/Amsterdam')
    q1 = input("do you want to change location? (y/N)")
    q2 = input("do you want us to use your location? (y/N)")
    if q1 == 'y':
        if q2 == 'y':
            print("we are working on this feature")  # add feature
        elif q2 == 'n':
            lon = input("please provide a longtitude; ex: 21.426")
            lat = input("please provide a latitude; ex: 39.825")
        else:
            print


def main():
    flush_screen()
    main_menu()
    while True:
        command = input('>')
        if command == 'help' or command == 'h':
            main_menu()
        elif command == 'c' or command == 'clear':
            flush_screen()
        elif command == 'quit' or command == 'q' or command == 'exit':
            flush_screen()
            exit()
        elif command == '' or command == ' ':
            continue
        else:
            print("'" + command + "' was not recognized")
            print("type h or help to see a list of commands")


main()
