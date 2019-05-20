import math
from datetime import datetime, timedelta
import numpy as np
import pytz

utc_timezone = pytz.timezone('UTC')
ny_timezone = pytz.timezone("America/New_York")


def parse_set(data_set):
    splitter = ',' if ',' in data_set else ' '
    # strip spaces, convert to all upper cases, split into array by comma
    return [data.strip() for data in data_set.strip().upper().split(splitter)]


def format_number(number, datatype):
    if datatype == "STR":
        return number
    elif datatype == "DEC":
        return number
    elif datatype == "HEX":
        hex_length = math.ceil(len(number) / 2.0) * 2
        return str(number).zfill(hex_length).upper()
    elif datatype == "BIN":
        bin_length = math.ceil(len(number) / 8.0) * 8
        return str(number).zfill(bin_length)
    else:
        return number


def output(data, data_type=None, with_header=True, with_line_number=False, split_lines=0):
    if not data_type:
        data_type = len(data[0]) * ("STR",)

    field_max_lengths = [0] * ((len(data[0]) + 1) if with_line_number else len(data[0]))

    if with_line_number:
        data_type = ("DEC",) + data_type

    count = 0
    for result in data[1:]:
        count += 1

        if with_line_number:
            result = (count,) + result

        if 'Bad inputs' not in result:
            result = [format_number(r, t) for r, t, in zip(result, data_type)]

        # figure max length for each field
        field_max_lengths = [max(m_l, d_l) for m_l, d_l in zip(field_max_lengths, [len(str(d)) for d in result])]

    body_data = data
    # output table
    field_max_lengths = [max(m_l, d_l) for m_l, d_l in zip(field_max_lengths, [len(str(d)) for d in data[0]])]
    print('+', end='')
    [print('-' * (n + 2), end="+") for n in field_max_lengths]
    print()

    if with_header:
        body_data = data[1:]

        if with_line_number:
            data[0] = ('',) + data[0]

        print('|', end='')
        [print(f' {d:{l+1}}', end="|") for d, l in zip(data[0], field_max_lengths)]
        print()

        print('+', end='')
        [print('-' * (n + 2), end="+") for n in field_max_lengths]
        print()

    count = 0
    for result in body_data:
        count += 1

        if with_line_number:
            result = (count,) + result

        if 'Bad inputs' not in result:
            result = [format_number(r, t) for r, t, in zip(result, data_type)]

        print('|', end='')
        [print(f' {str(d):{l + 1}}', end="|") for d, l in zip(result, field_max_lengths)]
        print()

        if count == len(body_data) or (split_lines != 0 and count % split_lines == 0):
            print('+', end='')
            [print('-' * (n + 2), end="+") for n in field_max_lengths]
            print()

    print()
    print()


def to_next_business_day(date_param):
    if type(date_param) is str:
        date = datetime.strptime(date_param, '%Y-%m-%d')
        if date.weekday() in [5, 6]:
            date = date + timedelta(days=(7 - date.weekday()))
        return datetime.strftime(date, '%Y-%m-%d')
    else:
        return to_next_business_day(datetime.strftime(date_param, '%Y-%m-%d'))


def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


# every trading day: 252
# every month: 12
# every week: 52 ??
def get_performance(s=None, n=252):
    if s is None:
        return 'Trades', 'Wins', 'Losses', 'Breakeven', 'Win/Loss Ratio', 'Mean Win', 'Mean Loss', 'Mean', 'STDEV', 'Max Win', 'Max Loss', 'Sharpe Ratio'

    s = s.dropna()
    count = len(s)
    win_count = len(s[s > 0])
    loss_count = len(s[s < 0])
    even_count = len(s[s == 0])
    mean_win = round(s[s > 0].mean(), 3)
    mean_loss = round(s[s < 0].mean(), 3)
    win_loss_ratio = -1 if loss_count == 0 else round(win_count / loss_count, 3)
    mean_trd = round(s.mean(), 3)
    stdev = round(np.std(s), 3)
    max_win = round(s.max(), 3)
    max_loss = round(s.min(), 3)
    sharpe_ratio = round((s.mean() / np.std(s)) * np.sqrt(n), 4)
    return count, win_count, loss_count, even_count, win_loss_ratio, mean_win, mean_loss, mean_trd, stdev, max_win, max_loss, sharpe_ratio


def uct_to_ny_time(utc_time):
    the_time = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_timezone.localize(the_time)
    ny_time = utc_time.astimezone(ny_timezone)
    return ny_time.strftime('%H:%M:%S')


class Stack:
    def __init__(self, size=None):
        self.items = []
        self.size = int(size) if size else size

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)
        if self.size:
            self.items = self.items[-self.size:]

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)

    def get_items(self):
        return self.items


class FifoQueue:
    def __init__(self, size=None):
        self.items = []
        self.size = int(size) if size else size

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)
        if self.size:
            self.items = self.items[-self.size:]

    def pop(self):
        v = self.items[0]
        self.items = self.items[1:]
        return v

    def peek(self):
        return self.items[0]

    def size(self):
        return len(self.items)

    def get_items(self):
        return self.items


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def get_slop_output(slop_value):
    return ((Color.GREEN + "/" if slop_value > 0 else Color.BLUE + "-") if slop_value >= 0 else Color.RED + "\\") + Color.END


def get_diff_output(diff_value, prefix='', postfix=''):
    return (Color.RED if diff_value < 0 else Color.GREEN) + prefix + str(diff_value) + postfix + Color.END


def a(value, trade_value):
    if is_digit(value):
        return (Color.RED if (value - trade_value) < 0 else Color.GREEN) + str(value) + Color.END
    else:
        return Color.BLUE + str(value) + Color.END
