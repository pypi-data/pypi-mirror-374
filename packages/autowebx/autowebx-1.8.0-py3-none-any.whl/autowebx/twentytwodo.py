from typing import Optional

from bs4 import BeautifulSoup
from requests import post

BASE_URL = 'https://22.do/api/v2'


class PurchaseError(Exception):
    pass


class EmailGenerationError(Exception):
    pass


class InboxRetrievalError(Exception):
    pass


class TwentyTwoDo:
    def __init__(self, api_token):
        response = post(BASE_URL + '/token', json={'token': api_token}).json()
        if response['code'] == 200:
            self.__headers = {'Authorization': f'Bearer {response['data']['Bearer']}'}
        else:
            raise PermissionError(response['msg'])

    class Message:
        def __init__(self, message_id: str, headers: dict):
            response = post(BASE_URL + '/inbox/message', json={'messageId': message_id}, headers=headers).json()
            if response['code'] == 200:
                self.subject = response['data']['subject']
                self.body = response['data']['body']
                self.html = BeautifulSoup(response['data']['html'], 'html.parser')
                self.sender = response['data']['from']


    def generate_gmail(self):
        response = post(BASE_URL + '/gmail/purchase', json={'number': 1}, headers=self.__headers).json()
        if response['code'] == 200:
            response = post(BASE_URL + '/gmail/generate', json={
                'number': 1,
                'plus': False,
                'gmailId': response['data']['items'][0]
            }, headers=self.__headers).json()
            if response['code'] == 200:
                return f'{response['data']['items'][0]}@gmail.com'
            else:
                raise EmailGenerationError(response['msg'])
        else:
            raise PurchaseError(response['msg'])



    def inbox(self, email: str, time: Optional[int] = None):
        response = post(BASE_URL + '/gmail/inbox', json={'email': email, 'time': time}, headers=self.__headers).json()
        if response['code'] == 200:
            return [self.Message(message['messageId'], self.__headers) for message in response['data']]
        else:
            raise InboxRetrievalError(response['msg'])

    def gmail(self, page: int = 1, limit: int = 100):
        response = post(BASE_URL + '/gmail', json={'page': page, 'limit': limit}, headers=self.__headers).json()
        if response['code'] == 200:
            open('../emails.txt', 'w').write('\n'.join(f'{item}@gmail.com\n{item}@googlemail.com' for item in response['data']['items']))


if __name__ == '__main__':
    # co.sta.bales.uv.ah.ohya66@gmail.com
    # Hazem3010..
    inbox = TwentyTwoDo('179942273717c7d40ce8be256c7a1b62').inbox('cooks.sto.dden796@gmail.com')
    pass    # 891643
