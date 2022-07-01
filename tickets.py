from urllib.request import urlopen
import datetime
import random
import re
import requests
import json 
import copy
import codecs

#payload={"flightList":[{"departureStation":"SVG","arrivalStation":"GDN","from":"2022-07-01","to":"2022-08-01"},{"departureStation":"GDN","arrivalStation":"SVG","from":"2022-08-01","to":"2022-09-01"}],"priceType":"wdc","adultCount":1,"childCount":0,"infantCount":0}
# payload={'flightList':[{"departureStation": "SVG", "arrivalStation": "GDN", "from": "2022-07-01", "to": "2022-08-01"}], 'priceType': 'wdc', 'adultCount': 1, 'childCount': 0, 'infantCount': 0}
wizz_payload={'flightList':[], 'priceType': 'wdc', 'adultCount': 1, 'childCount': 0, 'infantCount': 0}
wizz_url = "https://be.wizzair.com/12.10.0/Api/search/timetable"
outboundflights = []
inboundflights = []
des_ports = ['KTW','SZZ','KRK','GDN','KUN']
depart_ports = ['SVG']
travel_list = []
min_travel_days = 3
max_travel_days = 7
max_price = 800
class workDays():
    def __init__(self, start_date, end_date, days_off=None):
        """days_off:休息日,默认周六日, 以0(星期一)开始,到6(星期天)结束, 传入tupple
        没有包含法定节假日,
        """
        self.start_date = start_date
        self.end_date = end_date
        self.days_off = days_off
        if self.start_date > self.end_date:
            self.start_date,self.end_date = self.end_date, self.start_date
        if days_off is None:
            self.days_off = 5,6
        # 每周工作日列表
        self.days_work = [x for x in range(7) if x not in self.days_off]
 
    def workDays(self):
        """实现工作日的 iter, 从start_date 到 end_date , 如果在工作日内,yield 日期
        """
        # 还没排除法定节假日
        tag_date = self.start_date
        while True:
            if tag_date > self.end_date:
                break
            if tag_date.weekday() in self.days_work:
                yield tag_date
            tag_date += datetime.timedelta(days=1)
 
    def daysCount(self):
        """工作日统计,返回数字"""
        return len(list(self.workDays()))
 
    def weeksCount(self, day_start=0):
        """统计所有跨越的周数,返回数字
        默认周从星期一开始计算
        """
        day_nextweek = self.start_date
        while True:
            if day_nextweek.weekday() == day_start:
                break
            day_nextweek += datetime.timedelta(days=1)
        # 区间在一周内
        if day_nextweek > self.end_date:
            return 1
        weeks = ((self.end_date - day_nextweek).days + 1)/7
        weeks = int(weeks)
        if ((self.end_date - day_nextweek).days + 1)%7:
            weeks += 1
        if self.start_date < day_nextweek:
            weeks += 1
        return weeks
class Travel:
    def __init__(self, out_bound_flight, in_bound_flight, price, days, work_days):
        self.out_bound_flight = out_bound_flight
        self.in_bound_flight = in_bound_flight
        self.price = price
        self.days = days
        self.work_days = work_days
    def display(self, lan = ''):
        if lan == 'en':
             return ('Departure date :' + str(self.out_bound_flight.date) +'  '+ self.out_bound_flight.date.strftime("%A").ljust(9)        
        +'  Return home date : ' + str(self.in_bound_flight.date) + '  '+ self.in_bound_flight.date.strftime("%A").ljust(9)
        +'  Departure airport : ' + self.out_bound_flight.dep_port        
        +'  Return airport : ' + self.in_bound_flight.dep_port   
        +'  Price (NOK): ' + str(round(self.price,2))    
        +'  overall days: ' + str(self.days) 
        +'  overall working days: ' + str(self.work_days))  
        else :
            return ('出发日期： ' + str(self.out_bound_flight.date) +'  '+ self.out_bound_flight.date.strftime("%A").ljust(9)        
        +'  回家日期： ' + str(self.in_bound_flight.date) + '  '+ self.in_bound_flight.date.strftime("%A").ljust(9)
        +'  出发机场: ' + self.out_bound_flight.dep_port        
        +'  返回机场: ' + self.in_bound_flight.dep_port   
        +'  总价(NOK): ' + str(round(self.price,2))    
        +'  总天数: ' + str(self.days) 
        +'  工作日天数: ' + str(self.work_days))  
    def __eq__(self, other):
        print(self.__dict__)
        print(other.__dict__)
        return self.out_bound_flight.dep_port == other.out_bound_flight.dep_port  and \
        self.in_bound_flight.dep_port == other.in_bound_flight.dep_port  and \
        self.out_bound_flight.date == other.out_bound_flight.date  and \
        self.in_bound_flight.date == other.in_bound_flight.date

    def __hash__(self):
        return hash((self.out_bound_flight.dep_port,self.in_bound_flight.dep_port, self.out_bound_flight.date,self.in_bound_flight.date))
class Flight:   
    def __init__(self, date, price, dep_port, des_port):
        self.date = date
        self.price = price
        self.dep_port = dep_port
        self.des_port = des_port
    def display(self):
        print(self.date)        
        print(self.price)
        print(self.dep_port)
        print(self.des_port)

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
    work_day = workDays(out_flight.date.date(),in_flight.date.date())   
    if travel_days>= min_travel_days and travel_days <= max_travel_days and in_flight.price+out_flight.price <= max_price and travel_days > work_day.daysCount():
        #generate a travel
        travel = Travel(out_flight,in_flight,in_flight.price+out_flight.price,travel_days, work_day.daysCount())
        travel_list.append(travel)

def collect_flights_data(depart,arrival,start_year,start_month,length = 12):
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

            a,b =collect_flights_data(depart,des,2022,7)

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