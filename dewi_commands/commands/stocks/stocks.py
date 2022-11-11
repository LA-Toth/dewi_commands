# Copyright 2021-2022 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import copy
import csv
import datetime
import enum
import math

from dewi_core.config.node import Node
from dewi_core.utils.yaml import save_to_yaml

# Float numbers are not precise, so let's define a limit which can be handled as zero
ABOUT_ZERO = math.pow(10, -5)


class Action(enum.Enum):
    BUY = 1
    SELL = 2
    DIVIDEND = 3
    DIVIDE_SHARE = 4

    @classmethod
    def create(cls, action: str):
        if action.startswith('B'):
            return cls.BUY
        elif action.startswith('S'):
            return cls.SELL
        elif action == 'Dividend':
            return cls.DIVIDEND
        elif action == 'Divide_Share':
            return cls.DIVIDE_SHARE
        else:
            raise Exception('Unknown Action')

    def __repr__(self):
        return self.name.lower()


class StockInputEntry(Node):
    def __init__(self):
        self.date: datetime.date = None
        self.action: Action = None
        self.name: str = None
        self.price: float = 0
        self.share_price: float = 0
        self.share_amount: float = 0
        self._seal()

    @classmethod
    def create(cls, entry_date: str, action: str, stock: str, price: str, share_price: str, amount: str):
        r = cls()
        r.date = datetime.datetime.strptime(entry_date, '%Y.%m.%d').date()
        r.action = Action.create(action)
        r.name = stock
        r.price = float(price[2:].replace(',', '.') or '0.0')
        r.share_price = float(share_price[2:].replace(',', '.') or '0.0')
        if amount.startswith('$ '):
            amount = amount[2:]
        r.share_amount = float(amount.replace(',', '.') or 0.0)
        return r


class SharePriceAmount(Node):
    def __init__(self):
        self.price: float = 0.0
        self.amount: float = 0.0

    @classmethod
    def create(cls, price: float, amount: float):
        s = cls()
        s.price = price
        s.amount = amount
        return s


class ShareState(Node):
    def __init__(self):
        self.name: str = ''
        self.amount: float = 0
        self.dividend_gain: float = 0.0
        self.share_gain: float = 0.0
        self.total_gain: float = 0.0
        self.amount_details: list[SharePriceAmount] = []
        self._seal()


class State(Node):
    def __init__(self):
        self.input_entry: StockInputEntry = None
        self.shares_state: dict[str, ShareState] = dict()
        self.gain: float = 0.0
        self.loss: float = 0.0
        self.dividend: float = 0.0
        self.total: float = 0.0
        self._seal()

    def get_share_state(self, share_name: str):
        if share_name not in self.shares_state:
            s = ShareState()
            s.name = share_name
            self.shares_state[share_name] = s
            return s

        return self.shares_state[share_name]


class StocksProcessor:
    """
    Calculates total amount of loss / gain of stocks.

    The input format is very strict, and each entry must use the same currency (sometimes prefixed with two chars,
    usually '$ '.
    Flaots are in the computer-readable form (eg. 0,5 or 0.5, 7.100023422 or so), both comma and dot can delimit
    the decimals. The comma cannot be thousands-separator compared to regular English language.
    - it is a CSV file
    - it has a header
    - if a row's first cell is empty, the row is ignored
    - the row format:
       - DATE in YYYY.mm.dd format (%Y.%m.%d for strptime)
       - ACTION in ('Buy', 'Sell', 'Divide', 'Divide_Share')
       - PRICE float, prefixed with '$ ', ignored for Divide_Share
       - SHARE_PRICE float, prefixed with '$ ', ignored for Divide_Share or Divide. The price of a single share.
       - SHARE_AMOUNT float, ignored for 'Divide'; for 'Divide_Share' it defines the split amount of shares, so
              if an original share becomes ten shares, this field must contain '10' with action 'Divide_Share'.
       - any further columns are ignored

    In the YAML output:
    It calculates the total gain, total loss and the sum of dividends separately and their grand total.
    Also shows the details of all previously or currently exchanged stocks:
    - current amount (which can be 0 if the stock is sold previously)
    - received dividend
    - gain from sells (share gain)
    - total gain (share + dividend)
    - amount of the shares still be kept, a list of pairs of:
        o share price
        o share amount

    Example YAML output:
    dividend: 3.3
    gain: 107,7
    loss: 44,27
    shares_state:
        STOCKID:
            amount: 0.0
            amount_details: []
            dividend_gain: 2.3
            name: STOCKID
            share_gain: 107.7
            total_gain: 110.0
        STOCKID2:
            amount: 2.0
            amount_details:
            -   amount: 2.0
                price: 54.0
            dividend_gain: 1.0
            name: STOCKID2
            share_gain: -44,27
            total_gain: -43,27
    total: 66.73
    """

    def __init__(self, input_filename: str, output_filename: str):
        self._input = input_filename
        self._output = output_filename

        self._rows = []
        self._state: list[State] = []
        self._last_state = State()

    def process(self):
        self._load()
        self._process()
        self._save()

    def _load(self):
        with open(self._input, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            in_header = True
            for row in reader:

                if in_header:
                    in_header = False
                    continue

                if not row[0]:
                    continue

                self._rows.append(StockInputEntry.create(*row[:6]))

    def _process(self):
        for row in self._rows:
            self._state.append(self._process_row(row))

    def _process_row(self, entry: StockInputEntry):
        s = copy.deepcopy(self._last_state)
        # s.input_entry = entry

        share_state = s.get_share_state(entry.name)

        if entry.action == Action.DIVIDEND:
            share_state.dividend_gain += entry.price
            s.dividend += entry.price
            s.total += entry.price
        elif entry.action == Action.DIVIDE_SHARE:
            for sta in share_state.amount_details:
                sta.amount *= entry.share_amount
                sta.price /= entry.share_amount
            share_state.amount *= entry.share_amount
        elif entry.action == Action.BUY:
            share_state.amount += entry.share_amount
            share_state.amount_details.append(SharePriceAmount.create(entry.share_price, entry.share_amount))
        elif entry.action == Action.SELL:
            share_state.amount -= entry.share_amount
            adetails = share_state.amount_details
            share_state.amount_details = []
            amount = entry.share_amount
            ad = adetails[0]
            while True:
                if ad.amount - amount > ABOUT_ZERO:
                    ad.amount -= amount
                    chg = amount * (entry.share_price - ad.price)

                    if chg < 0:
                        s.loss -= chg
                    else:
                        s.gain += chg
                    s.total += chg
                    share_state.share_gain += chg
                    share_state.total_gain += chg
                    share_state.amount_details += adetails
                    break
                else:
                    chg = ad.amount * (entry.share_price - ad.price)
                    if chg < 0:
                        s.loss -= chg
                    else:
                        s.gain += chg
                    s.total += chg
                    share_state.share_gain += chg
                    share_state.total_gain += chg

                    amount -= ad.amount
                    if amount > ABOUT_ZERO:
                        adetails = adetails[1:]
                        ad = adetails[0]
                    else:
                        share_state.amount = 0.0
                        break

        s.shares_state[entry.name] = share_state

        self._last_state = s
        return s

    def _save(self):
        save_to_yaml(self._last_state, '-')
