import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from LOGS.Entities import (DatasetRequestParameter, ProjectRequestParameter,
                           SampleRequestParameter)
from LOGS.LOGS import LOGS

from .StatisticHandlerEntities import StatisticHandlerEntities


class StatisticsInstruments(StatisticHandlerEntities):
    """Class for creating the statistics for the instruements.

    Includes the following statistics:
    Which and how many experiments, projects and samples were created per instrument.
    """

    def __init__(
        self,
        logs: LOGS,
        target_path: str = "./statistics",
        begin_date: datetime = None,
        end_date: datetime = None,
        instruments: List = [],
        cutoff: int = 0,
    ):
        """Initialization.

        :param logs: LOGS object to access the LOGS web API,
        :param target_path: The target path, where all statistics should be saved.
        Default: Within the folder containing the script, a new folder "statistics"
        is created in which all statistics are saved.
        :param begin_date: Lowest date limit for statistics to be created.
        :param end_date: Highest date limit for statistics to be created.
        :param instruments: List of instruments to be included in the statistics.
        Default: empty list -> all instruments are included.
        :param cutoff: Only the statistics that correspond to >= the cut-off are displayed.
        """

        self._logger_instruments = logging.getLogger("StatisticInstruments")

        self._logger_instruments.setLevel(logging.INFO)

        logfile_folder = Path(__file__).resolve().parent / "logfiles"
        logfile_folder.mkdir(parents=True, exist_ok=True)
        logfile_path = logfile_folder / "StatisticInstruments.log"
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
        self._instruments = self._validate_list(instruments)
        self.__instrument_path = self._target_path / "instruments"
        self.__cutoff = (
            cutoff
            if isinstance(cutoff, int)
            else (_ for _ in ()).throw(ValueError("Cutoff must be an integer."))
        )

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

    def get_dataset_instruments(self) -> Dict:
        """Retrieves all instruments from the datasets and organizes them in a
        nested dictionary structure.

        Each entry in the dictionary represents an instrument, where the key is the instrument_id
        and the value is a tuple containing:
        - instrument_name: Name of the instrument as a string.
        - projects: A dictionary of all associated projects, where each key is the projectID and the value
        is a list containing the projectName and the number of projects.
        - samples: A dictionary of all associated samples, where each key is the sampleID and the value
        is a list containing the sampleName and the number of samples.
        - experiments: A dictionary of all associated experiments, where each key is the experimentID
        and the value is a list containing the experimentName and the number of experiments.

        :return: A dictionary with the structure:
                {instrument_id: (
                    instrument_name,
                    {projectID: [projectName, num], ...},
                    {sampleID: [sampleName, num], ...},
                    {experimentID: [experimentName, num], ...}
                ), ...}
        """

        instruments = {}

        instruments_total = self._logs.instruments().count
        # Check if there are instruments across all time frames
        if instruments_total == 0:
            self._logger_instruments.info(
                "No instruments found across all time frames."
            )
            return

        self._logger_instruments.info("Processing instruments.")
        count = 0  # Counter for the number of processed instruments
        for instrument in self._logs.instruments():
            # If a filter for instruments is active and the current instrument
            # is not included in the filter, skip the instrument.
            if self._instruments and instrument.id not in self._instruments:
                continue
            instruments[instrument.id] = (instrument.name, {}, {}, {})
            for project in self._logs.projects(ProjectRequestParameter()):
                project_count = self._logs.datasets(
                    DatasetRequestParameter(
                        instrumentIds=[instrument.id],
                        projectIds=[project.id],
                        acquisitionDateFrom=self._begin_date,
                        acquisitionDateTo=self._end_date,
                    )
                ).count
                if project_count > 0:
                    instruments[instrument.id][1][project.id] = [
                        project.name,
                        project_count,
                    ]
            for sample in self._logs.samples(SampleRequestParameter()):
                sample_count = self._logs.datasets(
                    DatasetRequestParameter(
                        instrumentIds=[instrument.id],
                        sampleIds=[sample.id],
                        acquisitionDateFrom=self._begin_date,
                        acquisitionDateTo=self._end_date,
                    )
                ).count
                if sample_count > 0:
                    instruments[instrument.id][2][sample.id] = [
                        sample.name,
                        sample_count,
                    ]
            for experiment in self._logs.experiments():
                experiment_count = self._logs.datasets(
                    DatasetRequestParameter(
                        instrumentIds=[instrument.id],
                        experimentIds=[experiment.id],
                        acquisitionDateFrom=self._begin_date,
                        acquisitionDateTo=self._end_date,
                    )
                ).count
                if experiment_count > 0:
                    instruments[instrument.id][3][experiment.id] = [
                        experiment.name,
                        experiment_count,
                    ]

            if count % 100 == 0 and count != 0:
                self._logger_instruments.info(
                    "%d/%d instruments processed.", count, instruments_total
                )
            count += 1

        self._logger_instruments.info("Finished processing instruments.")

        # If a filter for instruments is active and the "no instrument"
        # option (id 0) is not included in the filter, return a dictionary
        # containing the filtered instruments.
        if self._instruments and 0 not in self._instruments:
            return instruments

        # add datasets without instrument
        self._logger_instruments.info("Processing instrument 'No instrument'.")
        instrument_list = list(instruments.keys())
        instruments[0] = ("No instrument", {}, {}, {})
        for project in self._logs.projects(ProjectRequestParameter()):
            project_count_total = self._logs.datasets(
                DatasetRequestParameter(
                    projectIds=[project.id],
                    acquisitionDateFrom=self._begin_date,
                    acquisitionDateTo=self._end_date,
                )
            ).count
            project_count_instruments = self._logs.datasets(
                DatasetRequestParameter(
                    instrumentIds=instrument_list,
                    projectIds=[project.id],
                    acquisitionDateFrom=self._begin_date,
                    acquisitionDateTo=self._end_date,
                )
            ).count
            project_count = project_count_total - project_count_instruments
            if project_count > 0:
                instruments[0][1][project.id] = [project.name, project_count]
        for sample in self._logs.samples(SampleRequestParameter()):
            sample_count_total = self._logs.datasets(
                DatasetRequestParameter(
                    sampleIds=[sample.id],
                    acquisitionDateFrom=self._begin_date,
                    acquisitionDateTo=self._end_date,
                )
            ).count
            sample_count_instruments = self._logs.datasets(
                DatasetRequestParameter(
                    instrumentIds=instrument_list,
                    sampleIds=[sample.id],
                    acquisitionDateFrom=self._begin_date,
                    acquisitionDateTo=self._end_date,
                )
            ).count
            sample_count = sample_count_total - sample_count_instruments
            if sample_count > 0:
                instruments[0][2][sample.id] = [sample.name, sample_count]
        for experiment in self._logs.experiments():
            experiment_count_total = self._logs.datasets(
                DatasetRequestParameter(
                    experimentIds=[experiment.id],
                    acquisitionDateFrom=self._begin_date,
                    acquisitionDateTo=self._end_date,
                )
            ).count
            experiment_count_instruments = self._logs.datasets(
                DatasetRequestParameter(
                    instrumentIds=instrument_list,
                    experimentIds=[experiment.id],
                    acquisitionDateFrom=self._begin_date,
                    acquisitionDateTo=self._end_date,
                )
            ).count
            experiment_count = experiment_count_total - experiment_count_instruments
            if experiment_count > 0:
                instruments[0][3][experiment.id] = [experiment.name, experiment_count]
        self._logger_instruments.info("Finished processing Instrument 'No instrument'.")

        return instruments

    def create_statistic(self):
        """Generates the statistics for the instruments.

        The statistics are created for the following:
        - Number of projects, samples and experiments per instrument and without instrument.
        """

        self._logger_instruments.info(
            "Starting to generate statistics for instruments."
        )
        instrument_data = self.get_dataset_instruments()
        self.create_plot_instrument(
            self.__instrument_path, instrument_data, cutoff=self.__cutoff
        )
        self._logger_instruments.info("Finished generating statistics for instruments.")
