import re
from datetime import timedelta, datetime, date

from django.db.models import Lookup, DateTimeField
from django.utils import timezone


class DateTimeOffsetLookup(Lookup):
    lookup_name = 'dtoffset'  # Enables `created_at__dtoffset="-60d"` and ISO 8601 like `P1Y2M`

    ISO_PATTERN = r"P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?"

    SHORT_PATTERN = r"(-?\d+)([ymoWdHMs]+)"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        value = rhs_params[0]  # Extract filter value

        # If value is an actual date or datetime, use it directly
        if isinstance(value, (datetime, date)):
            return f"{lhs} = %s", [value]

        total_seconds = self.parse_duration(value)

        if total_seconds is None:
            raise ValueError("Invalid 'dtoffset' format. Use ISO 8601 (P3Y6M4DT12H30M5S) or shorthand (-60d, 2w).")

        date_threshold = timezone.now() - timedelta(seconds=abs(total_seconds))

        # If dtoffset is negative (`-60d`), use `>=`, otherwise use `<=`
        operator = ">=" if value.startswith("-") else "<="
        return f"{lhs} {operator} %s", [date_threshold]

    def parse_duration(self, value):
        """Parses both ISO 8601 duration (P3Y6M4DT12H30M5S) and shorthand (-60d, 2w)."""
        total_seconds = 0

        if re.match(self.ISO_PATTERN, value):  # ISO 8601 format
            match = re.match(self.ISO_PATTERN, value)
            years, months, weeks, days, hours, minutes, seconds = map(
                lambda x: int(x) if x else 0, match.groups()
            )
            total_seconds += years * 31536000  # 1 year ≈ 365 days * 86400 seconds
            total_seconds += months * 2592000  # 1 month ≈ 30 days * 86400 seconds
            total_seconds += weeks * 604800  # 1 week = 7 days * 86400 seconds
            total_seconds += days * 86400  # 1 day = 86400 seconds
            total_seconds += hours * 3600  # 1 hour = 3600 seconds
            total_seconds += minutes * 60  # 1 minute = 60 seconds
            total_seconds += seconds  # Seconds remain as is

        elif re.findall(self.SHORT_PATTERN, value):  # Shorthand format
            for amount, unit in re.findall(self.SHORT_PATTERN, value):
                amount = int(amount)
                if unit == 'y':
                    total_seconds += amount * 31536000
                elif unit == 'mo':
                    total_seconds += amount * 2592000
                elif unit == 'w':
                    total_seconds += amount * 604800
                elif unit == 'd':
                    total_seconds += amount * 86400
                elif unit == 'h':
                    total_seconds += amount * 3600
                elif unit == 'm':
                    total_seconds += amount * 60
                elif unit == 's':
                    total_seconds += amount

        else:
            return None  # Invalid format

        return total_seconds


# Register the lookup globally
DateTimeField.register_lookup(DateTimeOffsetLookup)
