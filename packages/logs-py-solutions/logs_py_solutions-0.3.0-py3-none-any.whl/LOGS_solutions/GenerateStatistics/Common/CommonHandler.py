from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
from LOGS.LOGS import LOGS

from .DateHandler import DateHandler
from .FileHandler import FileHandler
from .OutputGenerator import OutputGenerator
from .PathValidator import PathValidator


class CommonHandler(ABC):
    """This class provides methods to create statistics from LOGS data and save them as HTML or PDF files."""

    def __init__(
        self, logs: LOGS, begin_date: datetime, end_date: datetime, target_path: str
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API,
        :param begin_date: Lowest date limit for statistics to be created.
        :param end_date: Highest date limit for statistics to be created.
        :param target_path: Path where all datasets should be saved.
        """

        self._logs = logs
        self._begin_date = DateHandler.check_date(begin_date)
        self._end_date = DateHandler.check_date(end_date)
        self._target_path = PathValidator.validate_path(target_path)

        self.__template_path = Path(__file__).parent / "templates"
        self.__template_name = "statistic.jinja2"
        self.__report_generator = OutputGenerator(
            self.__template_path, self.__template_name
        )

    def _validate_list(self, parameter: List) -> List:
        if not isinstance(parameter, list):
            raise ValueError("Persons and Instruments must be a list.")
        return parameter

    def create_report(
        self, path: str, html: bool, pdf: bool, file_name: str, plot: plt.Figure
    ):
        """Creates a HTML or PDF file from a plot with the LOGS-PY Style.

        :param path: Path where the HTML should be saved.
        :param html_name: Name of the HTML file.
        :param plot: Plot that should be saved as HTML.
        """

        file_name = FileHandler.clean_filename(file_name)
        if html:
            self.__report_generator.create_html(path, file_name, plot)
        if pdf:
            self.__report_generator.create_pdf(path, file_name, plot)
