import requests


class OneInchApi():
    def get_active_orders(self):
        url = 'https://fusion.1inch.io/orders/v1.0/1/order/active/'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['items']
        else:
            print(f"Error get order status: {response.status_code}")
            print(response.json())
            return None
        
    def get_order_status(self, order_hash):
        url = 'https://fusion.1inch.io/orders/v1.0/1/order/status/'+order_hash
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error get order status: {response.status_code}")
            print(response.json())
            return None
        
class OpenOceanApi():
    def get_gas_price(self):
        url = 'https://open-api.openocean.finance/v1/1/getGasPrice'
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()['data']['gasPrice']
        return None
    
    def convert_txCost_to_quote(self, token_quote, amount, tokens):
        if token_quote == '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2':
            return amount
        base_url = 'https://open-api.openocean.finance/v1/cross/quote?'
        token_info = tokens.get_token(token_quote)
        params = {
            "inTokenAddress": '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
            "outTokenAddress": token_quote,
            "out_token_decimals": token_info.decimals,
            "amount": amount,
            "gasPrice": 5,
            "slippage": 10,
            "exChange": "openoceanv2",
            "chainId": 1
        }
        url = base_url + '&'.join([f'{k}={v}' for k, v in params.items()])
        r = requests.get(url)
        if r.status_code == 200:
            return float(r.json()['data']['outAmount'])
        print(r.json())
        return None

    def get_quote(self, token_from, token_to, amount, tokens):
        try:
            token_from_info = tokens.get_token(token_from)
            token_to_info = tokens.get_token(token_to)
            base_url = 'https://open-api.openocean.finance/v1/cross/quote?'
            params = {
                "inTokenAddress": token_from,
                "in_token_decimals": token_from_info.decimals,
                "outTokenAddress": token_to,
                "out_token_decimals": token_to_info.decimals,
                "amount": amount,
                "gasPrice": self.get_gas_price(),
                "slippage": 10,
                "exChange": "openoceanv2",
                "chainId": 1
            }
            url = base_url + '&'.join([f'{k}={v}' for k, v in params.items()])
            r = requests.get(url)
            if r.status_code == 200:
                try:
                    quote_tx_cost = self.convert_txCost_to_quote(token_to, float(r.json()['data']['transCost']), tokens)
                except:
                    print(r.json())
                result = r.json()
                result['data']['transCost'] = quote_tx_cost
                return result['data']
            else:
                print(r.json())
                return None
        except Exception as e:
            print(e)
            return None
        
    # return outAmount + transCost
    def get_quote_from_token(self, token_from, token_to, amount, tokens):
        data = self.get_quote(token_from, token_to, amount, tokens)
        if data:
            return data['outAmount'] + data['transCost']
        else:
            return None