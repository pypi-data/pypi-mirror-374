from datetime import datetime


class DateHandler:
    """This class provides methods to handle dates.

    The class provides methods to check if a given date is in the correct format and to check if a given date is in a given range.
    Additionally, the class provides a method to convert seconds to days, hours, minutes and seconds.
    """

    @staticmethod
    def check_date(date: datetime) -> datetime:
        """Checks if the given date is a datetime object.

        :param date: check if the given date is a datetime object.
        :return: datetime object
        """

        if not isinstance(date, datetime) and date is not None:
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    raise ValueError(
                        "Date is not in the correct format. It must be either a datetime object or a string in the format '%Y-%m-%d %H:%M:%S.%f'."
                    ) from None
        return date

    @staticmethod
    def check_date_range(
        current_date: datetime, begin_date: datetime, end_date: datetime
    ) -> bool:
        """Checks if the current date is in the range between begin_date and end_date

        :param current_date: Date which is to be checked

        :return: Boolean if the current_date is in the range
        """

        DateHandler.check_date(current_date)
        if begin_date and end_date:
            return begin_date <= current_date <= end_date
        return False

    @staticmethod
    def seconds_to_dhms(seconds):
        days = seconds // (24 * 3600)
        seconds = seconds % (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
