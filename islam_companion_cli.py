#!/usr/bin/env python
from os import get_terminal_size as get_tsize
from pytz import timezone as tz
from suncalc import get_position as spos, get_times as sphases
from datetime import datetime as dt, timezone as dtz
from functools import lru_cache
from timezonefinder import TimezoneFinder as tzf
from bidi.algorithm import get_display as gd
from geopy.geocoders import Photon, Nominatim
import arabic_reshaper as ara
import unicodedata as ucd
import requests as rq
import pandas as pd
import time as t
import sys
import os

# global constants
default_lad = "Mecca"
default_lon = 39.826155
default_lat = 21.4224609
arabic_test_text = 'اللَّهُ  \ufdf2'
basmala = '\uFDFD'
loading_frames = {
    1: ['', '.', '..', '...'],
    2: ['.\\', '--', './', '.|']
}
surahs = {}
cmd_map = {}

# global state
lad = default_lad
lon = default_lon
lat = default_lat
local_tz = None
tz_finder = tzf()
location_cache = {}

# setting pandas options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 20)

# configure arabic reshaper
ara_reshaper = ara.ArabicReshaper(configuration={
    'delete_harakat': False,  # preserve diacritics
    'support_ligatures': True,  # enable ligature handling
    'delete_tatweel': False,  # keep tajweed
    'shift_harakat_position': False,
    'language': 'Arabic',
    'use_unshaped_instead_of_isolated': True,
    'support_zwj': True
})

# Initialize geocoder
geolocator = Photon(user_agent="measurements", timeout=10) or Nominatim(user_agent="measurements", timeout=10)


def line():
    '''print horizontal line across terminal width'''
    print("-" * get_tsize().columns)


def flush():
    '''clear terminal screen'''
    print('\033c', end="")


def bsmllh(surah=False, wait=1.35):
    '''display the basmala'''
    if not surah:
        # return basmala
        return basmala
    else:
        # print basmala in center to open surah
        flush()
        line()
        centered_basmala = basmala.center(get_tsize().columns - 5)
        print(centered_basmala)
        line()
        t.sleep(wait)


def fix_arabic(text):
    '''process arabic text for proper display'''
    return gd(ara_reshaper.reshape(ucd.normalize('NFD', text)))


def readfile(filename, quran: bool = False, quiet: bool = True):
    '''read file with error handling, returns contents of file'''
    if not quran:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"error reading {filename}: {e}")
            return ""
    else:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                surah = f.read().strip()
                # go ayah by ayah
                ayahs = [
                    ayah.strip() for ayah in surah.split('\n') if ayah.strip()
                ]
                return '\n'.join(ayahs)
        except Exception as e:
            print(f"error handling surah: {e}")
            return ""


def display_surah(surah_num):
    '''display surah with proper formatting'''
    if surah_num in surahs:
        bsmllh(True)
        t_width = get_tsize().columns

        # align ayahs to centre
        for ayah in surahs[surah_num][2].split('\n'):
            ayah = ayah.strip()
            if ayah:
#                # first center text
#                try:
#                    from wcwidth import wcswidth as wcw
#                    v_width = wcw(ayah)  # get visual width
#                except Exception as e:
#                    print(f"error importing wcwidth module: {e}")
#                    v_width = len([c for c in ayah if not ucd.combining(c)])
#                pad = (t_width - v_width) // 2
#                centered = ' ' * pad + ayah
#
#                # then fix arabic
#                fixed_ayah = fix_arabic(centered)
#                print(fixed_ayah)
                # fix arabic text
                fixed_ayah = fix_arabic(ayah.strip())
                get_spacing = len(fixed_ayah) / 2
                spacing = int(t_width + get_spacing)
                center_ayah = fixed_ayah.center(spacing)
                print(center_ayah)
        line()
    else:
        print(f"Surah {surah_num} not found")


