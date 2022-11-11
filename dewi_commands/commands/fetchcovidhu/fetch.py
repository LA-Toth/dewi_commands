# Copyright 2020-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections.abc
import datetime
import json
import os
import time
import urllib.request
from io import StringIO

import urllib3
from lxml import etree

from dewi_core.logger import log_debug, log_info


class UrlFetcher:
    def __init__(self, *, limit: int, sleep_time: float):
        self.limit = limit
        self.current = 0
        self.sleep_time = sleep_time

    def fetch(self, url: str) -> bytes:
        try:
            with urllib.request.urlopen(url) as response:
                return response.read()
        finally:
            if self.limit:
                self.current += 1

                if self.current >= self.limit:
                    self.current = 0
                    time.sleep(self.sleep_time)

    def fetch_to_file(self, src: str, filename: str) -> bytes:
        content = self.fetch(src)
        with open(filename, 'wb') as f:
            f.write(content)

        return content


class _HistoricalMainPageParser:
    NO_DETAILS = 1
    DECEASED_ADDED_ONLY = 2
    DETAILS_BP_WITH_PEST = 3
    DETAILS_BP_ONLY = 4
    LATEST = 5

    def __init__(self):

        def parse(self, *, historical: bool = False) -> int:
            if historical:
                mode = self.NO_DETAILS
            else:
                mode = self.LATEST

            if mode == self.LATEST:
                pass


class _Fetcher:
    BASE_URL = 'https://koronavirus.gov.hu'

    def __init__(self, directory: str, timestamp: datetime.datetime | None = None, *,
                 historical_mode: bool = False,
                 url: str | None = None):
        self.directory = directory
        self.timestamp = timestamp or datetime.datetime.now()
        self.historical_mode = historical_mode
        self.main_stats_file = 'stats.json'
        self.main_html_file = 'Koronavírus.html'
        self.map_file = 'terkep.jpg'
        self.deceased_file = 'deceased.json'
        self.deceased_file_template = 'Elhunytak {last}-{first}.html'
        self.url = url if self.historical_mode and url else self.BASE_URL

        if not self.url:
            raise ValueError('The url parameter is required for historical mode in _Fetcher')

        self.http = urllib3.PoolManager()

    def __del__(self):
        self.http.clear()

    def fetch(self):
        # return
        self._prepare_directory()
        self._fetch_stats()
        self._fetch_images()
        self._fetch_deceased()

    def reprocess(self):
        self._reprocess_stats()

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
        # if os.path.exists()
        raw_page = self._fetch_to_file(f'{self.BASE_URL}/', self.main_html_file).decode('UTF-8')
        self._gen_stats(raw_page)

    def _reprocess_stats(self):
        raw_page = self._load_file(self.main_html_file)
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
            if field.attrib['id'] != 'api-utolso-frissites':
                result[field.attrib['id'].replace('api-', '')] = int(field.text.replace(' ', ''))
            else:
                result[field.attrib['id'].replace('api-', '')] = field[0].attrib['content']

        result['local-timestamp'] = self._parse_date('Magyarorsz', root)
        result['global-timestamp'] = self._parse_date('A vil', root)

        self._write_to_json(result, self.main_stats_file)

    def _parse_date(self, h2_prefix: str, root) -> str:
        p = root.xpath(f"//h2[starts-with(text(),'{h2_prefix}')]/../p")
        # eg: "Legutolsó frissítés dátuma: 2021.03.06. 08:01"
        # eg: "Legutolsó frissítés dátuma:&nbsp;2021.03.07&nbsp;08:01"
        # eg: 22021.04.05. 14:38
        # eg: 2021.04.16.. 08:26
        # 22022-05-11
        text = p[0].text.split(':', 1)[1].strip() \
            .replace('&nbsp;', ' ') \
            .replace('22021.', '2021.') \
            .replace('22022.', '2022.') \
            .replace('..', '.')
        patterns = [
            '%Y.%m.%d. %H:%M',
            '%Y.%m.%d.%H:%M',
            '%Y.%m.%d %H:%M',
            '%Y.%m.%d. %H.%M.',
        ]

        dt = None
        for pattern in patterns:
            try:
                dt = datetime.datetime.strptime(text, pattern)
            except ValueError:
                continue

        if dt is None:
            raise ValueError(f"Unexpected format: {text}", )
        return dt.strftime("%Y-%m-%d %H:%M")

    def _fetch_deceased(self):
        entries = []
        first = 0
        page = 0

        while first != 1:
            first = self._fetch_deceased_nth(page, entries)
            page += 1
            time.sleep(0.1)

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

            try:
                age = int(age.strip())
            except ValueError:
                age = -1
            data = dict(index=int(index.strip()), gender=self._map_gender(gender.strip()), age=age)

            data['deseases'] = [x.strip() for x in deseases.split(',')]

            entries.append(data)

            if not last:
                last = data['index']

            first = data['index']

        with open(os.path.join(self.directory, self.deceased_file_template.format(first=first, last=last)), 'wt',
                  encoding='UTF-8') as f:
            f.write(raw_page)

        return first

    def _map_gender(self, gender: str) -> str:
        if not gender:
            return '-'

        first_letter = gender[0].lower()
        if first_letter == 'f':
            return 'man'
        else:
            return 'woman'

    def _fetch_image(self, src: str, filename: str):
        self._fetch_to_file(src, filename)

    def _fetch_to_file(self, src: str, filename: str) -> bytes:
        content = self._fetch_url(src)
        with open(os.path.join(self.directory, filename), 'wb') as f:
            f.write(content)

        return content

    def _load_file(self, filename: str) -> str:
        with open(os.path.join(self.directory, filename), 'rt', encoding='UTF-8') as f:
            return f.read()

    def _fetch_url(self, url: str) -> bytes:
        r = self.http.request('GET', url, retries=10)
        return r.data

    def _write_to_json(self, data: dict | list, filename: str):
        with open(f'{self.directory}/{filename}', 'wt', encoding='UTF-8') as f:
            json.dump(data, f, indent=2)


