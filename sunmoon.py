"""
autor: Alex Olivier Michaud
Zobrazí informace o Slunci a o Měsíci v daný den v daném městě v České republice. Používám API AA USNO pro získání informací o Slunci a Měsíci.
Součástí je databáze se souřadnicemi měst v ČR. Data jsou získána z https://github.com/33bcdd/souradnice-mest/blob/master/souradnice.csv
"""

import datetime
from urllib.request import urlopen
from json import loads
import time
from sqlite3 import connect
import pprint

def iter_paths(d):
    def iter1(d, path):
        paths = []
        for k, v in d.items():
            if isinstance(v, dict):
                paths += iter1(v, path + [k])
            paths.append((path + [k], v))
        return paths
    return iter1(d, [])

def get_coordinates(city):
    conn = connect("souradnice_mest.db")
    c = conn.cursor()
    c.execute(f"SELECT Latitude, Longitude FROM mesta WHERE Obec = '{city}'")
    return c.fetchone()

if __name__ == "__main__":
    while True:
        user_city = input("Zadejte město: ")
        user_time = input("Zadejte čas ve formátu DD:MM:YYYY : ")
        if user_city == None:
            print("Nezadal jste město")
        else:
            souradnice = get_coordinates(user_city)
            if souradnice == None:
                print("Neznámé město")
                continue
            if user_time == None:
                print("Nezadal jste čas")
                continue
            if user_time == "now":
                today = datetime.datetime.now()
                datum = today.day, today.month, today.year
            if user_time != "now":
                datum = user_time.split(":")
                datum = int(datum[0]), int(datum[1]), int(datum[2])


            casova_zona = 1
            dotaz_v_url = "date=%04d-%02d-%02d&coords=%5.2f,%5.2f&tz=%d&dst=true" % (
                datum[2], datum[1], datum[0],
                souradnice[0], souradnice[1],
                casova_zona
            )
            url = "https://aa.usno.navy.mil/api/rstt/oneday?" + str(dotaz_v_url)
            odpoved = urlopen(url)
            odpoved = loads(odpoved.read())
            #Slunce
            BeginCivilTwilight = odpoved["properties"]["data"]["sundata"][0]["time"]
            Rise = odpoved["properties"]["data"]["sundata"][1]["time"]
            UpperTransit = odpoved["properties"]["data"]["sundata"][2]["time"]
            Set = odpoved["properties"]["data"]["sundata"][3]["time"]
            EndCivilTwilight = odpoved["properties"]["data"]["sundata"][4]["time"]
            #Měsíc
            MoonUpperTransit = odpoved["properties"]["data"]["moondata"][0]["time"]
            Moonset = odpoved["properties"]["data"]["moondata"][1]["time"]
            print("#################################################")
            print("data o Slunci")
            print("Začátek civilního svitu: ", BeginCivilTwilight)
            print("Východ slunce: ", Rise)
            print("Nejvyšší bod slunce: ", UpperTransit)
            print("Západ slunce: ", Set)
            print("Konec civilního svitu: ", EndCivilTwilight)
            print("#################################################")
            print("data o Měsíci")
            print("Nejvyšší bod Měsíce: ", MoonUpperTransit)
            print("Západ Měsíce: ", Moonset)
            #pprint.pprint(iter_paths(odpoved))    # pro lepší orientaci v odpovědi