def loading(msg: str, wait: int = 5, style: int = 2):
    '''loading animation'''
    reel = loading_frames.get(style, loading_frames[2])
    start = t.time()
    for _ in range(wait):
        for frame in reel:
            flush()
            print(f"{msg}{frame}")
            t.sleep(0.1)
    print(f"\nloaded in {t.time()-start:.2f}s")


def waitforkey(timeout=9):
    '''wait for keypress or timeout, returns True if key pressed'''
    print(f"press any key to continue ({timeout}s)...", end='', flush=True)

    # posix (unix/macos)
    if os.name == 'posix':
        import select
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            sys.stdin.read(1)
            flush()
            return True

    # windows
    elif os.name == 'nt':
        import msvcrt
        end_time = t.monotonic() + timeout
        while t.monotonic() < end_time:
            if msvcrt.kbhit():
                msvcrt.getch()
                flush()
                return True
            t.sleep(0.025)

    # other
    else:
        loading("checking terminal", timeout, 1)
        return False


def check_terminal_support():
    '''verify arabic rendering support'''
    print("testing terminal compatibility...")
    print(f"raw: {arabic_test_text}")
    print(f"processed: {fix_arabic(arabic_test_text)}")
    print("if the processed arabic doesn't display properly:")
    print("- install arabic supporting fonts.")
    print("- use a different terminal application (i.e. alacritty, konsole)")
    print("- set env: '$ export LANG=ar_SA.UTF-8'")
    waitforkey(20)


def network_check():
    '''test network connectivity with multiple endpoints'''
    endpoints = [
        "https://photon.komoot.io",
        "https://nominatim.openstreetmap.org",
        "https://api.sunrise-sunset.org"
    ]

    success = False
    for url in endpoints:
        try:
            rspns = rq.head(url, timeout=2)
            if rspns.status_code in (200-208, 266, 300-308):
                print(f"✓ {url} accessible; status: {rspns.status_code}")
                success = True
            else:
                print(f"⚠ {url} returned status: {rspns.status_code}")
        except Exception as e:
            print(f"✗ {url} unreachable; statuscode: {e}")

    return success


@lru_cache(maxsize=32)
def geocode_with_retry(location, max_retries=3, delay=1):
    '''cached geocoding with retry mechanism'''
    for attempt in range(max_retries):
        try:
            if loca := geolocator.geocode(location):
                return loca
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                t.sleep(delay)
            else:
                print("max retries exceeded. using default location.")
                return None
    print("geocoding failed. using default location")
    return None