class _HistoricalFetcher:
    URL_FORMAT_STRING = 'https://archive.org/wayback/available?url=koronavirus.gov.hu&timestamp={date}2000'
    ARCHIVED_URL_FILENAME = '{date}.url.json'
    FIRST_DAY = (2020, 3, 4)

    def __init__(self, directory: str, timestamp: datetime.datetime):
        self.directory = directory
        self.timestamp = timestamp
        self.archived_url_directory = os.path.join(self.directory, 'archived-urls')
        self.archived_directory = os.path.join(self.directory, 'archived')
        self.url_fetcher = UrlFetcher(limit=50, sleep_time=3)

    def fetch(self):
        log_info('Fetching historical data')
        self._fetch_urls()
        self._fetch_archives()

    def _fetch_urls(self):
        if not os.path.exists(self.archived_url_directory):
            os.makedirs(self.archived_url_directory)

        for fetch_date in self._each_day():
            log_debug('Fetching/Checking historical URL info', dict(date=fetch_date.strftime('%Y-%m-%d')))
            filename = os.path.join(self.archived_url_directory,
                                    self.ARCHIVED_URL_FILENAME.format(date=fetch_date.strftime('%Y-%m-%d')))
            if not os.path.exists(filename):
                self.url_fetcher.fetch_to_file(
                    self.URL_FORMAT_STRING.format(date=fetch_date.strftime('%Y%m%d')),
                    filename)

    def _fetch_archives(self):
        for fetch_date in self._each_day():
            date = fetch_date.strftime('%Y-%m-%d')
            log_debug('Fetching/Checking historical details', dict(date=date))
            filename = os.path.join(self.archived_url_directory,
                                    self.ARCHIVED_URL_FILENAME.format(date=date))
            directory = os.path.join(self.archived_directory, date)
            _Fetcher(directory, self.timestamp, historical_mode=True).fetch()

    def _each_day(self) -> collections.abc.Iterable[datetime.date]:
        day = datetime.date(*self.FIRST_DAY)
        last_day = datetime.date.today()
        while day <= last_day:
            yield day
            day += datetime.timedelta(days=1)


class Fetcher:
    def __init__(self, directory: str, *, historical_mode: bool = False):
        self.base_directory = directory
        self.timestamp = datetime.datetime.now()
        self.directory = self.base_directory + f'/{self.timestamp.strftime("%Y%m%d-%H%M%S-%s")}'
        self.historical_mode = historical_mode

    def fetch(self):
        if self.historical_mode:
            return _HistoricalFetcher(self.base_directory, self.timestamp).fetch()
        else:
            return _Fetcher(self.directory, self.timestamp).fetch()
