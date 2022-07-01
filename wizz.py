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

#payload={"flightList":[{"departureStation":"SVG","arrivalStation":"GDN","from":"2022-07-01","to":"2022-08-01"},{"departureStation":"GDN","arrivalStation":"SVG","from":"2022-08-01","to":"2022-09-01"}],"priceType":"wdc","adultCount":1,"childCount":0,"infantCount":0}
# payload={'flightList':[{"departureStation": "SVG", "arrivalStation": "GDN", "from": "2022-07-01", "to": "2022-08-01"}], 'priceType': 'wdc', 'adultCount': 1, 'childCount': 0, 'infantCount': 0}
wizz_payload={'flightList':[], 'priceType': 'wdc', 'adultCount': 1, 'childCount': 0, 'infantCount': 0}
wizz_url = "https://be.wizzair.com/12.11.2/Api/search/timetable"
outboundflights = []
inboundflights = []
des_ports = ['KTW','SZZ','KRK','GDN','KUN']
depart_ports = ['SVG']
travel_list = []
min_travel_days = 3
max_travel_days = 7
max_price = 800

def flight_json_obj_creator(depart, arrival,start_date,end_date):
    flight = {}
    flight['departureStation'] = depart
    flight['arrivalStation']   = arrival
    flight['from'] = start_date
    flight['to'] = end_date
    return flight

def date_creator_from_month(year,month):
    start_date = ''
    start_date = str(year) + '-' + str(month) + '-01'
    if month == 12:
        end_date = str(year+1) + '-' + '01' + '-01'
    else:        
        end_date = str(year) + '-' + str (month+1) + '-01'
    return start_date, end_date

def getLinks(url,payload):
    out_flight_list = []
    return_flight_list = []
    html = requests.post(url,json = payload)
    print(html.content)
    # bs = BeautifulSoup(html.content, 'html.parser')
    # print(bs) 
    json_data = json.loads(html.content)
    out_flights = json_data.get('outboundFlights')
    return_flights = json_data.get('returnFlights')
    print('outbound flights',json_data.get('outboundFlights'))

    for flight in out_flights:
        if flight['priceType'] == 'price':  #some price type is 'checkprice', should be ignored
            print(flight['departureStation'] , flight['arrivalStation'] , flight['price'] , flight['departureDates'])
            out_flight_list.append(Flight(datetime.datetime.strptime(flight['departureDates'][0],"%Y-%m-%dT%H:%M:%S"),currency_change(flight['price']),flight['departureStation'],flight['arrivalStation']))

    for flight in return_flights:
        if flight['priceType'] == 'price':
            print(flight['departureStation'] , flight['arrivalStation'] , flight['price'] , flight['departureDates'])
            return_flight_list.append(Flight(datetime.datetime.strptime(flight['departureDates'][0],"%Y-%m-%dT%H:%M:%S"),currency_change(flight['price']),flight['departureStation'],flight['arrivalStation']))    
    return out_flight_list,return_flight_list    

# start_date,end_date=date_creator_from_month(2023,3)
# print(date_creator_from_month(2023,3))

# # data = flight_json_obj_creator('SVG','GDN','2022-07-01','2022-08-01')
# data = flight_json_obj_creator('SVG','GDN',start_date, end_date)
# print(data)
# payload['flightList'].append(data)
# print(payload)
# getLinks(wizz_url,payload)   
# for flight in outboundflights:
#     flight.display()
# getLinks(wizz_url,payload)
# 
#change current to NOK
def currency_change(price):
    currency = {
        'NOK' : 1 ,
        'PLN' : 2.2
    }
    return  price['amount'] * currency.get(price['currencyCode'],0)

def Iterate_flights(out_flights_list,in_flights_list):
    for out_flight in out_flights_list:
        for in_flight in in_flights_list:
            #find all possible flights
            travel_filter(in_flight, out_flight)

def travel_filter(in_flight, out_flight):

    travel_days=(in_flight.date.date() - out_flight.date.date()).days + 1
    work_day = WorkDays(out_flight.date.date(),in_flight.date.date())   
    if travel_days>= min_travel_days and travel_days <= max_travel_days and in_flight.price+out_flight.price <= max_price and travel_days > work_day.daysCount():
        #generate a travel
        travel = Travel(out_flight,in_flight,in_flight.price+out_flight.price,travel_days, work_day.daysCount())
        travel_list.append(travel)

def collect_flights_data(depart,arrival,start_year=datetime.date.today().year,start_month=datetime.date.today().month,length = 12):
    out_flight_list = []
    return_flight_list = []
    year = start_year
    month = start_month
    out_payload = copy.deepcopy(wizz_payload)
    return_payload = copy.deepcopy(wizz_payload)
    out_payload['flightList'].extend(('',''))
    for i in range(length):
        if month > 12:
            month = 1
            year = year + 1
        start,end = date_creator_from_month(year,month)
        o_data = flight_json_obj_creator(depart,arrival,start,end)
        r_data = flight_json_obj_creator(arrival,depart,start,end)
        out_payload['flightList'][0] = o_data
        out_payload['flightList'][1] = r_data
        print(out_payload)
        o_list,r_list = getLinks(wizz_url,out_payload)
        if(not o_list and not r_list):
            break
        out_flight_list = out_flight_list + o_list
        return_flight_list = return_flight_list + r_list
        month = month + 1

    return out_flight_list, return_flight_list


def main():
    for depart in depart_ports:
        for des in des_ports:

            a,b =collect_flights_data(depart,des)

            Iterate_flights(a,b)
            
    print(len(travel_list))        
    a_list = list(set(travel_list))

    a_list.sort(key=lambda x:(x.price,x.work_days))

    f=codecs.open('wizzair'+datetime.datetime.now().strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8')

    for travel in a_list:
        print(travel.display('en')) 
        f.write(travel.display()+'\n')
    f.close()
if __name__ == "__main__":
        debug = 0
        main()    