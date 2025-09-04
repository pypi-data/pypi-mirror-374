import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from LOGS.Entities import DatasetRequestParameter
from LOGS.LOGS import LOGS

from ..Common.FileHandler import FileHandler
from .StatisticHandlerNMR import StatisticHandlerNMR


class StatisticsTypesOfExperiments(StatisticHandlerNMR):
    """This class provides methods to create statistics for the different types of NMR experiments and save them as HTML or PDF files."""

    def __init__(
        self,
        logs: LOGS,
        begin_date: datetime = None,
        end_date: datetime = None,
        target_path: str = None,
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API,
        :param begin_date: Lowest date limit for statistics to be created.
        :param end_date: Highest date limit for statistics to be created.
        :param target_path: Path where all datasets should be saved.
        """

        self._logger_instruments = logging.getLogger("StatisticsTypesInstruments")

        self._logger_instruments.setLevel(logging.INFO)

        logfile_folder = Path(__file__).resolve().parent / "logfiles"
        logfile_folder.mkdir(parents=True, exist_ok=True)
        logfile_path = logfile_folder / "StatisticsTypesInstruments.log"
        if not self._logger_instruments.hasHandlers():
            logfile_handler = logging.FileHandler(logfile_path, mode="w")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            logfile_handler.setFormatter(formatter)
            self._logger_instruments.addHandler(logfile_handler)

            logconsole_handler = logging.StreamHandler(sys.stdout)
            logconsole_handler.setLevel(logging.INFO)
            logconsole_handler.setFormatter(formatter)
            self._logger_instruments.addHandler(logconsole_handler)

        super().__init__(
            logs, begin_date, end_date, target_path, self._logger_instruments
        )
        # self._instruments = self._validate_list(instruments)
        self.__instrument_path = self._target_path / "types_of_instruments"

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

    def get_dataset_instruments(self) -> Dict[int, Tuple[str, Dict[str, int]]]:
        """Get all instruments of the datasets and count the number of each type of experiment per instrument.

        :return: Dictionary with instrument ID as key and a tuple with instrument name and a dictionary with experiment type as key and count as value.
        """

        # Get the total number of datasets with the format "BrukerNMR" in the given time frame
        datasets_total = self._logs.datasets(
            DatasetRequestParameter(
                acquisitionDateFrom=self._begin_date,
                acquisitionDateTo=self._end_date,
                formatIds=["BrukerNMR"],
            )
        ).count

        if datasets_total == 0:
            self._logger_instruments.warning(
                "No datasets with format 'BrukerNMR' found in the given time frame."
            )
            return {}

        self._logger_instruments.info(
            "Processing instruments with format 'BrukerNMR' in the given time frame: begin date: %s - end date: %s.",
            self._begin_date.strftime("%d/%B/%Y"),
            self._end_date.strftime("%d/%B/%Y"),
        )
        instruments = {}  # {instrument_id: (instrument_name, {experiment_type: count})}
        count = 0
        # Get all datasets with format "BrukerNMR" and acquisition date between begin_date and end_dates
        # and count the number of each type of experiment per instrument
        for dataset in self._logs.datasets(
            DatasetRequestParameter(
                acquisitionDateFrom=self._begin_date,
                acquisitionDateTo=self._end_date,
                formatIds=["BrukerNMR"],
            )
        ):
            # Skip datasets with invalid acquisition date
            tz = dataset.acquisitionDate.tzinfo
            if (
                (dataset.acquisitionDate is None)
                or (datetime(1677, 9, 21, tzinfo=tz) >= dataset.acquisitionDate)
                or (dataset.acquisitionDate >= datetime(2262, 4, 11, tzinfo=tz))
            ):
                self._logger_instruments.warning(
                    "Dataset %s has invalid acquisition date.: %s. Dataset will not be included in the statistics.",
                    dataset.id,
                    dataset.acquisitionDate,
                )
                continue

            if dataset.instrument is None:
                dataset_instrument_id = 0
                dataset_instrument_name = "No instrument"
            else:
                dataset_instrument_id = dataset.instrument.id
                dataset_instrument_name = dataset.instrument.name
            if dataset_instrument_id not in instruments:
                instruments[dataset_instrument_id] = (
                    dataset_instrument_name,
                    {},
                )

            dataset.fetchParameters()
            if (
                dataset.parameters.get("General acquisition parameters/Dimension")
                is not None
            ):
                if (
                    dataset.parameters["General acquisition parameters/Dimension"]
                    not in instruments[dataset_instrument_id][1]
                ):
                    instruments[dataset_instrument_id][1][
                        dataset.parameters["General acquisition parameters/Dimension"]
                    ] = 1
                else:
                    instruments[dataset_instrument_id][1][
                        dataset.parameters["General acquisition parameters/Dimension"]
                    ] += 1
            else:
                # If the dataset has no dimension, create a CSV file with the dataset ID and instrument ID
                # and instrument name
                # create "No dimension" in the instruments dictionary and add 1 to the count

                self.__instrument_path.mkdir(parents=True, exist_ok=True)
                csv_path = self.__instrument_path / "no_dimension.csv"
                file_exists = csv_path.is_file()

                with open(
                    csv_path,
                    "a",
                ) as file:
                    if not file_exists:
                        writer = csv.writer(file)
                        writer.writerow(
                            [
                                "Dataset ID",
                                "Instrument ID",
                                "Instrument Name",
                            ]
                        )
                    writer = csv.writer(file)
                    writer.writerow(
                        [
                            dataset.id,
                            dataset_instrument_id,
                            dataset_instrument_name,
                        ]
                    )
                if "No dimension" not in instruments[dataset_instrument_id][1]:
                    instruments[dataset_instrument_id][1]["No dimension"] = 1
                else:
                    instruments[dataset_instrument_id][1]["No dimension"] += 1
            if count % 10000 == 0 and count != 0:
                self._logger_instruments.info(
                    "%d/%d datasets processed.", count, datasets_total
                )
            count += 1

        self._logger_instruments.info(
            "Finished getting all datasets with format 'BrukerNMR' in the given date range."
        )

        return instruments

    def create_statistic(self):
        """Create the statistics of the different types of NMR experiments of each instrument."""

        self._logger_instruments.info(
            "Starting to generate a statistical analysis of the different types of NMR experiments of each instrument."
        )

        instruments = self.get_dataset_instruments()

        self._logger_instruments.info(
            "Creating reports with a statistical analysis of the different types of NMR experiments."
        )

        for instrument_id, value in instruments.items():
            instrument_name = FileHandler.clean_filename(value[0])
            self.create_report(
                self.__instrument_path,
                True,
                False,
                f"Types_of_NMR_experiments_of_{instrument_name}_ID{instrument_id})",
                self.create_plot_instrument_num(
                    instrument_id,
                    value[0],
                    value[1],
                ),
            )

        self._logger_instruments.info(
            "Finished generating reports with a statistical analysis of the different types of NMR experiments."
        )
        self._logger_instruments.info(
            "Finished generating a statistical analysis of the different types of NMR experiments of each instrument."
        )
