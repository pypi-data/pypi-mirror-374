import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from LOGS.Entities import Sample, SampleRequestParameter
from LOGS.LOGS import LOGS

from .StatisticHandlerEntities import StatisticHandlerEntities


class StatisticsSamples(StatisticHandlerEntities):
    """Class for creating the statistics for the samples.

    Includes the following statistics:
    How many samples were created per time unit (day, week, month, year).
    The statistics are output per
    - LOGS group
    - Person (or filtered by a specific person)

    For the statistics of samples per logs-group "prepared at" is used.
    For the statistcs of samples per person "prepared at" and "discarded at" is used.

    The result is a CSV file per person and logs-group and a pdf per logs-group, person and instrument.
    """

    def __init__(
        self,
        logs: LOGS,
        target_path: str = "./statistics",
        begin_date: datetime = None,
        end_date: datetime = None,
        show_num: bool = True,
        persons: List = [],
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
        """

        self._logger_samples = logging.getLogger("StatisticSamples")

        self._logger_samples.setLevel(logging.INFO)

        logfile_folder = Path(__file__).resolve().parent / "logfiles"
        logfile_folder.mkdir(parents=True, exist_ok=True)
        logfile_path = logfile_folder / "StatisticSamples.log"
        if not self._logger_samples.hasHandlers():
            logfile_handler = logging.FileHandler(logfile_path, mode="w")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            logfile_handler.setFormatter(formatter)
            self._logger_samples.addHandler(logfile_handler)

            logconsole_handler = logging.StreamHandler(sys.stdout)
            logconsole_handler.setLevel(logging.INFO)
            logconsole_handler.setFormatter(formatter)
            self._logger_samples.addHandler(logconsole_handler)

        super().__init__(logs, begin_date, end_date, target_path, self._logger_samples)
        self.__sample_path = self._target_path / "sample"
        self.__show_num = show_num if isinstance(show_num, bool) else True
        self._persons = self._validate_list(persons)

        if self._begin_date is None:
            self._begin_date = (
                self._logs.samples(
                    SampleRequestParameter(orderby="PREPARATION_DATE_ASC")
                )
                .first()
                .preparedAt
            )
        if self._end_date is None:
            self._end_date = (
                self._logs.samples(
                    SampleRequestParameter(orderby="PREPARATION_DATE_DESC")
                )
                .first()
                .preparedAt
            )

    def update_person_dict_sample(
        self,
        sample: Sample,
        sample_person_prep_dict: Dict,
        sample_person_dis_dict: Dict,
    ) -> Tuple[Dict, Dict]:
        """Updates the dictionary of persons who prepared the sample and who
        discarded the sample based on the provided sample. Only data where the date is provided is considered.

        :param sample: The sample from which person details and preparation date and discard date are extracted.
        :param sample_person_prep_dict: Dictionary of all persons with a list of the preparation date of their prepared samples.
        :param sample_person_dis_dict: Dictionary of all persons with a list of the discard date of their discarded samples.

        :return: An tuple of two updated dictionaries (sample_person_prep_dict, sample_person_dis_dict),
        where each key is an person ID and each value is a list with the person name as the first element followed by all
        preparation dates/discard dates (both existing and newly added).
        Structure:
        sample_person_prep_dict: {person_id: [person_name, preparationDate1, preparationDate2, ...]}
        sample_person_dis_dict: {person_id: [person_name, discardDate1, discardDate2, ...]}
        """

        if not sample.preparedBy:
            if not self._persons or "No Person" in self._persons:
                if "No Person" not in sample_person_prep_dict:
                    sample_person_prep_dict["No Person"] = [" "]
                sample_person_prep_dict["No Person"].append(sample.preparedAt)
        else:
            for person in sample.preparedBy:
                if self._persons and person.id not in self._persons:
                    continue
                if person.id not in sample_person_prep_dict:
                    sample_person_prep_dict[person.id] = [person.name]

                sample_person_prep_dict[person.id].append(sample.preparedAt)

        # If the date of the discard is provided, update the dictionary of persons who discarded the sample
        if sample.discardedAt:
            # Skip samples with invalid discard date
            tz = sample.discardedAt.tzinfo
            if (datetime(1677, 9, 21, tzinfo=tz) >= sample.discardedAt) or (
                (sample.discardedAt) >= datetime(2262, 4, 11, tzinfo=tz)
            ):
                self._logger_samples.warning(
                    "Sample %s has invalid discard date: %s. Discard date will not be included in the statistics.",
                    sample.id,
                    sample.discardedAt,
                )
                return (sample_person_prep_dict, sample_person_dis_dict)

            if not sample.discardedBy:
                if not self._persons or "No Person" in self._persons:
                    if "No Person" not in sample_person_dis_dict:
                        sample_person_dis_dict["No Person"] = [" "]
                    sample_person_dis_dict["No Person"].append(sample.discardedAt)
            else:
                for person in sample.discardedBy:
                    if self._persons and person.id not in self._persons:
                        continue
                    if person.id not in sample_person_dis_dict:
                        sample_person_dis_dict[person.id] = [person.name]
                    sample_person_dis_dict[person.id].append(sample.discardedAt)

        return (sample_person_prep_dict, sample_person_dis_dict)

    def create_statistic(self):
        """
        Generates the statistics for the samples.
        Includes the following statistics:
        How many samples were created per time unit (day, week, month, year).
        The statistics are output per
        - LOGS group
        - Person (or filtered by a specific person)

        For the statistics of samples per logs-group "prepared at" is used.
        For the statistcs of samples per person "prepared at" and "discarded at" is used.

        The result is a CSV file per person and logs-group and a pdf per logs-group, person and instrument.
        """

        self._logger_samples.info("Starting to generate statistics for samples.")

        # Dictionary of the persons who prepared the sample
        samples_person_prep_dict = {}
        # Dictionary of the persons who discarded the sample
        samples_person_dis_dict = {}
        # List of the preparation time of all samples prepared in the given time frame
        samples_filtered_list = []

        # Count the number of samples in the given time frame for process information
        samples_total = self._logs.samples(
            SampleRequestParameter(
                preparedAtFrom=self._begin_date, preparedAtTo=self._end_date
            )
        ).count

        # Check if there are samples in the given time frame
        if samples_total == 0:
            self._logger_samples.info("No samples found in the given time frame.")
            return

        self._logger_samples.info(
            "Processing samples in the given time frame: begin date: %s - end date: %s.",
            self._begin_date,
            self._end_date,
        )
        count = 0  # Counter for the number of processed samples
        for sample in self._logs.samples(
            SampleRequestParameter(
                preparedAtFrom=self._begin_date, preparedAtTo=self._end_date
            )
        ):
            # Skip samples with invalid preparation date
            tz = sample.preparedAt.tzinfo
            if (
                (sample.preparedAt is None)
                or (datetime(1677, 9, 21, tzinfo=tz) >= sample.preparedAt)
                or (sample.preparedAt >= datetime(2262, 4, 11, tzinfo=tz))
            ):
                self._logger_samples.warning(
                    "Sample %s has invalid preparation date: %s. Sample will not be included in the statistics.",
                    sample.id,
                    sample.preparedAt,
                )
                continue
            # Add the preparation date of the sample to the list
            samples_filtered_list.append(sample.preparedAt)

            # Update the dictionaries of persons who prepared and discarded the sample
            (
                samples_person_prep_dict,
                samples_person_dis_dict,
            ) = self.update_person_dict_sample(
                sample, samples_person_prep_dict, samples_person_dis_dict
            )

            if count % 5000 == 0 and count != 0:
                self._logger_samples.info(
                    "%s/%s samples processed.", count, samples_total
                )

            count += 1

        self._logger_samples.info("Finished processing samples.")

        ### Create plots and csv files for logs-group
        samples_sorted_list = sorted(samples_filtered_list)
        path_logs_group = self.__sample_path / "logs_group"
        self.create_plot_list(
            samples_sorted_list,
            path_logs_group,
            "samples",
            "logs-group",
            True,
            show_num=self.__show_num,
        )

        ### Create plots and csv files for logs-group
        path_person = self.__sample_path / "person"
        self.create_plot_of_dict(
            samples_person_prep_dict,
            path_person,
            "prepared_samples",
            "person",
            False,
            show_num=self.__show_num,
        )
        self.create_plot_of_dict(
            samples_person_dis_dict,
            path_person,
            "discarded_samples",
            "person",
            False,
            show_num=self.__show_num,
        )

        self.create_csv_file_prep_dis(
            samples_person_prep_dict,
            samples_person_dis_dict,
            "Prepared",
            "Discarded",
            "samples",
            "person",
            path_person,
        )

        self._logger_samples.info("Finished generating statistics for samples.")
