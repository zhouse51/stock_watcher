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

    def peek_first(self):
        return self.items[0] if self.get_size() > 0 else None

    def peek_last(self):
        return self.items[-1] if self.get_size() > 0 else None

    def get_size(self):
        return len(self.items)

    def get_items(self):
        return self.items


class Color:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BG_NORMAL = '\033[7m'
    DARKCYAN = '\033[36m'
    BRIGHT_WHITE = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    GREY = '\033[37m'
    BG_WHITE = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_GREY = '\033[47m'
    LIGHT_BLACK = '\033[90m'
    LIGHT_RED = '\033[91m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_PURPLE = '\033[95m'
    LIGHT_CYAN = '\033[96m'
    DARK_BLACK = '\033[97m'
    BG_LIGHT_BLACK = '\033[100m'
    BG_LIGHT_RED = '\033[101m'
    BG_LIGHT_GREEN = '\033[102m'
    BG_LIGHT_YELLOW = '\033[103m'
    BG_LIGHT_BLUE = '\033[104m'
    BG_LIGHT_PURPLE = '\033[105m'
    BG_LIGHT_CYAN = '\033[106m'
    BG_DARK_BLACK = '\033[107m'
    END = '\033[0m'


def get_slop_output(slop_value):
    return ((Color.GREEN + "/" if slop_value > 0 else Color.BLUE + "-") if slop_value >= 0 else Color.RED + "\\") + Color.END


def get_diff_output(value, format='{:>7}', prefix='', postfix=''):
    return (Color.RED if value < 0 else Color.GREEN) + \
           prefix + \
           format.format(value) + \
           postfix + \
           Color.END


def get_level_output(value, trade_value):
    if is_digit(value):
        return ((Color.RED if (value - trade_value) < 0 else Color.CYAN) if (value - trade_value) <= 0 else Color.GREEN) + str(value) + Color.END
    else:
        return Color.BLUE + str(value) + Color.END
