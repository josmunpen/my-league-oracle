import pandas as pd
import datetime
import logging



class APILimitHandler():

    def __init__(self):
        self.today_format = datetime.datetime.today().strftime("%Y%m%d")
        self.requests_file = "./config/requests.csv"
        self.log = logging.getLogger(__name__)                                  
        # self.log.setLevel(logging.INFO)   
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    # @property
    # def today_format(self):
    #     return self._today_format
    
    # @property
    # def requests_file(self):
    #     return self._requests_file

    def get_current_requests(self, df):
        num_req = df[df['date'] == self.today_format]['num_requests']

        return num_req.values[0]

    def set_request(self, df):
        num_req = df[df['date'] == self.today_format]['num_requests']
        df.loc[df['date'] == self.today_format, 'num_requests'] = num_req + 1

        df.to_csv(self.requests_file, sep=";")

        return num_req+1

    def check_requests(self):
        df = pd.read_csv(self.requests_file, sep=";", dtype={"date":str, "num_requests": int}, index_col="index")

        num_req = self.get_current_requests(df)
        res = False
        if num_req < 100:
            self.log.info(f"Num of requests is {num_req}")
            new_num_req = self.set_request(df)
            return True
        else:
            self.log.warning(f"!!!!! NUMBER OF REQUESTS EXCEEDED ({num_req}) !!!!!")
            return False

if __name__ == "__main__":
    api_limit = APILimitHandler()
    api_limit.check_requests()