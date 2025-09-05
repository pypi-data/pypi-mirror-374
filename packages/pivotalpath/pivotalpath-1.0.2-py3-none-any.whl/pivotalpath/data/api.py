
import pandas as pd
import warnings
import requests

class ApiCaller:
    
    base_url = "http://apps.pivotalpath.com/p3ypi/resources/api/v1/"
    api_key = "p3k_7H9mK2pL8qX3nR5vW1cY4jZ6sA0uE9"
    
    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.api_key}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def get_data(cls,endpoint=None,params=dict()):
        url=cls.base_url+endpoint
        headers=cls.get_headers()
        response=requests.get(url,headers=headers,params=params)
        if response.status_code==200:
            try:
                return pd.DataFrame(response.json())
            except ValueError:
                warnings.warn("Failed to parse JSON response")
                return pd.DataFrame()
        else:
            warnings.warn(f"API call failed with status code {response.status_code}")
            return pd.DataFrame()


def GetFilteredDataFrame(table_name=None, filter_by=dict())->pd.DataFrame:
    return ApiCaller.get_data(endpoint=table_name,params=filter_by)
