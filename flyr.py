from urllib.request import urlopen
import datetime
import random
import re
import requests
import json 
import copy
import codecs
from workdays import *
from travel import *
min_travel_days = 3
max_travel_days = 7
max_price = 2000
class Flyr:
    def __init__(self):
        self.API_URL = 'https://flyr.com/api/flyr/'
        self.PAYLOAD = 'fares/promotions?currency=NOK&origin=OSL&onlyDirectFlights=true&destination=AHO%2CALC%2CATH%2CBCN%2CBGO%2CBER%2CBLL%2CBOO%2CBRU%2CDBV%2CEDI%2CFAO%2CLPA%2CEVE%2CIBZ%2CCPH%2CKSU%2CMAD%2CAGP%2CPMI%2CMPL%2CNAP%2CNCE%2COSL%2CPMO%2CCDG%2CPSA%2COPO%2CPRG%2CFCO%2CSVG%2CARN%2CSKG%2CTOS%2CTRD%2CVLC%2CVCE%2CZAD'
        self.FLIGHT_SEARCH = 'fares?currency=NOK&origin=XXX&destination=YYY&adults=1&infants=0&children=0&onlyDirectFlights=false'
        self.depart = []
        self.des = []
        self.search = ''
        self.search_results = []
        print('flyr created')
    
    def find_all_des_from_depart(self,depart):
        payload = self.PAYLOAD.replace('OSL', depart)
        print(payload)
        html = requests.get(self.API_URL + payload)
        print(html.content)
        json_data = json.loads(html.content)
        destinations_list = json_data.get('destinations')
        for des in destinations_list:
            self.des.append(des['destination'])
        print(self.des)

    def collect_flights_data(self,depart,des):
        out_bound_flights = []
        payload = self.FLIGHT_SEARCH.replace('XXX', depart).replace('YYY',des)
        html = requests.get(self.API_URL + payload)
        print(html.content)
        json_data = json.loads(html.content)
        f_list = json_data.get('fares')
        for f in f_list:
            #sometime price is not a int but a fault, must ignore this
            if isinstance(f['lowestFare'], int):                         
                flight = Flight(datetime.datetime.strptime(f['date'],"%Y-%m-%d"),f['lowestFare'],depart,des)
                print(flight.display())
                out_bound_flights.append(flight)
        return out_bound_flights

def Iterate_flights(out_flights_list,in_flights_list):
    travel_list = []
    for out_flight in out_flights_list:
        for in_flight in in_flights_list:
            #find all possible flights
            travel_filter(in_flight, out_flight,travel_list)
    return travel_list

def travel_filter(in_flight, out_flight,a_list):    
    travel_days=(in_flight.date.date() - out_flight.date.date()).days + 1
    work_day = WorkDays(out_flight.date.date(),in_flight.date.date())   
    if travel_days>= min_travel_days and travel_days <= max_travel_days and in_flight.price+out_flight.price <= max_price and travel_days > work_day.daysCount():
        #generate a travel
        travel = Travel(out_flight,in_flight,in_flight.price+out_flight.price,travel_days, work_day.daysCount())
        a_list.append(travel)

depart = 'SVG'
travels = []
flyr = Flyr()
flyr.find_all_des_from_depart(depart)
for des in flyr.des:
    a = flyr.collect_flights_data(depart,des)
    b = flyr.collect_flights_data(des,depart)
    travels = travels + Iterate_flights(a,b)


a_list = list(set(travels))

a_list.sort(key=lambda x:(x.price,x.work_days))

f=codecs.open('flyr scraping '+ depart + datetime.datetime.now().strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8')

for travel in a_list:
    print(travel.display('en')) 
    f.write(travel.display()+'\n')
f.close()
    
