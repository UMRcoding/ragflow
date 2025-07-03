import json
from abc import ABC
import pandas as pd
import requests
from agent.component.base import ComponentBase, ComponentParamBase


class Jin10Param(ComponentParamBase):
    """
    Define the Jin10 component parameters.
    """

    def __init__(self):
        super().__init__()
        self.type = "flash"
        self.secret_key = "xxx"
        self.flash_type = '1'
        self.calendar_type = 'cj'
        self.calendar_datatype = 'data'
        self.symbols_type = 'GOODS'
        self.symbols_datatype = 'symbols'
        self.contain = ""
        self.filter = ""

    def check(self):
        self.check_valid_value(self.type, "Type", ['flash', 'calendar', 'symbols', 'news'])
        self.check_valid_value(self.flash_type, "Flash Type", ['1', '2', '3', '4', '5'])
        self.check_valid_value(self.calendar_type, "Calendar Type", ['cj', 'qh', 'hk', 'us'])
        self.check_valid_value(self.calendar_datatype, "Calendar DataType", ['data', 'event', 'holiday'])
        self.check_valid_value(self.symbols_type, "Symbols Type", ['GOODS', 'FOREX', 'FUTURE', 'CRYPTO'])
        self.check_valid_value(self.symbols_datatype, 'Symbols DataType', ['symbols', 'quotes'])


class Jin10(ComponentBase, ABC):
    component_name = "Jin10"

    def _run(self, history, **kwargs):
        ans = self.get_input()
        ans = " - ".join(ans["content"]) if "content" in ans else ""
        if not ans:
            return Jin10.be_output("")

        jin10_res = []
        headers = {'secret-key': self._param.secret_key}
        try:
            if self._param.type == "flash":
                params = {
                    'category': self._param.flash_type,
                    'contain': self._param.contain,
                    'filter': self._param.filter
                }
                response = requests.get(
                    url='https://open-data-api.jin10.com/data-api/flash?category=' + self._param.flash_type,
                    headers=headers, data=json.dumps(params))
                response = response.json()
                for i in response['data']:
                    jin10_res.append({"content": i['data']['content']})
            if self._param.type == "calendar":
                params = {
                    'category': self._param.calendar_type
                }
                response = requests.get(
                    url='https://open-data-api.jin10.com/data-api/calendar/' + self._param.calendar_datatype + '?category=' + self._param.calendar_type,
                    headers=headers, data=json.dumps(params))

                response = response.json()
                jin10_res.append({"content": pd.DataFrame(response['data']).to_markdown()})
            if self._param.type == "symbols":
                params = {
                    'type': self._param.symbols_type
                }
                if self._param.symbols_datatype == "quotes":
                    params['codes'] = 'BTCUSD'
                response = requests.get(
                    url='https://open-data-api.jin10.com/data-api/' + self._param.symbols_datatype + '?type=' + self._param.symbols_type,
                    headers=headers, data=json.dumps(params))
                response = response.json()
                if self._param.symbols_datatype == "symbols":
                    for i in response['data']:
                        i['Commodity Code'] = i['c']
                        i['Stock Exchange'] = i['e']
                        i['Commodity Name'] = i['n']
                        i['Commodity Type'] = i['t']
                        del i['c'], i['e'], i['n'], i['t']
                if self._param.symbols_datatype == "quotes":
                    for i in response['data']:
                        i['Selling Price'] = i['a']
                        i['Buying Price'] = i['b']
                        i['Commodity Code'] = i['c']
                        i['Stock Exchange'] = i['e']
                        i['Highest Price'] = i['h']
                        i['Yesterday’s Closing Price'] = i['hc']
                        i['Lowest Price'] = i['l']
                        i['Opening Price'] = i['o']
                        i['Latest Price'] = i['p']
                        i['Market Quote Time'] = i['t']
                        del i['a'], i['b'], i['c'], i['e'], i['h'], i['hc'], i['l'], i['o'], i['p'], i['t']
                jin10_res.append({"content": pd.DataFrame(response['data']).to_markdown()})
            if self._param.type == "news":
                params = {
                    'contain': self._param.contain,
                    'filter': self._param.filter
                }
                response = requests.get(
                    url='https://open-data-api.jin10.com/data-api/news',
                    headers=headers, data=json.dumps(params))
                response = response.json()
                jin10_res.append({"content": pd.DataFrame(response['data']).to_markdown()})
        except Exception as e:
            return Jin10.be_output("**ERROR**: " + str(e))

        if not jin10_res:
            return Jin10.be_output("")

        return pd.DataFrame(jin10_res)
