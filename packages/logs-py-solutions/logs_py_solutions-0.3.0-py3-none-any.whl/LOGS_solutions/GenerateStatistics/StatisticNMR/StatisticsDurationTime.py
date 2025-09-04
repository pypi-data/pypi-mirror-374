import csv
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
from LOGS import LOGS
from LOGS.Entities import Dataset, DatasetRequestParameter

from ..Common.FileHandler import FileHandler
from .StatisticHandlerNMR import StatisticHandlerNMR


class StatisticsDurationTime(StatisticHandlerNMR):
    """Class to generate
    - statistics for the duration time of each instrument. The statistics are divided into the following parts:
        - Year duration time
        - Year month duration time
        - Year calendar week duration time
        - Comparison heatmap duration time
    """

    def __init__(
        self,
        logs: LOGS,
        begin_date: datetime,
        end_date: datetime,
        target_path: str,
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API,
        :param begin_date: Lowest date limit for statistics to be created.
        :param end_date: Highest date limit for statistics to be created.
        :param target_path: Path where all datasets should be saved.
        """

        self._logger_dur_time = logging.getLogger("StatisticsDurationTime")
        self._logger_dur_time.setLevel(logging.INFO)

        logfile_folder = Path(__file__).resolve().parent / "logfiles"
        logfile_folder.mkdir(parents=True, exist_ok=True)
        logfile_path = logfile_folder / "StatisticsDurationTime.log"
        if not self._logger_dur_time.hasHandlers():
            logfile_handler = logging.FileHandler(logfile_path, mode="w")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            logfile_handler.setFormatter(formatter)
            self._logger_dur_time.addHandler(logfile_handler)

            logconsole_handler = logging.StreamHandler(sys.stdout)
            logconsole_handler.setLevel(logging.INFO)
            logconsole_handler.setFormatter(formatter)
            self._logger_dur_time.addHandler(logconsole_handler)

        super().__init__(logs, begin_date, end_date, target_path, self._logger_dur_time)

        if self._begin_date is None:
            self._begin_date = (
                self._logs.datasets(
                    DatasetRequestParameter(orderby="ACQUISITION_DATE_ASC")
                )
                .first()
                .acquisitionDate
            )
        if self._end_date is None:
            self._end_date = (
                self._logs.datasets(
                    DatasetRequestParameter(orderby="ACQUISITION_DATE_DESC")
                )
                .first()
                .acquisitionDate
            )

    def sum_time_strings(self, time_string: str):
        """Sum up the given time_string in seconds.

        :param time_string: Time string in the format "1d 2h 3min 4s".

        :return: Total time in seconds.

        """

        total_seconds = 0
        days = re.search(r"(\d+)\s*d", time_string)
        houres = re.search(r"(\d+)\s*h", time_string)
        minutes = re.search(r"(\d+)\s*min", time_string)
        seconds = re.search(r"(\d+)\s*s", time_string)

        if days:
            total_seconds += int(days.group(1)) * 86400
        if houres:
            total_seconds += int(houres.group(1)) * 3600
        if minutes:
            total_seconds += int(minutes.group(1)) * 60
        if seconds:
            total_seconds += int(seconds.group(1))

        return total_seconds

    def get_general_info(self, dataset: Dataset):
        """Checks if 'General information/Duration' or 'General info/Duration' exists in the dataset."""

        if dataset.getParameter("General information/Duration") is not None:
            return dataset.getParameter("General information/Duration")
        if dataset.getParameter("General info/Duration") is not None:
            return dataset.getParameter("General info/Duration")
        return None

    def check_duration(self, dataset: Dataset) -> bool:
        """Check if the duration parameter of the data set is empty or None.
        Write the data set to one of the following csv files:
        - DurationNone.csv: If the data set has no duration parameter.
        - NoDurationTime.csv: If the duration parameter of the data set is empty.
        - DurationTime.csv: If the duration parameter of the data set is not empty.
        """

        if dataset.instrument is None or dataset.instrument == "":
            instrument_name = "No_Instrument"
            instrument_id = 0
        else:
            instrument_name = FileHandler.clean_csv_text(dataset.instrument.name)
            instrument_id = dataset.instrument.id

        if self.get_general_info(dataset) is None:
            # If the data set has no duration parameter log an error message and write the dataset to a csv file
            self._logger_dur_time.warning(
                "Dataset has no duration parameter. %s It will not be included in the statistic.",
                dataset.name,
            )
            self._target_path.mkdir(parents=True, exist_ok=True)
            csv_path = self._target_path / "DurationNone.csv"

            file_exists = csv_path.is_file()
            with open(
                self._target_path / "DurationNone.csv", "a", newline=""
            ) as error_file:
                writer = csv.writer(error_file, delimiter=";")
                if not file_exists:
                    writer.writerows(
                        [
                            [
                                f"Datasets acquired between {self._begin_date.strftime('%d/%B/%Y')} "
                                f"and {self._end_date.strftime('%d/%B/%Y')} with 'None' as duration parameter."
                            ],
                            [
                                "Dataset",
                                "ID",
                                "Acquisition Date",
                                "Instrument Name",
                                "Instrument ID",
                            ],
                        ]
                    )
                writer.writerow(
                    [
                        FileHandler.clean_csv_text(dataset.name),
                        dataset.id,
                        dataset.acquisitionDate,
                        instrument_name,
                        instrument_id,
                    ]
                )

            return True

        if self.get_general_info(dataset) == "":
            # If the duration parameter of the data set is empty log an error message and write the dataset to a csv file
            self._logger_dur_time.warning(
                "The duration parameter of the Dataset %s is empty.", dataset.name
            )
            self._target_path.mkdir(parents=True, exist_ok=True)
            csv_path = self._target_path / "NoDurationTime.csv"

            file_exists = csv_path.is_file()
            with open(
                self._target_path / "NoDurationTime.csv", "a", newline=""
            ) as error_file:
                writer = csv.writer(error_file, delimiter=";")
                if not file_exists:
                    writer.writerows(
                        [
                            [
                                f"Datasets acquired between {self._begin_date.strftime('%d/%B/%Y')} "
                                f"and {self._end_date.strftime('%d/%B/%Y')} with an empty duration parameter."
                            ],
                            [
                                "Dataset",
                                "ID",
                                "Acquisition Date",
                                "Instrument Name",
                                "Instrument ID",
                            ],
                        ]
                    )
                writer.writerow(
                    [
                        FileHandler.clean_csv_text(dataset.name),
                        dataset.id,
                        dataset.acquisitionDate,
                        instrument_name,
                        instrument_id,
                    ]
                )

                return False
        else:
            # If the duration parameter is not empty, write the dataset to a csv file
            self._target_path.mkdir(parents=True, exist_ok=True)
            csv_path = self._target_path / "DurationTime.csv"

            file_exists = csv_path.is_file()
            with open(
                self._target_path / "DurationTime.csv", "a", newline=""
            ) as error_file:
                writer = csv.writer(error_file, delimiter=";")
                if not file_exists:
                    writer.writerows(
                        [
                            [
                                f"Datasets acquired between {self._begin_date.strftime('%d/%B/%Y')} "
                                f"and {self._end_date.strftime('%d/%B/%Y')} with a duration parameter."
                            ],
                            [
                                "Dataset",
                                "ID",
                                "Duration",
                                "Acquisition Date",
                                "Instrument Name",
                                "Instrument ID",
                            ],
                        ]
                    )
                writer.writerow(
                    [
                        FileHandler.clean_csv_text(dataset.name),
                        dataset.id,
                        self.get_general_info(dataset),
                        dataset.acquisitionDate,
                        instrument_name,
                        instrument_id,
                    ]
                )

                return False

    def update_instrument_dict(
        self, dataset: Dataset, dataset_instrument_dict: Dict
    ) -> Dict:
        """Updating the instrument dictionary for the data set. For this purpose, the current accumulated time and the acquisition date are added to the dicitonary.

        :param dataset: Data set containing the instrument.
        :param dataset_instrument_dict: Dictionary of all instruments with a list of the acquisition date of their data sets.

        :return: Dictionary of the instruments, each key is the id of the instrument and
        has the instrument name as value[0]
        """
        try:
            dataset.fetchParameters()
        except Exception as e:
            self._logger_dur_time.error(
                "Could not fetch the full dataset. %s It will not be included in the statistic. %s",
                dataset.name,
                e,
            )
            return dataset_instrument_dict

        if self.check_duration(dataset):
            return dataset_instrument_dict

        # If the data set has no instrument
        if dataset.instrument is None or dataset.instrument == "":
            if 0 not in dataset_instrument_dict:
                dataset_instrument_dict[0] = ["No_Instrument"]
            datasets_date_list = dataset_instrument_dict[0]
            datasets_date_list.append(
                (
                    self.sum_time_strings(self.get_general_info(dataset)),
                    dataset.acquisitionDate,
                    dataset.operators,
                )
            )
            dataset_instrument_dict[0] = datasets_date_list
        else:
            if dataset.instrument.id not in dataset_instrument_dict:
                dataset_instrument_dict[dataset.instrument.id] = [
                    dataset.instrument.name
                ]

            datasets_date_list = dataset_instrument_dict[dataset.instrument.id]
            datasets_date_list.append(
                (
                    self.sum_time_strings(self.get_general_info(dataset)),
                    dataset.acquisitionDate,
                    dataset.operators,
                )
            )
            dataset_instrument_dict[dataset.instrument.id] = datasets_date_list

        return dataset_instrument_dict

    def create_statistic(self):
        """Generates the statistics for the utilization time (based on "duration") of each instrument.

        This statistic is divided into the following parts:
        - Year utilization time
        - Year month utilization time
        - Year calendar week utilization time
        - Comparison heatmap utilization time
        """

        self._logger_dur_time.info(
            "Starting to generate a statistical analysis of the utilization time."
        )

        # Get the total number of datasets with the format "BrukerNMR" and "NMR (Varian)" and the acquisition date between the begin and end date
        datasets_total = self._logs.datasets(
            DatasetRequestParameter(
                acquisitionDateFrom=self._begin_date,
                acquisitionDateTo=self._end_date,
                formatIds=["BrukerNMR", "VarianNMR"],
            )
        ).count

        # Check if there are datasets with the fromat 'BrukerNMR'nand 'NMR (Varian)' in the given time frame
        if datasets_total == 0:
            self._logger_dur_time.info(
                "No datasets with the format 'BrukerNMR' and 'NMR (Varian)' found in the given time frame."
            )
            return

        self._logger_dur_time.info(
            "Processing datasets with the format 'BrukerNMR' and 'VarianNMR' in the given time frame: begin date: %s - end date: %s.",
            self._begin_date,
            self._end_date,
        )
        instrument_dict = {}
        count = 0  # Counter for the number of processed datasets
        # Get all datasets with the format "BrukerNMR" and "NMR (Varian)" and the acquisition date between the begin and end date
        for dataset in self._logs.datasets(
            DatasetRequestParameter(
                acquisitionDateFrom=self._begin_date,
                acquisitionDateTo=self._end_date,
                formatIds=["BrukerNMR", "VarianNMR"],
            )
        ):
            # Skip datasets with invalid acquisition date
            tz = dataset.acquisitionDate.tzinfo
            if (
                (dataset.acquisitionDate is None)
                or (datetime(1677, 9, 21, tzinfo=tz) >= dataset.acquisitionDate)
                or (dataset.acquisitionDate >= datetime(2262, 4, 11, tzinfo=tz))
            ):
                self._logger_dur_time.warning(
                    "Dataset %s has invalid acquisition date.: %s Dataset will not be included in the statistics.",
                    dataset.id,
                    dataset.acquisitionDate,
                )
                continue

            if count % 10000 == 0 and count != 0:
                self._logger_dur_time.info(
                    "%d/%d datasets processed.",
                    count,
                    datasets_total,
                )

            count += 1

            instrument_dict = self.update_instrument_dict(dataset, instrument_dict)

        self._logger_dur_time.info(
            "Finished processing datasets with the format 'BrukerNMR' and 'NMR (Varian)'."
        )

        # Create the statistics for the utilization time of each instrument
        self._logger_dur_time.info(
            "Generating reports with the statistics for the utilization time of each instrument."
        )

        if len(instrument_dict) == 0:
            self._logger_dur_time.warning(
                "There are no datasets with utilization time."
            )
        else:
            path_instrument = self._target_path / "utilization_time" / "instrument"
            path_instrument.mkdir(parents=True, exist_ok=True)
            for instrument, value in instrument_dict.items():
                path_instrument_folder = path_instrument / FileHandler.clean_filename(
                    f"instrument_{value[0]}_ID{instrument}"
                )

                path_instrument_folder.mkdir(parents=True, exist_ok=True)

                fig_dict = self.create_plot_year_duration(
                    value[1:], f"instrument {value[0]} (ID: {instrument})"
                )
                for key, fig in fig_dict.items():
                    path_instrument_year = path_instrument_folder / key
                    path_instrument_year.mkdir(parents=True, exist_ok=True)
                    if fig is not None:
                        self.create_report(
                            path_instrument_year,
                            True,
                            False,
                            f"instrument_{value[0]}_ID{instrument}_{key}_utilization_time",
                            fig,
                        )
                        plt.close(fig)

                fig_dict = self.create_plot_year_month_duration(
                    value[1:], f"instrument {value[0]} (ID: {instrument})"
                )
                for key, fig in fig_dict.items():
                    month = key.split("-")[1]
                    year = key.split("-")[0]
                    path_instrument_month = path_instrument_folder / year / "Months"

                    path_instrument_year.mkdir(parents=True, exist_ok=True)
                    if fig is not None:
                        self.create_report(
                            path_instrument_month,
                            True,
                            False,
                            f"instrument_{value[0]}_ID{instrument}_{month}_{year}_utilization_time",
                            fig,
                        )
                        plt.close(fig)

                fig_dict = self.create_plot_year_calendarWeek_duration(
                    value[1:], f"instrument {value[0]} (ID: {instrument})"
                )
                for key, fig in fig_dict.items():
                    calendar_week = key.split("-")[1]
                    year = key.split("-")[0]
                    path_instrument_cw = path_instrument_folder / year / "CWs"

                    path_instrument_year.mkdir(parents=True, exist_ok=True)
                    if fig is not None:
                        self.create_report(
                            path_instrument_cw,
                            True,
                            False,
                            f"instrument_{value[0]}_ID{instrument}_CW{calendar_week}_{year}_utilization_time",
                            fig,
                        )
                        plt.close(fig)

            fig = self.create_plot_comparison_heatmap_duration(
                instrument_dict, "instruments"
            )
            if fig is not None:
                self.create_report(
                    path_instrument,
                    True,
                    False,
                    "Utilization_of_instruments",
                    fig,
                )
                plt.close(fig)

        self._logger_dur_time.info(
            "Finished generating reports with the statistics for the utilization time of each instrument."
        )
        self._logger_dur_time.info("Finished generating statistic of utilization time.")
