import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from LOGS.Entities import Project, ProjectRequestParameter
from LOGS.LOGS import LOGS

from .StatisticHandlerEntities import StatisticHandlerEntities


class StatisticsProjects(StatisticHandlerEntities):
    """Class for creating the statistics for the projects.

    Includes the following statistics:
    How many projects were created per time unit (day, week, month, year).
    The statistics are output per
    - LOGS group
    - Person (or filtered by a specific person)

    For the statistics of projects per log-group "created on" is used.
    For the statistcs of projects per person "created on" and "modified on" is used.

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

        self._logger_projects = logging.getLogger("StatisticProjects")

        self._logger_projects.setLevel(logging.INFO)

        logfile_folder = Path(__file__).resolve().parent / "logfiles"
        logfile_folder.mkdir(parents=True, exist_ok=True)
        logfile_path = logfile_folder / "StatisticProjects.log"
        if not self._logger_projects.hasHandlers():
            logfile_handler = logging.FileHandler(logfile_path, mode="w")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            logfile_handler.setFormatter(formatter)
            self._logger_projects.addHandler(logfile_handler)

            logconsole_handler = logging.StreamHandler(sys.stdout)
            logconsole_handler.setLevel(logging.INFO)
            logconsole_handler.setFormatter(formatter)
            self._logger_projects.addHandler(logconsole_handler)

        super().__init__(logs, begin_date, end_date, target_path, self._logger_projects)
        self.__project_path = self._target_path / "projects"
        self.__show_num = show_num if isinstance(show_num, bool) else True
        self._persons = self._validate_list(persons)

        if self._begin_date is None:
            self._begin_date = (
                self._logs.projects(ProjectRequestParameter(orderby="CREATED_ON_ASC"))
                .first()
                .createdOn
            )
        if self._end_date is None:
            self._end_date = (
                self._logs.projects(ProjectRequestParameter(orderby="CREATED_ON_DESC"))
                .first()
                .createdOn
            )

    def update_person_dict_project(
        self,
        project: Project,
        project_person_crtd_dict: Dict,
        project_person_mod_dict: Dict,
    ) -> Tuple[Dict, Dict]:
        """Updates the dictionary of persons who created the project and who
        modified the project based on the provided project.

        :param project: The project from which person details and created date and discard date are extracted.
        :param project_person_crtd_dict: Dictionary of all persons with a list of the creation date of their created projects.
        :param project_person_mod_dict: Dictionary of all persons with a list of the modification date of their modified projects.

        :return: An tuple of two updated dictionaries (project_person_crtd_dict, project_person_mod_dict),
        where each key is an person ID and each value is a list with the person name as the first element followed by all
        creation dates/modification dates (both existing and newly added).
        Structure:
        project_person_crtd_dict: {person_id: [person_name, creationDate1, creationDate2, ...]}
        project_person_mod_dict: {person_id: [person_name, modificationDate1, modificationDate2, ...]}
        """

        if project.createdBy is None:
            if not self._persons or "No Person" in self._persons:
                if "No Person" not in project_person_crtd_dict:
                    project_person_crtd_dict["No Person"] = [" "]
                project_person_crtd_dict["No Person"].append(project.createdOn)
        else:
            if not self._persons or project.createdBy.id in self._persons:
                if project.createdBy.id not in project_person_crtd_dict:
                    project_person_crtd_dict[project.createdBy.id] = [
                        project.createdBy.name
                    ]
                project_person_crtd_dict[project.createdBy.id].append(project.createdOn)

        # If the project was modified
        if project.modifiedOn:
            # Skip projects with invalid modification date
            tz = project.modifiedOn.tzinfo
            if (datetime(1677, 9, 21, tzinfo=tz) >= project.modifiedOn) or (
                project.modifiedOn >= datetime(2262, 4, 11, tzinfo=tz)
            ):
                self._logger_projects.warning(
                    "Project has invalid modification date: %s. Modification date will not be included in the statistics.",
                    project.modifiedOn,
                )
                return (project_person_crtd_dict, project_person_mod_dict)

            if not project.modifiedBy:
                if not self._persons or "No Person" in self._persons:
                    if "No Person" not in project_person_mod_dict:
                        project_person_mod_dict["No Person"] = [" "]
                    project_person_mod_dict["No Person"].append(project.modifiedOn)
            else:
                if not self._persons or project.modifiedBy.id in self._persons:
                    if project.modifiedBy.id not in project_person_mod_dict:
                        project_person_mod_dict[project.modifiedBy.id] = [
                            project.modifiedBy.name
                        ]
                    project_person_mod_dict[project.modifiedBy.id].append(
                        project.modifiedOn
                    )

        return (project_person_crtd_dict, project_person_mod_dict)

    def create_statistic(self):
        """Generates the statistics for the projects.

        Includes the following statistics:
        How many projects were created per time unit (day, week, month, year).
        The statistics are output per
        - LOGS group
        - Person (or filtered by a specific person)

        For the statistics of projects per logs-group "created on" is used.
        For the statistcs of projects per person "created on" and "modified on" is used.

        The result is a CSV file per person, logs-group and instrument and a pdf per logs-group, person and instrument.
        """

        self._logger_projects.info("Starting to generate statistics for projects.")

        # Dictionary of the persons who created the project
        project_person_crtd_dict = {}
        # Dictionary of the persons who modified the project
        projects_person_mod_dict = {}
        # List of the creation time of all projects created in the given time frame
        projects_filtered_list = []

        # Count the number of projects in the given time frame for process information
        projects_total = self._logs.projects(
            ProjectRequestParameter(
                createdFrom=self._begin_date, createdTo=self._end_date
            )
        ).count

        # Check if there are projects in the given time frame
        if projects_total == 0:
            self._logger_projects.info("No projects found in the given time frame.")
            return

        self._logger_projects.info(
            "Processing projects in the given time frame: begin date: %s - end date: %s.",
            self._begin_date,
            self._end_date,
        )
        count = 0  # Counter for the number of processed projects
        for project in self._logs.projects(
            ProjectRequestParameter(
                createdFrom=self._begin_date, createdTo=self._end_date
            )
        ):
            # Skip projects with invalid creation date
            tz = project.createdOn.tzinfo
            if (
                (project.createdOn is None)
                or (datetime(1677, 9, 21, tzinfo=tz) >= project.createdOn)
                or (project.createdOn >= datetime(2262, 4, 11, tzinfo=tz))
            ):
                self._logger_projects.warning(
                    "Project %s has invalid creation date: %s. Project will not be included in the statistics.",
                    project.id,
                    project.createdOn,
                )
                continue

            # Add the creation date of the project to the list
            projects_filtered_list.append(project.createdOn)

            # Update the dictionaries of persons who created and modified the project
            (
                project_person_crtd_dict,
                projects_person_mod_dict,
            ) = self.update_person_dict_project(
                project, project_person_crtd_dict, projects_person_mod_dict
            )

            if count % 5000 == 0 and count != 0:
                self._logger_projects.info(
                    "%d/%d projects processed.",
                    count,
                    projects_total,
                )

            count += 1

        self._logger_projects.info("Finished processing projects.")

        ### Create plots and csv files for logs-group
        projects_sorted_list = sorted(projects_filtered_list)
        path_logs_group = self.__project_path / "logs_group"
        super().create_plot_list(
            projects_sorted_list,
            path_logs_group,
            "projects",
            "logs-group",
            True,
            self.__show_num,
        )

        ### Create plots and csv files for persons
        path_person = self.__project_path / "person"
        super().create_plot_of_dict(
            project_person_crtd_dict,
            path_person,
            "created_projects",
            "person",
            False,
            show_num=self.__show_num,
        )
        super().create_plot_of_dict(
            projects_person_mod_dict,
            path_person,
            "last_modified_projects",
            "person",
            False,
            show_num=self.__show_num,
        )

        super().create_csv_file_prep_dis(
            project_person_crtd_dict,
            projects_person_mod_dict,
            "Created",
            "Last Modified",
            "projects",
            "person",
            path_person,
        )

        self._logger_projects.info("Finished generating statistics for projects.")
