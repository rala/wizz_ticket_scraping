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

class JointTravels:
    def __init__(self, travel1, travel2):
        self.travels = [travel1,travel2]
    def display(self):
        return (self.travels[0].out_bound_flight.dep_port + '-->' + self.travels[0].out_bound_flight.des_port  
        +'   date :' + self.travels[0].out_bound_flight.date.strftime("%A").ljust(9) 
        +self.travels[1].out_bound_flight.dep_port + '-->' + self.travels[1].out_bound_flight.des_port 
        +'   date :' + self.travels[1].out_bound_flight.date.strftime("%A").ljust(9) 
        +self.travels[1].in_bound_flight.dep_port + '-->'  +self.travels[1].in_bound_flight.des_port  
        +'   date :' + self.travels[0].out_bound_flight.date.strftime("%A").ljust(9) 
        +self.travels[0].in_bound_flight.dep_port + '-->' +self.travels[0].in_bound_flight.des_port 
        +'   date :' + self.travels[0].in_bound_flight.date.strftime("%A").ljust(9) 
        +'   total price (NOK) : ' + str(round(self.travels[0].price + self.travels[1].price,2))      
        #+'   overall days  :' +self.travels[0].days + self.travels[1].days
        )
        # return (self.travels[0].display() \
                # + self.travels[1].display())