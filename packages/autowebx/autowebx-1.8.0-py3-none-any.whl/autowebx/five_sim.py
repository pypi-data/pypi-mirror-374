import time
import requests

DOMAIN = "5sim.net"


class Phone:
    def __init__(self, number_id, phone):
        self.id = number_id
        self.number = phone


class FiveSim:
    def __init__(self, token):
        self.headers = {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json',
        }

    def balance(self):
        response = requests.get(f'https://{DOMAIN}/v1/user/profile', headers=self.headers)
        return response.json()['balance']

    def buy_activation_number(self, country: str, operator: str, product: str):
        url = f'https://{DOMAIN}/v1/user/buy/activation/{country}/{operator}/{product}'
        response = requests.get(url, headers=self.headers).json()
        return Phone(response['id'], response['phone'][1:])

    def get_codes(self, phone: Phone, timeout: float = 30):
        start = time.time()
        while True:
            try:
                response = requests.get(f'https://{DOMAIN}/v1/user/check/{phone.id}', headers=self.headers).json()
                return [sms['code'] for sms in response['sms']]
            except (ValueError, IndexError):
                pass

            if time.time() - start > timeout:
                raise TimeoutError


def min_cost_providers(country: str, product: str):
    response = requests.get(f'https://{DOMAIN}/v1/guest/prices?country={country}&product={product}').json()
    operators0 = []
    for operator in response[country][product]:
        if response[country][product][operator]['count'] != 0:
            operators0.append(operator)
    min_cost = response[country][product][operators0[0]]['cost']
    for operator in operators0:
        if response[country][product][operator]['cost'] < min_cost:
            min_cost = response[country][product][operator]['cost']
    operators1 = []
    for operator in operators0:
        if response[country][product][operator]['cost'] == min_cost:
            operators1.append(operator)
    return operators1


if __name__ == '__main__':
    token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODcxNDA4MjUsImlhdCI6MTc1NTYwNDgyNSwicmF5IjoiNTRlMDdjMDEyZjIzYjM0ZDI2ZDE4N2RiZTFiZDgyY2MiLCJzdWIiOjE0MjMyMjR9.PIERSXfyvfN5QaGr42U74PhZtXX5EWVsNRJNcRC8iVK0DWqaJVJeAbYZDSoOrvN-dzPxPlhtR547fdfbMrDzs49b01UaXelNSOIG16XKO6-xhSn97-1JWZm9a9PRNbWAAQgmaRQPWjKpJqA0DpdRZnMtrQgrjlrChlVx3NUq9ye07N9UAJiJ9NooCD3238Np1qkCA6XYnKQp9iIfFqtigCd_BM49ewSI8weCW8qLpbPtBIaUdpMEadjS3ZHfsB0mBJbwEy_B0bOGX98llDTOlYPYVufZTXMd6T45UxDt6vllMtAMoOlUiZ6OCBtJW3UttrwR5VKlI0czgtRdrujYpQ'
    phone = FiveSim(token).buy_activation_number('netherlands', 'any', 'other')
    pass