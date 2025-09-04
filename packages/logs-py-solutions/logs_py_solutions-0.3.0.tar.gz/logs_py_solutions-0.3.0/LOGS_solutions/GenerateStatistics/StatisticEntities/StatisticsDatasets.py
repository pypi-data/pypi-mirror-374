import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from LOGS.Entities import Dataset, DatasetRequestParameter
from LOGS.LOGS import LOGS

from .StatisticHandlerEntities import StatisticHandlerEntities


class StatisticsDatasets(StatisticHandlerEntities):
    """
    Class for creating the statistics for the data sets.
    Includes the following statistics:
    How many data sets were created per time unit (day, week, month, year). The acquisition date is used.
    The statistics are output per
    - LOGS group
    - Person (or filtered by a specific person)
    - Instrument (or filtered by a specific person)

    The result is a CSV file per person, logs-group and instrument and a pdf per logs-group, person and instrument.
    """

    def __init__(
        self,
        logs: LOGS,
        target_path: str = "./statistics",
        begin_date: datetime = None,
        end_date: datetime = None,
        show_num: bool = True,
        persons: List = [],
        instruments: List = [],
    ):
        """Initialization.

        :param logs: LOGS object to access the LOGS web API,
        :param target_path: The target path, where all statistics should be saved.
        Default: Within the folder containing the script, a new folder "statistics"
        is created in which all statistics are saved.
        :param begin_date: Lowest date limit for statistics to be created.
        :param end_date: Highest date limit for statistics to be created.
        :param show_num: Boolean to show the number of data sets in the heatmap.
        Default: True
        :param persons: List of persons to be included in the statistics.
        Default: empty list -> all persons are included.
        :param instruments: List of instruments to be included in the statistics.
        Default: empty list -> all instruments are included.
        """

        self._logger_datasets = logging.getLogger("StatisticDatasets")

        self._logger_datasets.setLevel(logging.INFO)

        logfile_folder = Path(__file__).resolve().parent / "logfiles"
        logfile_folder.mkdir(parents=True, exist_ok=True)
        logfile_path = logfile_folder / "StatisticDatasets.log"
        if not self._logger_datasets.hasHandlers():
            logfile_handler = logging.FileHandler(logfile_path, mode="w")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            logfile_handler.setFormatter(formatter)
            self._logger_datasets.addHandler(logfile_handler)

            logconsole_handler = logging.StreamHandler(sys.stdout)
            logconsole_handler.setLevel(logging.INFO)
            logconsole_handler.setFormatter(formatter)
            self._logger_datasets.addHandler(logconsole_handler)

        super().__init__(logs, begin_date, end_date, target_path, self._logger_datasets)
        self.__dataset_path = self._target_path / "dataset"
        self.__show_num = show_num if isinstance(show_num, bool) else True
        self._persons = self._validate_list(persons)
        self._instruments = self._validate_list(instruments)

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

    def update_instrument_dict(
        self, dataset: Dataset, dataset_instrument_dict: Dict
    ) -> Dict:
        """Updates the dictionary of instruments based on the provided dataset.
        The dictionary is updated with the instrument associated with the data
        set. The acquisition date is added to the associated list in the
        dictionary.

        :param dataset: The dataset from which instrument details and acquisition dates are extracted.
        :param dataset_instrument_dict: A dictionary mapping instrument IDs to lists that contain the
                                        instrument's name and previously recorded acquisition dates.
                                        Structure: {instrument_id: [instrument_name, ...acquisition_dates]}

        :return: An updated dictionary where each key is an instrument ID and each value is a list with the
                instrument name as the first element followed by all acquisition dates (both existing and newly added).
                Structure: {instrument_id: [instrument_name, acquisition_date1, acquisition_date2, ...]}
        """

        # If the data set has no instrument add it to the dictionary
        if dataset.instrument is None or dataset.instrument == "":
            if not self._instruments or 0 in self._instruments:
                if 0 not in dataset_instrument_dict:
                    dataset_instrument_dict[0] = ["No Instrument"]
                dataset_instrument_dict[0].append(dataset.acquisitionDate)
                return dataset_instrument_dict
        else:
            # If a filter for instruments is active and the current instrument is not
            # included in the filter, skip the instrument.
            if self._instruments and dataset.instrument.id not in self._instruments:
                return dataset_instrument_dict

            # If the filter is active and the current instrument is included in the filter,
            # update the dictionary
            elif self._instruments and dataset.instrument.id in self._instruments:
                if dataset.instrument.id not in dataset_instrument_dict:
                    dataset_instrument_dict[dataset.instrument.id] = [
                        dataset.instrument.name
                    ]

                dataset_instrument_dict[dataset.instrument.id].append(
                    dataset.acquisitionDate
                )
                return dataset_instrument_dict

            # If no filter is active, update the dictionary
            elif not self._instruments:
                if dataset.instrument.id not in dataset_instrument_dict:
                    dataset_instrument_dict[dataset.instrument.id] = [
                        dataset.instrument.name
                    ]
                dataset_instrument_dict[dataset.instrument.id].append(
                    dataset.acquisitionDate
                )
                return dataset_instrument_dict

        return dataset_instrument_dict

    def update_person_dict_dataset(
        self, dataset: Dataset, dataset_person_dict: Dict
    ) -> Dict:
        """Updates the dictionary of persons based on the provided dataset. The
        dictionary is updated with the persons associated with the data set.
        The acquisition date is added to the associated list in the dictionary.

        :param dataset: The dataset from which person details and acquisition dates are extracted.
        :param dataset_person_dict: A dictionary mapping person IDs to lists that contain the
                                        person's name and previously recorded acquisition dates.
                                        Structure: {person-id: [person-name, ...acquisition_dates]}

        :return: An updated dictionary where each key is an person ID and each value is a list with the
                person name as the first element followed by all acquisition dates (both existing and newly added).
                Structure: {person_id: [person_name, acquisition_date1, acquisition_date2, ...]}
        """

        if dataset.operators is None:
            if not self._persons or 0 in self._persons:
                if 0 not in dataset_person_dict:
                    dataset_person_dict[0] = ["No Person"]
                dataset_person_dict[0].append(dataset.acquisitionDate)
        else:
            for person in dataset.operators:
                if self._persons and person.id not in self._persons:
                    continue
                if person.id not in dataset_person_dict:
                    dataset_person_dict[person.id] = [person.name]

                dataset_person_dict[person.id].append(dataset.acquisitionDate)

        return dataset_person_dict

    def create_statistic(self):
        """
        Generates the statistics for the datasets.
        The statistics include:
        How many projects, samples and data sets were created per time unit (day, week, month, year). The acquisition date is used.
        The statistics are output per
        - LOGS group
        - Person (or filtered by a specific person)
        - Instrument (or filtered by a specific person) (only for statistic of data sets)

        The result is a CSV file per person, logs group and instrument and a pdf per logs group, person and instrument.
        """

        self._logger_datasets.info("Starting to generate statistics for datasets.")

        # Dictionary for statistic of persons
        dataset_person_dict = {}
        # Dictionary for statistic of instruments
        dataset_instrument_dict = {}
        # List for statistic of LOGS logs group, it includes the acquisition date of each dataset
        datasets_filtered_list = []
        # Count the number of datasets in the given time frame for process informations
        datasets_total = self._logs.datasets(
            DatasetRequestParameter(
                acquisitionDateFrom=self._begin_date,
                acquisitionDateTo=self._end_date,
            )
        ).count

        # Check if there are datasets in the given time frame
        if datasets_total == 0:
            self._logger_datasets.info("No datasets found in the given time frame.")
            return

        self._logger_datasets.info(
            "Processing datasets in the given time frame: begin date: %s - end date: %s.",
            self._begin_date,
            self._end_date,
        )
        count = 0  # Counter for the number of processed datasets
        for dataset in self._logs.datasets(
            DatasetRequestParameter(
                acquisitionDateFrom=self._begin_date, acquisitionDateTo=self._end_date
            )
        ):
            # Skip datasets with invalid acquisition date
            tz = dataset.acquisitionDate.tzinfo
            if (
                (dataset.acquisitionDate is None)
                or (datetime(1677, 9, 21, tzinfo=tz) >= dataset.acquisitionDate)
                or (dataset.acquisitionDate >= datetime(2262, 4, 11, tzinfo=tz))
            ):
                self._logger_datasets.warning(
                    "Dataset %d has invalid acquisition date: %s. Dataset will not be included in the statistics.",
                    dataset.id,
                    dataset.acquisitionDate,
                )
                continue

            datasets_filtered_list.append(dataset.acquisitionDate)

            # Instrument
            dataset_instrument_dict = self.update_instrument_dict(
                dataset, dataset_instrument_dict
            )

            # Person
            dataset_person_dict = self.update_person_dict_dataset(
                dataset, dataset_person_dict
            )

            if count % 10000 == 0 and count != 0:
                self._logger_datasets.info(
                    "%d/%d datasets processed.",
                    count,
                    datasets_total,
                )
            count += 1

        self._logger_datasets.info("Finished processing datasets.")

        # Sort list by acquisition date
        datasets_sorted_list = sorted(datasets_filtered_list)
        # Sort the list of data sets of the individual instruments by date
        for ins_key, value in dataset_instrument_dict.items():
            sorted_list = sorted(value[1:])
            dataset_instrument_sorted_list = [value[0]] + sorted_list
            dataset_instrument_dict[ins_key] = dataset_instrument_sorted_list

        for ins_key, value in dataset_person_dict.items():
            sorted_list = sorted(value[1:])
            dataset_person_sorted_list = [value[0]] + sorted_list
            dataset_person_dict[ins_key] = dataset_person_sorted_list

        ### Plot statistic of LOGS logs-group and write it in a PDF.
        path_logs_group = self.__dataset_path / "logs_group"
        self.create_plot_list(
            datasets_sorted_list,
            path_logs_group,
            "datasets",
            "logs-group",
            csv_bool=True,
            show_num=self.__show_num,
        )

        ### Plot statistic of instruments and write it in a PDF.
        path_instrument = self.__dataset_path / "instrument"
        self.create_plot_of_dict(
            dataset_instrument_dict,
            path_instrument,
            "datasets",
            "instrument",
            csv_bool=True,
            show_num=self.__show_num,
        )

        ### Plot statistic of persons and write it in a PDF.
        path_person = self.__dataset_path / "person"
        self.create_plot_of_dict(
            dataset_person_dict,
            path_person,
            "datasets",
            "person",
            csv_bool=True,
            show_num=self.__show_num,
        )

        self._logger_datasets.info("Finished generating statistics for datasets.")
