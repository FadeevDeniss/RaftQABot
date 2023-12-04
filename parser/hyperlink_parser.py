import os

import requests

from lxml.html import document_fromstring


class HyperTextParser:
    full_url = 'https://www.promptingguide.ai'

    def __init__(self):
        self.hyperlinks = []

    def get_hyperlinks(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        if not os.path.exists('text/'):
            os.mkdir('text/')

        with requests.session() as session:
            result = session.get(url=self.full_url, headers=headers)
            a_tags = document_fromstring(result.text).xpath('//a')

            for t in a_tags:
                href = t.attrib['href']
                if href.startswith('/'):
                    self.hyperlinks.append(self.full_url + href)

    def parse_url(self):
        with requests.session() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                              ' Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;'
                          'q=0.9,image/avif,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            for url in self.hyperlinks:
                res = session.get(url=url, headers=headers)
                article = document_fromstring(res.text).xpath('//article')

                if article:
                    text = article[0].text_content()
                    with open(
                            f'text/{url[8:].replace("/", "_").replace(".", "_")}.txt',
                            'w',
                            encoding='UTF-8'
                    ) as f:
                        f.write(text)
