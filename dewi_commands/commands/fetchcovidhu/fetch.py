# Copyright 2020 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import datetime
import json
import os
import typing
import urllib.request
from io import StringIO

from lxml import etree

from dewi_core.logger import log_debug


class Fetcher:
    BASE_URL = 'https://koronavirus.gov.hu'

    def __init__(self, directory: str):
        self.base_directory = directory
        self.timestamp = datetime.datetime.now()
        self.directory = self.base_directory + f'/{self.timestamp.strftime("%Y%m%d-%H%M%S-%s")}'
        self.main_stats_file = 'stats.json'
        self.main_html_file = 'Koronavírus.html'
        self.map_file = 'terkep.jpg'
        self.deceased_file = 'deceased.json'
        self.deceased_file_template = 'Elhunytak {last}-{first}.html'

    def fetch(self):
        self._prepare_directory()

        self._fetch_stats()
        self._fetch_images()
        self._fetch_deceased()

    def _prepare_directory(self):
        os.makedirs(self.directory, exist_ok=True)
        self._write_to_json(dict(
            site=self.BASE_URL,
            timestamp=self.timestamp.strftime("%Y-%m-%d %H:%M:%S %z"),
            main_stats=self.main_stats_file,
            main_html=self.main_html_file,
            map_file=self.map_file,
            deceased_file=self.deceased_file,
        ), 'info.json')

    def _fetch_stats(self):
        raw_page = self._fetch_to_file(f'{self.BASE_URL}/', self.main_html_file).decode('UTF-8')
        self._gen_stats(raw_page)

    def _fetch_images(self):
        raw_page = self._fetch_url(f'{self.BASE_URL}/terkepek/fertozottek/').decode('UTF-8')
        parser = etree.HTMLParser()
        root = etree.parse(StringIO(raw_page), parser)
        imgs = root.xpath("//div[contains(@class, 'views-field-field-terkepek-image')]//img")
        terkep = None
        for img in imgs:
            if terkep is None:
                terkep = img.attrib['src']

            src = img.attrib['src']

            filename = os.path.basename(src)

            self._fetch_image(src, filename)

        self._fetch_image(terkep, self.map_file)

    def _gen_stats(self, raw_page: str):
        parser = etree.HTMLParser()
        root = etree.parse(StringIO(raw_page), parser)
        fields = root.xpath("//div[starts-with(@id,'api-')]")

        result = dict()
        for field in fields:
            result[field.attrib['id'].replace('api-', '')] = int(field.text.replace(' ', ''))

        result['local-timestamp'] = self._parse_date('Magyarorsz', root)
        result['global-timestamp'] = self._parse_date('A vil', root)

        self._write_to_json(result, self.main_stats_file)

    def _parse_date(self, h2_prefix: str, root) -> str:
        p = root.xpath(f"//h2[starts-with(text(),'{h2_prefix}')]/../p")
        dt = datetime.datetime.strptime(p[0].text.split(':', 1)[1].strip(), '%Y.%m.%d. %H:%M')
        return dt.strftime("%Y-%m-%d %H:%M")

    def _fetch_deceased(self):
        entries = []
        first = 0
        page = 0

        while first != 1:
            first = self._fetch_deceased_nth(page, entries)
            page += 1

        self._write_to_json(entries, self.deceased_file)

    def _fetch_deceased_nth(self, n: int, entries: list) -> int:
        log_debug('Fetching deceased pages', dict(page_idx=n))
        suffix = '' if n < 1 else f'?page={n}'

        raw_page = self._fetch_url(f'{self.BASE_URL}/elhunytak/{suffix}').decode('UTF-8')
        parser = etree.HTMLParser()
        root = etree.parse(StringIO(raw_page), parser)
        rows = root.xpath("//tr[contains(@class, 'odd') or contains(@class, 'even')]")

        first, last = 0, 0

        for row in rows:
            index, gender, age, deseases = row[0].text, row[1].text, row[2].text, row[3].text
            data = dict(index=int(index.strip()), gender=gender.strip(), age=int(age.strip()))

            data['deseases'] = [x.strip() for x in deseases.split(',')]

            entries.append(data)

            if not last:
                last = data['index']

            first = data['index']

        with open(os.path.join(self.directory, self.deceased_file_template.format(first=first, last=last)), 'wt',
                  encoding='UTF-8') as f:
            f.write(raw_page)

        return first

    def _fetch_image(self, src: str, filename: str):
        self._fetch_to_file(src, filename)

    def _fetch_to_file(self, src: str, filename: str) -> bytes:
        content = self._fetch_url(src)
        with open(os.path.join(self.directory, filename), 'wb') as f:
            f.write(content)

        return content

    def _fetch_url(self, url: str) -> bytes:
        with urllib.request.urlopen(url) as response:
            return response.read()

    def _write_to_json(self, data: typing.Union[dict, list], filename: str):
        with open(f'{self.directory}/{filename}', 'wt', encoding='UTF-8') as f:
            json.dump(data, f, indent=2)
