import pandas as pd
import datetime
import logging
from functools import wraps
import sqlite3

log = logging.getLogger(__name__)                                  
# log.setLevel(logging.INFO)   
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def get_current_requests(df, today_format, requests_file):
    num_req = df[df.date == today_format]['num_requests']


    if num_req.empty:
        log.info(f"First call of the day :)")
        num_req = 1
        new_row = pd.DataFrame([{"num_requests": num_req, "date": today_format}])
        df = pd.concat([df, new_row])
        # df.to_csv(requests_file, sep=";")
        with sqlite3.connect('soccer.db') as conn:
            df.to_sql(name="requests", con=conn, if_exists="replace", index=False)
    else:
        num_req = num_req.values[0]

    
    return num_req

def set_request(df, today_format, requests_file):
    num_req = df[df.date == today_format]['num_requests']
    
    df.loc[df.date == today_format, 'num_requests'] = num_req + 1

    # df.to_csv(requests_file, sep=";")

    with sqlite3.connect('soccer.db') as conn:
        df.to_sql(name="requests", con=conn, if_exists="replace", index=False)

    return num_req+1

def check_requests2(func):

    @wraps(func)
    def wrapper_check_req(*args, **kwargs):
        today_format = datetime.datetime.today().strftime("%Y%m%d")
        requests_file = "./config/requests.csv"

        # df = pd.read_csv(requests_file, sep=";", dtype={"date":str, "num_requests": int}, index_col="index")
        
        with sqlite3.connect('soccer.db') as conn:
            df = pd.read_sql("""
                        SELECT *
                        FROM requests
                        """, con=conn)
            
        num_req = get_current_requests(df, today_format, requests_file)
        res = False

        if num_req < 100:
            log.info(f" === Number of requests is {num_req}")
            new_num_req = set_request(df, today_format, requests_file)
        else:
            log.warning(f"!!!!! NUMBER OF REQUESTS EXCEEDED ({num_req}) !!!!!")
        func(*args, **kwargs)

    return wrapper_check_req


def check_requests(func):

    @wraps(func)
    def wrapper_check_req(*args, **kwargs):
        today = datetime.datetime.today()

        with sqlite3.connect('soccer.db') as conn:
            df = pd.read_sql(f"""
                        SELECT *
                        FROM requests
                        WHERE DATE(requests.date) = DATE("{today}")
                        """, con=conn)
        
        # First call of the day
        if df.empty:  
            log.info(f"First call of the day :)")
            updated_num_req = 0
        else:
            updated_num_req = df["num_requests"].values[0]

        log.info(f" === Today we made {updated_num_req} requests")

        # If number of requests exceeded limit, raise exception
        if updated_num_req < 100:
            updated_num_req = updated_num_req + 1
            new_row = pd.DataFrame(data={"date": [today],"num_requests": [updated_num_req]})

            with sqlite3.connect('soccer.db') as conn:
                new_row.to_sql(name="requests", con=conn, if_exists="replace", index=False)

        # Else (more than 100 requests today), raise exception
        else:
            log.info(f" !!!!! Reached requests limit by day !!!!!")
            raise Exception("Reached requests limit by day")

        func(*args, **kwargs)

    return wrapper_check_req



@check_requests
def prueba(a):
    print('holi')
    print(a)

class ApiCaller():

    def __init__(self, url, headers):
        self._url = url
        self._headers = headers

    @property
    def url(self):
        return self._url

    @property
    def headers(self):
        return self._headers

    @check_requests
    def prueba(self):
        print('holi')