def localization(silent=False):
    '''set location and timezone'''
    global lad, lon, lat, local_tz

    # use default if no valid coords
    if lon == default_lon and lat == default_lat:
        lad = default_lad

    # try geocoding
    loca = geocode_with_retry(lad)

    if loca:
        lon = loca.longitude
        lat = loca.latitude
        if silent is not True:
            print(f"location: {fix_arabic(loca.address)}")
        else:
            print("")
    else:
        if silent is not True:
            print(f"using default location {lad}")
        lon = lon
        lat = lat
    # get timezone
    tz_name = tz_finder.timezone_at(lng=lon, lat=lat)
    local_tz = tz(tz_name) if tz_name else tz('UTC')

    if not silent:
        # ask user
        while True:
            q1 = input("change location? (y/N): ").lower().strip()
            if q1 != 'y':
                cache_key = f"{lon:.4f},{lat:.4f}"
                if cache_key in location_cache:
                    print(f"using cached location: {cache_key}")
                    local_tz = location_cache[cache_key]
                    return
                print(cache_key)
            q2 = input("use device location? (y/N): ").lower().strip()
            if q2 == 'y':
                # TODO add location services
                print("we are working on this feature! using default location")
                break
            elif q2 == 'n':
                print("1. provide coordinates")
                print("2. provide city name")
                try:
                    q3 = int(input("choose localization method: "))
                except Exception as e:
                    print(e)
                if q3 == 1:
                    try:
                        lon_input = input("Longitude (ex: 21.426): ").strip()
                        lat_input = input("Latitude (ex: 39.825): ").strip()

                        # Handle coordinate direction
                        if lon_input.endswith(('W', 'w')):
                            lon = -float(lon_input[:-1])
                        elif lon_input.endswith(('E', 'e')):
                            lon = float(lon_input[:-1])
                        else:
                            lon = float(lon_input)

                        if lat_input.endswith(('S', 's')):
                            lat = -float(lat_input[:-1])
                        elif lat_input.endswith(('N', 'n')):
                            lat = float(lat_input[:-1])
                        else:
                            lat = float(lat_input)
                        # update timezone
                        tz_name = tz_finder.timezone_at(lng=lon, lat=lat)
                        local_tz = tz(tz_name) if tz_name else tz('UTC')
                        cache_key = f"{lon:.4f},{lat:.4f}"
                        location_cache[cache_key] = local_tz
                        break
                    except ValueError:
                        print("invalid input; please use coordinates")
                elif q3 == 2:
                    try:
                        lad = input("city name (ex: Mecca): ")
                        loca = geolocator.geocode(lad)
                        lon = loca.longitude
                        lat = loca.latitude
                        tz_name = tz_finder.timezone_at(lng=lon, lat=lat)
                        local_tz = tz(tz_name) if tz_name else tz('UTC')
                        cache_key = f"{lon:.4f},{lat:.4f}"
                        location_cache[cache_key] = local_tz
                        break
                    except Exception:
                        print("invalid city name")
                else:
                    print("please choose a valid option")

            else:
                print("please answer 'y' or 'n'...")
    elif silent is True:
        silent = False
    else:
        print("you can only pass a boolean for the localization function")

    # update cache
    cache_key = f"{lon:.4f},{lat:.4f}"
    location_cache[cache_key] = local_tz
    if not silent:
        print(f"location cached: {cache_key}")
        print(f"timezone: {local_tz.zone}")
        now = dt.now(local_tz)
        print(f"local time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"UTC offset: {now.utcoffset()}")


def exec_cmd(cmd):
    '''execute given command with error handling'''
    if not cmd:
        return

    xcmd = cmd_map.get(cmd)
    if xcmd:
        try:
            xcmd()
        except Exception as e:
            print(f"error executing '{cmd}': {e}")
    else:
        print(f"command '{cmd}' not recognized. type 'help' for more info")


def main_menu():
    '''display main menu'''
    line()
    print('Main menu')
    line()
    print('loca, l - change location')
    print('help, h - print this menu to list available commands')
    print('clear, c - clear the screen')
    print('quit, q - exit the CLI')
    for s in surahs:
        print(f'{surahs[s][1]} - display {surahs[s][0]}')
    print('basmala - display the basmala')


def main():
    '''main application flow'''
    # loading('initializing', 5,  2)
    network_check()
    check_terminal_support()
    localization(silent=True)
    bsmllh(True)
    flush()
    main_menu()

    while True:
        try:
            cmd = input('>').strip().lower()
            exec_cmd(cmd)
        except KeyboardInterrupt:
            print("\ntype 'quit' to exit or type 'help' for more info")
        except Exception as e:
            print(f"unexpected error: {e}")


if __name__ == "__main__":
    # preload surahs
    surahs = {
        1: ['Surah Al-Fatihah', 'fatiha', readfile('al-fatihah.txt', quran=True)],
        2: ['Surah An-Nas', 'nas', readfile('an-nas.txt', quran=True)]
    }
    # populate command map
    cmd_map = {
        'help': main_menu,
        'h': main_menu,
        'clear': flush,
        'c': flush,
        'quit': lambda: exit(flush()),
        'q': lambda: exit(flush()),
        'exit': lambda: exit(flush()),
        'location': localization,
        'loca': localization,
        'l': localization,
        'fatiha': lambda: display_surah(1),
        'nas': lambda: display_surah(2),
        'basmala': lambda: bsmllh(True),
        'insert': lambda: eval(input('>'))
    }
    main()
