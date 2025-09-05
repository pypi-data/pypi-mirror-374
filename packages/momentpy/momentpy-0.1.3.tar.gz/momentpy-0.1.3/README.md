# momentpy – A Python Date Manipulation Library (Laravel Moment Inspired)

`momentpy` is a Python library inspired by Laravel’s Moment, providing readable date/time manipulation with timezone support.

---

## 📦 Installation

```bash
pip install momentpy
```

Or locally:

```bash
git clone <your-repo>
cd momentpy
pip install .
```

---

## 🕰️ Importing

```python
from momentpy import Moment
```

---

## 🕰️ Method Table (Quick Reference)

| Category       | Method                               | Description                |
| -------------- | ------------------------------------ | -------------------------- |
| Constructors   | `Moment.now(tz=None)`                | Current datetime           |
| Constructors   | `Moment.today(tz=None)`              | Today at 00:00             |
| Constructors   | `Moment.yesterday(tz=None)`          | Yesterday at 00:00         |
| Constructors   | `Moment.tomorrow(tz=None)`           | Tomorrow at 00:00          |
| Constructors   | `Moment.parse(date_str, fmt, tz)`    | Parse string to Moment     |
| Constructors   | `Moment.from_datetime(dt)`           | Convert datetime to Moment |
| Formatting     | `format(fmt)`                        | Format datetime            |
| Timezone       | `set_timezone(tz)`                   | Convert to timezone        |
| Timezone       | `timezone_name()`                    | Get timezone name          |
| Day            | `start_of_day()`                     | 00:00:00                   |
| Day            | `end_of_day()`                       | 23:59:59.999999            |
| Week           | `start_of_week(week_start="monday")` | Start of week              |
| Week           | `end_of_week(week_start="monday")`   | End of week                |
| Month          | `start_of_month()`                   | First day of month         |
| Month          | `end_of_month()`                     | Last day of month          |
| Year           | `start_of_year()`                    | First day of year          |
| Year           | `end_of_year()`                      | Last day of year           |
| Quarter        | `start_of_quarter()`                 | First day of quarter       |
| Quarter        | `end_of_quarter()`                   | Last day of quarter        |
| Relative       | `next(weekday)`                      | Next weekday               |
| Relative       | `previous(weekday)`                  | Previous weekday           |
| Relative       | `next_or_same(weekday)`              | Next or same weekday       |
| Relative       | `previous_or_same(weekday)`          | Previous or same weekday   |
| Manipulation   | `add_days(days)`                     | Add days                   |
| Manipulation   | `sub_days(days)`                     | Subtract days              |
| Manipulation   | `add_hours(hours)`                   | Add hours                  |
| Manipulation   | `sub_hours(hours)`                   | Subtract hours             |
| Manipulation   | `add_minutes(minutes)`               | Add minutes                |
| Manipulation   | `sub_minutes(minutes)`               | Subtract minutes           |
| Comparison     | `is_future()`                        | True if in future          |
| Comparison     | `is_past()`                          | True if in past            |
| Comparison     | `is_today()`                         | True if today              |
| Comparison     | `is_yesterday()`                     | True if yesterday          |
| Comparison     | `is_tomorrow()`                      | True if tomorrow           |
| Human-readable | `diff_for_humans(other)`             | Human-readable diff        |

---

## 📖 Example

```python
from momentpy import Moment

now = Moment.now("UTC")
print("Start of week:", now.start_of_week())
print("End of quarter:", now.end_of_quarter())
print("Next Monday:", now.next("monday"))
print("Start of year:", now.start_of_year())
print("Difference:", now.diff_for_humans(Moment.parse("2025-01-01")))
```
