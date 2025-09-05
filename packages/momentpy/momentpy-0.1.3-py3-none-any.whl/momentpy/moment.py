from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class Moment(datetime):
    WEEKDAYS = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    DEFAULT_WEEK_START = 0  # Monday

    # --- Static constructors ---
    @staticmethod
    def now(tz=None):
        return Moment.from_datetime(datetime.now(tz=ZoneInfo(tz) if tz else None))

    @staticmethod
    def today(tz=None):
        return Moment.from_datetime(datetime.now(tz=ZoneInfo(tz) if tz else None).replace(
            hour=0, minute=0, second=0, microsecond=0
        ))

    @staticmethod
    def yesterday(tz=None):
        return Moment.today(tz).sub_days(1)

    @staticmethod
    def tomorrow(tz=None):
        return Moment.today(tz).add_days(1)

    @staticmethod
    def parse(date_str, fmt="%Y-%m-%d %H:%M:%S", tz=None):
        dt = datetime.strptime(date_str, fmt)
        if tz:
            dt = dt.replace(tzinfo=ZoneInfo(tz))
        return Moment.from_datetime(dt)

    @staticmethod
    def from_datetime(dt: datetime):
        return Moment(
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second,
            dt.microsecond, dt.tzinfo
        )

    # --- Formatting ---
    def format(self, fmt="%Y-%m-%d %H:%M:%S"):
        return self.strftime(fmt)

    # --- Timezone ---
    def set_timezone(self, tz: str):
        return self.astimezone(ZoneInfo(tz))

    def timezone_name(self):
        return self.tzinfo.key if self.tzinfo else None

    # --- Manipulations ---
    def add_days(self, days=1):
        return self + timedelta(days=days)

    def sub_days(self, days=1):
        return self - timedelta(days=days)

    def add_hours(self, hours=1):
        return self + timedelta(hours=hours)

    def sub_hours(self, hours=1):
        return self - timedelta(hours=hours)

    def add_minutes(self, minutes=1):
        return self + timedelta(minutes=minutes)

    def sub_minutes(self, minutes=1):
        return self - timedelta(minutes=minutes)

    # --- Start / End helpers ---
    def start_of_day(self):
        return Moment(self.year, self.month, self.day, 0, 0, 0, 0, self.tzinfo)

    def end_of_day(self):
        return Moment(self.year, self.month, self.day, 23, 59, 59, 999999, self.tzinfo)

    def start_of_week(self, week_start="monday"):
        """Return the start of the week (default Monday)."""
        week_start = week_start.lower()
        if week_start not in self.WEEKDAYS:
            raise ValueError(f"Invalid weekday: {week_start}")

        current = self.weekday()
        target = self.WEEKDAYS[week_start]
        days_behind = (current - target + 7) % 7
        return self.sub_days(days_behind).start_of_day()

    def end_of_week(self, week_start="monday"):
        """Return the end of the week (default Sunday if week starts on Monday)."""
        start = self.start_of_week(week_start)
        return start.add_days(6).end_of_day()

    def start_of_month(self):
        return Moment(self.year, self.month, 1, 0, 0, 0, 0, self.tzinfo)

    def end_of_month(self):
        if self.month == 12:
            next_month = Moment(self.year + 1, 1, 1, tzinfo=self.tzinfo)
        else:
            next_month = Moment(self.year, self.month + 1, 1, tzinfo=self.tzinfo)
        return next_month.sub_days(1).end_of_day()

    def start_of_year(self):
        return Moment(self.year, 1, 1, 0, 0, 0, 0, self.tzinfo)

    def end_of_year(self):
        return Moment(self.year, 12, 31, 23, 59, 59, 999999, self.tzinfo)

        # --- Quarter helpers ---

    def start_of_quarter(self):
        quarter = ((self.month - 1) // 3) + 1
        start_month = 3 * (quarter - 1) + 1
        return Moment(self.year, start_month, 1, 0, 0, 0, 0, self.tzinfo)

    def end_of_quarter(self):
        quarter = ((self.month - 1) // 3) + 1
        start_month = 3 * (quarter - 1) + 1
        if start_month + 2 > 12:
            end_month = 12
            year = self.year
        else:
            end_month = start_month + 2
            year = self.year
        # Last day of the month
        if end_month == 12:
            last_day = 31
        else:
            last_day = (Moment(year, end_month + 1, 1, tzinfo=self.tzinfo) - timedelta(days=1)).day
        return Moment(year, end_month, last_day, 23, 59, 59, 999999, self.tzinfo)

    # --- Relative weekday helpers ---
    def next(self, weekday: str):
        weekday = weekday.lower()
        if weekday not in self.WEEKDAYS:
            raise ValueError(f"Invalid weekday: {weekday}")

        target = self.WEEKDAYS[weekday]
        days_ahead = (target - self.weekday() + 7) % 7
        days_ahead = 7 if days_ahead == 0 else days_ahead
        return self.add_days(days_ahead)

    def previous(self, weekday: str):
        weekday = weekday.lower()
        if weekday not in self.WEEKDAYS:
            raise ValueError(f"Invalid weekday: {weekday}")

        target = self.WEEKDAYS[weekday]
        days_behind = (self.weekday() - target + 7) % 7
        days_behind = 7 if days_behind == 0 else days_behind
        return self.sub_days(days_behind)

    def next_or_same(self, weekday: str):
        weekday = weekday.lower()
        if weekday not in self.WEEKDAYS:
            raise ValueError(f"Invalid weekday: {weekday}")

        target = self.WEEKDAYS[weekday]
        days_ahead = (target - self.weekday() + 7) % 7
        return self.add_days(days_ahead)

    def previous_or_same(self, weekday: str):
        weekday = weekday.lower()
        if weekday not in self.WEEKDAYS:
            raise ValueError(f"Invalid weekday: {weekday}")

        target = self.WEEKDAYS[weekday]
        days_behind = (self.weekday() - target + 7) % 7
        return self.sub_days(days_behind)

    # --- Comparisons ---
    def is_future(self):
        return self > datetime.now(self.tzinfo or None)

    def is_past(self):
        return self < datetime.now(self.tzinfo or None)

    def is_today(self):
        today = datetime.now(self.tzinfo or None).date()
        return self.date() == today

    def is_yesterday(self):
        yesterday = (datetime.now(self.tzinfo or None) - timedelta(days=1)).date()
        return self.date() == yesterday

    def is_tomorrow(self):
        tomorrow = (datetime.now(self.tzinfo or None) + timedelta(days=1)).date()
        return self.date() == tomorrow

    # --- Human-friendly differences ---
    def diff_for_humans(self, other=None):
        if other is None:
            other = datetime.now(self.tzinfo or None)

        delta = self - other
        seconds = int(delta.total_seconds())

        if seconds == 0:
            return "just now"

        future = seconds > 0
        seconds = abs(seconds)

        if seconds < 60:
            unit = "second"
            count = seconds
        elif seconds < 3600:
            unit = "minute"
            count = seconds // 60
        elif seconds < 86400:
            unit = "hour"
            count = seconds // 3600
        else:
            unit = "day"
            count = seconds // 86400

        if count != 1:
            unit += "s"

        if future:
            return f"in {count} {unit}"
        else:
            return f"{count} {unit} ago"
