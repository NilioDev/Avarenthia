"""The reckoning of days in Avarenthia: twelve months of thirty days, seven days to the week."""

MONTHS = ['Deepfrost', 'Thawmoon', 'Seedwake', 'Greentide', 'Blossomreign', 'Highsun',
          'Emberwane', 'Goldfield', 'Harvestmoon', 'Leaffall', 'Mistwane', 'Longnight']
SEASONS = ['winter', 'winter', 'spring', 'spring', 'spring', 'summer', 'summer', 'summer', 'autumn', 'autumn', 'autumn', 'winter']
WEEKDAYS = ['Moonsday', 'Hearthday', 'Stonesday', 'Windsday', 'Tidesday', 'Starsday', 'Restday']
DAYS_IN_MONTH = 30
YEAR = 1172            # years After the Ruin
START = 2 * DAYS_IN_MONTH + 2     # the story begins on the 3rd of Seedwake


def _split(day):
    n = START + day - 1
    y, r = divmod(n, DAYS_IN_MONTH * 12)
    mo, d = divmod(r, DAYS_IN_MONTH)
    return YEAR + y, mo, d + 1, (day - 1) % 7      # your first day is a Moonsday


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def short(day):
    y, mo, d, wd = _split(day)
    return f'{d} {MONTHS[mo]}'


def long(day):
    y, mo, d, wd = _split(day)
    return f'{WEEKDAYS[wd]}, the {ordinal(d)} of {MONTHS[mo]}, {y} AR'


def season(day):
    return SEASONS[_split(day)[1]]


def weekday(day):
    return WEEKDAYS[_split(day)[3]]
