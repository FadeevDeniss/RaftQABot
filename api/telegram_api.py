import aiohttp


class TelegramAPI:
    _telegram_base_url = 'https://api.telegram.org'

    def __init__(self, token):
        self._token = token

    async def get_updates(self, offset=None, timeout=0):
        params = {}

        if offset:
            params['offset'] = offset
        if timeout:
            params['timeout'] = timeout

        return await self.send_request(api_method='getUpdates', params=params)

    async def send_message(self, chat_id, message):
        json_body = {
            'chat_id': chat_id,
            'text': message
        }
        return await self.send_request('sendMessage', json=json_body)

    async def send_request(self, api_method, switch_url=False, **kwargs) -> dict:

        url = f"{self._telegram_base_url}/bot{self._token}/{api_method}"

        method = 'POST' if 'json' in kwargs or 'data' in kwargs else 'GET'

        json_body = kwargs.get('json')
        params = kwargs.get('params')

        async with aiohttp.ClientSession() as session:
            async with session.request(url=url, method=method, json=json_body, params=params) as response:
                return await response.json()





