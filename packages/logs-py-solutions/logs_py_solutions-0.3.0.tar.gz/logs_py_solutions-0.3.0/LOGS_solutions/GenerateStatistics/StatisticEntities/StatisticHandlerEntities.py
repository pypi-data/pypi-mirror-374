import calendar
import logging
import math
from abc import abstractmethod
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from LOGS.LOGS import LOGS
from matplotlib.figure import Figure

from ..Common.CommonHandler import CommonHandler
from ..Common.FileHandler import FileHandler


class StatisticHandlerEntities(CommonHandler):
    """Abstract class for creating statistics."""

    def __init__(
        self,
        logs: LOGS,
        begin_date: str,
        end_date: str,
        target_path: str,
        logger: logging.Logger,
    ):
        """Initialization.

        :param logs: LOGS object to access the LOGS web API,
        :param begin_date: Lowest date limit for statistics to be
            created.
        :param end_date: Highest date limit for statistics to be
            created.
        :param target_path: Path where all datasets should be saved.
        """

        super().__init__(logs, begin_date, end_date, target_path)
        self._logger = logger

    @abstractmethod
    def create_statistic(self):
        """A method responsible for generating statistics.

        This method must be implemented in all subclasses inheriting
        from the base class to ensure that each subclass provides its
        specific implementation of the statistics generation
        functionality.
        """

    def create_csv_file_prep_dis(
        self,
        dictionary_prep: Dict,
        dictionary_dis: Dict,
        dictionary_prep_str: str,
        dictionary_dis_str: str,
        entity: str,
        statistical_unit: str,
        path: Path,
    ):
        """Creates a csv file of the statistics of how many entities (like
        samples) where prepared/created or deleted/modified by the statistical unit (person).
        Used for statistics for entities whose person can prepare and delete.

        :param dictionary_prep: Dictionary with all elements of the unit
            and a sorted list of the preparation/creation data for each element.
            dictionary_prep = {key: [entity_name, date1, date2, ...]}
        :param dictionary_dis: Dictionary with all elements of the unit
            and a sorted list of the discarded or modified data for each
            element.
            dictionary_dis = {key: [entity_name, date1, date2, ...]}
        :param dictionary_prep_str: String indicating whether the
            dictionary contains preparation or creation data, etc. e.g:
            "Prepared"
        :param dictionary_dis_str: String indicating whether the
            dictionary contains discarded or modified data, etc. e.g:
            "Discarded"
        :param entity: Name of the entity that is part of the statistics
            (e.g. dataset for dataset_count)
        :param statistical_unit: Unit for which the statistics were
            prepared (e.g. person)
        :param path: Path where the csv file should be saved
        """

        column_name_prep = (
            f"{dictionary_prep_str}_{entity}_Counts"  # e.g. "Prepared_samples_Counts"
        )
        column_name_dis = (
            f"{dictionary_dis_str}_{entity}_Counts"  # e.g. "Discarded_samples_Counts"
        )

        if not dictionary_prep and not dictionary_dis:
            return

        dictionary_prep_dis_sorted_list = {}
        # Dicionary order: key: entity_id, value: [entity_name, [dates_prep], [dates_dis]]
        # First fill the dictionary with the preparation data
        for key, value in dictionary_prep.items():
            if key not in dictionary_prep_dis_sorted_list:
                dictionary_prep_dis_sorted_list[key] = [
                    value[0],  # entity_name
                    value[1:],  # dates of preparation
                    [],  # no discard data
                ]
            else:
                dictionary_prep_dis_sorted_list[key][1] = (
                    dictionary_prep_dis_sorted_list[key][1] + value[1:]
                )
        # Second fill the dictionary with the discard data
        for key, value in dictionary_dis.items():
            if key not in dictionary_prep_dis_sorted_list:
                dictionary_prep_dis_sorted_list[key] = [
                    value[0],  # entity_name
                    [],  # no preparation data
                    value[1:],  # dates of discard
                ]
            else:
                dictionary_prep_dis_sorted_list[key][2] = (
                    dictionary_prep_dis_sorted_list[key][2] + value[1:]
                )
        # Create a CSV file with the statistic of entity of current statistical unit
        for key, value in dictionary_prep_dis_sorted_list.items():
            if len(value[1]) == 0:
                dates_prep = []
            else:
                dates_prep = sorted(value[1])
            if len(value[2]) == 0:
                dates_dis = []
            else:
                dates_dis = sorted(value[2])

            folder_name = FileHandler.clean_filename(
                f"{statistical_unit}_{value[0]}_ID_{key}"
            )  # Remove unwanted special characters and replace a space with _
            entity_unit_path = Path(path) / folder_name
            entity_unit_path.mkdir(parents=True, exist_ok=True)

            entity_name = FileHandler.clean_filename(value[0])

            aggregated_data_year = pd.DataFrame(
                columns=[
                    "Year",
                    column_name_prep,
                ],
            )
            aggregated_data_month = pd.DataFrame(
                columns=[
                    "Year",
                    "Month",
                    column_name_prep,
                ]
            )
            aggregated_data_week = pd.DataFrame(
                columns=[
                    "Year",
                    "CalendarWeek",
                    column_name_prep,
                ]
            )
            aggregated_data_day = pd.DataFrame(
                columns=[
                    "CalendarWeek",
                    "Day",
                    column_name_prep,
                ]
            )

            # Add the preparation data if available
            if dates_prep:
                df_prep = pd.DataFrame({"Date": dates_prep})
                df_prep["Date"] = pd.to_datetime(df_prep["Date"])
                year, week, day_of_week = zip(
                    *[d.isocalendar() for d in df_prep["Date"]]
                )
                df_prep["Year"] = year
                df_prep["Month"] = df_prep["Date"].dt.month
                df_prep["CalendarWeek"] = week
                df_prep["Day"] = day_of_week

                # data aggregated by year
                aggregated_data_year = df_prep.groupby("Year", as_index=False).agg(
                    **{
                        column_name_prep: ("Date", "count"),
                    }
                )
                # data aggregated by month of the year
                aggregated_data_month = df_prep.groupby(
                    ["Year", "Month"], as_index=False
                ).agg(
                    **{
                        column_name_prep: ("Date", "count"),
                    }
                )
                # data aggregated by calendar week of the year
                aggregated_data_week = df_prep.groupby(
                    ["Year", "CalendarWeek"], as_index=False
                ).agg(
                    **{
                        column_name_prep: ("Date", "count"),
                    }
                )
                # data aggregated by day of the calendar week
                aggregated_data_day = df_prep.groupby(
                    ["CalendarWeek", "Day"], as_index=False
                ).agg(
                    **{
                        column_name_prep: ("Date", "count"),
                    }
                )
            else:
                aggregated_data_year[column_name_prep] = 0
                aggregated_data_month[column_name_prep] = 0
                aggregated_data_week[column_name_prep] = 0
                aggregated_data_day[column_name_prep] = 0

            # Add the discard data if available, otherwise fill with zeros
            if dates_dis:
                df_dis = pd.DataFrame({"Date": dates_dis})
                df_dis["Date"] = pd.to_datetime(df_dis["Date"])
                year, week, day_of_week = zip(
                    *[d.isocalendar() for d in df_dis["Date"]]
                )
                df_dis["Year"] = year
                df_dis["Month"] = df_dis["Date"].dt.month
                df_dis["CalendarWeek"] = week
                df_dis["Day"] = day_of_week

                # Merge the discard data with the preparation data for year, month, calendar week and day
                aggregated_data_year = pd.merge(
                    aggregated_data_year,
                    df_dis.groupby(["Year"], as_index=False).agg(
                        **{
                            column_name_dis: ("Date", "count"),
                        }
                    ),
                    on=["Year"],
                    how="outer",
                )
                aggregated_data_month = pd.merge(
                    aggregated_data_month,
                    df_dis.groupby(["Year", "Month"], as_index=False).agg(
                        **{
                            column_name_dis: ("Date", "count"),
                        }
                    ),
                    on=["Year", "Month"],
                    how="outer",
                )
                aggregated_data_week = pd.merge(
                    aggregated_data_week,
                    df_dis.groupby(["Year", "CalendarWeek"], as_index=False).agg(
                        **{
                            column_name_dis: ("Date", "count"),
                        }
                    ),
                    on=["Year", "CalendarWeek"],
                    how="outer",
                )
                aggregated_data_day = pd.merge(
                    aggregated_data_day,
                    df_dis.groupby(["CalendarWeek", "Day"], as_index=False).agg(
                        **{
                            column_name_dis: ("Date", "count"),
                        }
                    ),
                    on=["CalendarWeek", "Day"],
                    how="outer",
                )
            else:
                aggregated_data_year[column_name_dis] = 0
                aggregated_data_month[column_name_dis] = 0
                aggregated_data_week[column_name_dis] = 0
                aggregated_data_day[column_name_dis] = 0

            # Fill NaN values with 0 and convert to integer
            aggregated_data_year = aggregated_data_year.fillna(0).astype(int)
            aggregated_data_month = aggregated_data_month.fillna(0).astype(int)
            aggregated_data_week = aggregated_data_week.fillna(0).astype(int)
            aggregated_data_day = aggregated_data_day.fillna(0).astype(int)

            # Save the data to a csv file
            entity_name_csv = entity_name.replace("_", " ")
            with open(
                entity_unit_path
                / f"yearly_statistics_{entity}_{statistical_unit}_{entity_name}_ID_{key}.csv",
                "w",
                encoding="utf-8",
                newline="",
            ) as f:
                f.write(
                    f"yearly statistics of {entity} for {statistical_unit} {entity_name_csv} (ID:{key}) from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}\n"
                )
                aggregated_data_year.to_csv(f, index=False, sep=";")

            with open(
                entity_unit_path
                / f"monthly_yearly_statistics_{entity}_{statistical_unit}_{entity_name}_ID_{key}.csv",
                "w",
                encoding="utf-8",
                newline="",
            ) as f:
                f.write(
                    f"monthly yearly statistics of {entity} for {statistical_unit} {entity_name_csv} (ID:{key}) from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}\n"
                )
                aggregated_data_month.to_csv(f, index=False, sep=";")

            with open(
                entity_unit_path
                / f"weekly_yearly_statistics_{entity}_{statistical_unit}_{entity_name}_ID_{key}.csv",
                "w",
                encoding="utf-8",
                newline="",
            ) as f:
                f.write(
                    f"weekly yearly statistics of {entity} for {statistical_unit} {entity_name_csv} (ID:{key}) from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}\n"
                )
                aggregated_data_week.to_csv(f, index=False, sep=";")

            with open(
                entity_unit_path
                / f"daily_weekly_statistics_{entity}_{statistical_unit}_{entity_name}_ID_{key}.csv",
                "w",
                encoding="utf-8",
                newline="",
            ) as f:
                f.write(
                    f"daily weekly statistics of {entity} for {statistical_unit} {entity_name_csv} (ID: {key}) from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}\n"
                )
                aggregated_data_day.to_csv(f, index=False, sep=";")

    def create_csv_file(
        self, sorted_list: List, entity: str, statistical_unit: str, path: str
    ):
        """Creates a csv file of the statistics.

        :param sorted_list: sorted list with all acquisition dates of
            each dataset
        :param entity: Name of the entity that is part of the
            statistics (e.g. dataset for dataset_count)
        :param statistical_unit: Unit for which the statistics were
            prepared
        :param path: Path where the csv file should be saved
        """

        if not sorted_list:
            return
        dates = sorted(sorted_list)

        df = pd.DataFrame({"Date": dates})
        df["Date"] = pd.to_datetime(df["Date"])
        year, week, day_of_week = zip(*[d.isocalendar() for d in df["Date"]])
        df["Year"] = year
        df["Month"] = df["Date"].dt.month
        df["CalendarWeek"] = week
        df["Day"] = day_of_week

        aggregated_data_year = df.groupby("Year", as_index=False).agg(
            **{
                f"{entity}_Counts": ("Date", "size"),
            }
        )

        aggregated_data_month = df.groupby(["Year", "Month"], as_index=False).agg(
            **{
                f"{entity}_Counts": ("Date", "size"),
            }
        )

        aggregated_data_week = df.groupby(["Year", "CalendarWeek"], as_index=False).agg(
            **{
                f"{entity}_Counts": ("Date", "size"),
            }
        )

        aggregated_data_day = df.groupby(["CalendarWeek", "Day"], as_index=False).agg(
            **{
                f"{entity}_Counts": ("Date", "size"),
            }
        )

        # Save the data to a csv file
        statistical_unit_csv = statistical_unit.replace("_", " ")
        statistical_unit = FileHandler.clean_filename(statistical_unit)

        with open(
            path / f"yearly_statistics_{entity}_{statistical_unit}.csv",
            "w",
            encoding="utf-8",
            newline="",
        ) as f:
            f.write(
                f"yearly statistics of {entity} for {statistical_unit_csv} from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}\n"
            )
            aggregated_data_year.to_csv(f, index=False, sep=";")

        with open(
            path / f"monthly_yearly_statistics_{entity}_{statistical_unit}.csv",
            "w",
            encoding="utf-8",
            newline="",
        ) as f:
            f.write(
                f"monthly yearly statistics of {entity} for {statistical_unit_csv} from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}\n"
            )
            aggregated_data_month.to_csv(f, index=False, sep=";")

        with open(
            path / f"weekly_yearly_statistics_{entity}_{statistical_unit}.csv",
            "w",
            encoding="utf-8",
            newline="",
        ) as f:
            f.write(
                f"weekly yearly statistics of {entity} for {statistical_unit_csv} from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}\n"
            )
            aggregated_data_week.to_csv(f, index=False, sep=";")

        with open(
            path / f"daily_weekly_statistics_{entity}_{statistical_unit}.csv",
            "w",
            encoding="utf-8",
            newline="",
        ) as f:
            f.write(
                f"daily weekly statistics of {entity} for {statistical_unit_csv} from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}\n"
            )
            aggregated_data_day.to_csv(f, index=False, sep=";")

    def create_plot_list(
        self,
        dates_list: List,
        entity_path: Path,
        entity: str,
        statistical_unit: str,
        csv_bool: bool,
        show_num: bool = True,
    ):
        """Creates the plots for one entity.

        :param dates_list: The list with the acquisition dates of
            the entity.
        :param entity_path: Path, where the statistic should be saved.
        :param entity: Entity on which the statistics are
            based, e.g.: "samples".
        :param statistical_unit: Entity as instrument for which the statistics are
            generated, e.g.: "logs_group".
        :param csv_bool: Boolean if the csv file should be created or
            not.
        :param show_num: Boolean if the number should be shown in the
            heatmap
        """

        entity_path.mkdir(parents=True, exist_ok=True)

        if not dates_list:
            self._logger.warning(
                f"No data available for the statistic of {entity} of {statistical_unit}."
            )
            return

        # Create html of the statistic as block diagram per year, month-year and heatmap per month-year, week-year and day-week
        self.create_report(
            entity_path,
            True,
            False,
            f"Statistic_{entity}_logs_{statistical_unit}_year_blockdiagram",
            self.create_plot_year(dates_list, f"{entity} of {statistical_unit}"),
        )
        self.create_report(
            entity_path,
            True,
            False,
            f"Statistic_{entity}_logs_{statistical_unit}_month_blockdiagram",
            self.create_blockdiagram_month(
                dates_list, f"{entity} of {statistical_unit}"
            ),
        )
        self.create_report(
            entity_path,
            True,
            False,
            f"Statistic_{entity}_logs_{statistical_unit}_month_heatmap",
            self.create_plot_month(
                dates_list, f"{entity} of {statistical_unit}", show_num
            ),
        )
        self.create_report(
            entity_path,
            True,
            False,
            f"Statistic_{entity}_logs_{statistical_unit}_week_heatmap",
            self.create_plot_week(
                dates_list, f"{entity} of {statistical_unit}", show_num
            ),
        )
        self.create_report(
            entity_path,
            True,
            False,
            f"Statistic_{entity}_logs_{statistical_unit}_day_heatmap",
            self.create_plot_day(
                dates_list, f"{entity} of {statistical_unit}", show_num
            ),
        )

        if csv_bool:
            self.create_csv_file(dates_list, entity, statistical_unit, entity_path)

    def create_plot_of_dict(
        self,
        dictionary: Dict,
        entity_path: Path,
        entity: str,
        statistical_unit: str,
        csv_bool: bool,
        show_num: bool = True,
    ):
        """Creates the plots for all entries in the dictionary.

        :param dictionary: The dictionary with the entries to be plotted.
        :param entity_path: Path, where the statistic should be saved.
        :param entity: Entity on which the statistics are based, e.g.: "Samples prepared" or "Samples".
        :param statistical_unit: Entity for which the statistics are generated, "e.g.: "person".
        :param csv_bool: Boolean if the csv file should be created or not.
        show_num: Boolean if the number should be shown in the heatmap
        """

        if not dictionary:
            self._logger.warning(
                "No data available for the statistic of %s of %s.",
                entity,
                statistical_unit,
            )
            return

        ### Plot statistic of entity and write it in a PDF.
        entity_path.mkdir(parents=True, exist_ok=True)
        for key, value in dictionary.items():
            folder_name = FileHandler.clean_filename(
                f"{statistical_unit}_{value[0]}_ID_{key}"
            )
            entity_inst_path = entity_path / folder_name
            entity_inst_path.mkdir(parents=True, exist_ok=True)

            # Create html of the statistic as block diagram per year, month-year and heatmap per month-year, week-year and day-week
            title = f"{entity} for {statistical_unit} {value[0]} (ID: {key})"
            title = title.replace("_", " ")
            self.create_report(
                entity_inst_path,
                True,
                False,
                f"Statistic_{entity}_{statistical_unit}_ID_{key}_year_blockdiagram",
                self.create_plot_year(value[1:], title),
            )
            self.create_report(
                entity_inst_path,
                True,
                False,
                f"Statistic_{entity}_{statistical_unit}_ID_{key}_month_blockdiagram",
                self.create_blockdiagram_month(value[1:], title),
            )
            self.create_report(
                entity_inst_path,
                True,
                False,
                f"Statistic_{entity}_{statistical_unit}_ID_{key}_month_heatmap",
                self.create_plot_month(value[1:], title, show_num),
            )
            self.create_report(
                entity_inst_path,
                True,
                False,
                f"Statistic_{entity}_{statistical_unit}_ID_{key}_week_heatmap",
                self.create_plot_week(value[1:], title, show_num),
            )
            self.create_report(
                entity_inst_path,
                True,
                False,
                f"Statistic_{entity}_{statistical_unit}_ID_{key}_day_heatmap",
                self.create_plot_day(value[1:], title, show_num),
            )

            ## Create a CSV file with the statistic of current instrument
            if csv_bool == True:
                entity_name = FileHandler.clean_filename(value[0])
                self.create_csv_file(
                    value[1:],
                    entity,
                    f"{statistical_unit} {entity_name} (ID: {key})",
                    entity_inst_path,
                )

    def create_plot_instrument(
        self, entity_path: Path, instrument_data: Dict, cutoff: int = 0
    ):
        """Creates the plots for the extracted data of StatisticInstruments and
        the question "Which and how many experiments, projects and samples were
        created per instrument".

        :param entity_path: Path, where the statistic should be saved.
        :param instrument_data: Dictionary with the instrument data.
        :param cutoff: Cutoff value for the plots.
        """

        for instrument_id, data in instrument_data.items():
            # Create html of the distribution of experiments, samples and projects per instrument
            self.create_report(
                entity_path,
                True,
                False,
                f"Distribution_of experiments_of_{data[0]}_ID_{instrument_id}",
                self.create_plot_instrument_list(
                    instrument_id,
                    data[0],
                    data[3],
                    statistic_entity="experiments",
                    cutoff=cutoff,
                ),
            )

            self.create_report(
                entity_path,
                True,
                False,
                f"Distribution_of_samples_of_{data[0]}_ID_{instrument_id}",
                self.create_plot_instrument_list(
                    instrument_id,
                    data[0],
                    data[2],
                    statistic_entity="samples",
                    cutoff=cutoff,
                ),
            )

            self.create_report(
                entity_path,
                True,
                False,
                f"Distribution_of_projects_of_{data[0]}_ID_{instrument_id}",
                self.create_plot_instrument_list(
                    instrument_id,
                    data[0],
                    data[1],
                    statistic_entity="projects",
                    cutoff=cutoff,
                ),
            )

    def create_plot_year(self, dates_list: List, entity_title: str) -> Figure:
        """Creates a block diagram per year.

        :param dates_list: list with all dates of the entity type.
        :param entity_title: E.g. 'datasets for instrument x'.
        :return: Figure with the block diagram with the title "Number of
            \n {entity_title} \n per year"
        """

        dates = dates_list
        df = pd.DataFrame({"Date": dates})
        df["Date"] = pd.to_datetime(df["Date"])
        df["Year"] = df["Date"].dt.year.astype(str)
        counts_per_year = df.groupby("Year").size()

        # dynamic adjustment of the plot size
        num_dates = len(counts_per_year)
        dynamic_width = max(10, round(num_dates * 0.5))

        # dynamic adjust of the y-axis ticks
        max_y_value = max(counts_per_year.values)
        max_y_value_round = (math.ceil(max_y_value / 10) * 10) if max_y_value > 0 else 1
        step = (max_y_value_round // 10) if max_y_value_round > 0 else 1
        if (max_y_value_round <= 15) or step == 0:
            step = 1
        elif max_y_value_round <= 50:
            step = math.ceil(step / 5) * 5
        else:
            step = math.ceil(step / 10) * 10
        y_ticks = np.arange(0, max_y_value_round + 1, step)
        dynamic_height = 6 + len(y_ticks) * 0.3

        fig, ax = plt.subplots(figsize=(dynamic_width, dynamic_height))
        ax.bar(
            counts_per_year.index.astype(str),
            counts_per_year.values,
            width=0.8,
            align="center",
        )
        ax.grid(
            True,
            which="both",
            axis="y",
            linestyle="-",
            linewidth=0.1,
            color="lightgray",
        )

        ax.set_xlabel("Year")
        ax.set_ylabel(f"Number of {entity_title}")

        ax.set_xticks(range(len(counts_per_year.index)))
        ax.set_xticklabels(
            counts_per_year.index.astype(str),
            rotation=90,
            fontsize=10,
            ha="center",
        )
        # Set the x-axis limits
        fixed_margin_x = 0.2
        ax.set_xlim(0 - 0.4 - fixed_margin_x, num_dates - 0.4)

        # Set y-axis ticks in steps of step
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_ticks)

        plt.title(
            f"Number of \n {entity_title} \n per year from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}",
            loc="center",
        )

        plt.close(fig)

        return fig

    def create_blockdiagram_month(self, dates_list: List, entity_title: str) -> Figure:
        """Creates a block diagram per month.

        :param dates_list: list with all dates of the entity type.
        :param entity_title: E.g. 'datasets for instrument x'.
        :return: Figure with the block diagram with the title "Number of
            \n {entity_title} \n per month and year"
        """

        dates = dates_list
        df = pd.DataFrame({"Date": dates})
        df["Date"] = pd.to_datetime(df["Date"])
        df["Date"] = df["Date"].dt.tz_localize(None)
        df["YearMonth"] = df["Date"].dt.to_period("M")
        counts_per_year_month = df.groupby("YearMonth").size()

        # dynamic adjustment of the plot size
        num_dates = len(counts_per_year_month)
        dynamic_width = max(10, round(num_dates * 0.5))

        # dynamic adjust of the y-axis ticks
        max_y_value = max(counts_per_year_month.values)
        max_y_value_round = (math.ceil(max_y_value / 10) * 10) if max_y_value > 0 else 1
        step = (max_y_value_round // 10) if max_y_value_round > 0 else 1
        if (max_y_value_round <= 15) or step == 0:
            step = 1
        elif max_y_value_round <= 50:
            step = math.ceil(step / 5) * 5
        else:
            step = math.ceil(step / 10) * 10
        y_ticks = np.arange(0, max_y_value_round + 1, step)
        dynamic_height = 6 + len(y_ticks) * 0.3

        fig, ax = plt.subplots(figsize=(dynamic_width, dynamic_height))
        ax.bar(
            counts_per_year_month.index.astype(str),
            counts_per_year_month.values,
            width=0.8,
            align="center",
        )
        ax.grid(
            True,
            which="both",
            axis="y",
            linestyle="-",
            linewidth=0.1,
            color="lightgray",
        )

        ax.set_xlabel("Year-Month")
        ax.set_ylabel(f"Number of {entity_title}")

        ax.set_xticks(range(len(counts_per_year_month.index)))
        ax.set_xticklabels(
            counts_per_year_month.index.astype(str),
            rotation=90,
            fontsize=10,
            ha="center",
        )
        # Set the x-axis limits
        fixed_margin_x = 0.2
        ax.set_xlim(0 - 0.4 - fixed_margin_x, num_dates - 0.4)

        # Set y-axis ticks in steps of step
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_ticks)

        plt.title(
            f"Number of \n {entity_title} \n per month and year from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}",
            loc="center",
        )
        plt.close(fig)

        return fig

    def create_plot_month(
        self, dates_list: List, entity_title: str, show_num: bool = True
    ) -> Figure:
        """Creates a heatmap per month in a year.

        :param dates_list: list with all dates of the entity type
        :param entity_title: E.g. 'datasets for instrument x'
        :param show_num: Boolean if the number should be shown in the
            heatmap
        :return: Figure with the heatmap with the title "Number of \n
            {entity_title} \n per month and year"
        """

        dates = dates_list

        df = pd.DataFrame({"Date": dates})
        df["Date"] = pd.to_datetime(df["Date"])
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month

        heatmap_data = df.groupby(["Year", "Month"]).size().reset_index(name="Counts")

        heatmap_data_pivot = heatmap_data.pivot(
            index="Year", columns="Month", values="Counts"
        ).fillna(0)

        # Set the x and y ticks dynamically
        dynamic_width = max(10, len(heatmap_data_pivot.columns))
        dynamic_height = max(6, len(heatmap_data_pivot.index))

        fig, ax = plt.subplots(figsize=(dynamic_width, dynamic_height))
        cax = ax.matshow(heatmap_data_pivot, cmap="coolwarm")

        if show_num:
            for (i, j), val in np.ndenumerate(heatmap_data_pivot):
                if val != 0:
                    ax.text(j, i, int(val), ha="center", va="center", color="black")

        month_labels = [calendar.month_abbr[i] for i in heatmap_data_pivot.columns]
        plt.xticks(
            np.arange(len(heatmap_data_pivot.columns)), month_labels, rotation=45
        )
        plt.yticks(np.arange(len(heatmap_data_pivot.index)), heatmap_data_pivot.index)

        plt.colorbar(cax)
        plt.title(
            f"Number of \n {entity_title} \n per month and year from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}",
            loc="center",
        )
        plt.xlabel("Month")
        plt.ylabel("Year")
        plt.close(fig)

        return fig

    def create_plot_week(
        self, dates_list: List, entity_title: str, show_num: bool = True
    ) -> Figure:
        """Creates a heat map with the number of data records within a calendar
        week per year.

        ::param dates_list: list with all dates of the entity type
        :param title: E.g. 'datasets for instrument x'
        :param show_num: Boolean if the number should be shown in the heatmap

        :return: Figure with the heatmap with title "Number of \n {entity_type} \n per calendar week and year"
        """

        dates = dates_list

        df = pd.DataFrame({"Date": dates})
        df["Date"] = pd.to_datetime(df["Date"])
        year, week, day_of_week = zip(*[d.isocalendar() for d in df["Date"]])

        df["Year"] = year
        df["CalendarWeek"] = week

        heatmap_data = (
            df.groupby(["Year", "CalendarWeek"]).size().reset_index(name="Counts")
        )
        heatmap_data_pivot = heatmap_data.pivot(
            index="Year", columns="CalendarWeek", values="Counts"
        ).fillna(0)

        num_years = len(heatmap_data_pivot.index)

        # Dynamic adjustment of the plot size
        dynamic_height = max(6, num_years)
        dynamic_width = max(12, len(heatmap_data_pivot.columns))

        fig, ax = plt.subplots(figsize=(dynamic_width, dynamic_height))
        cax = ax.matshow(heatmap_data_pivot, cmap="coolwarm")

        if show_num:
            for (i, j), val in np.ndenumerate(heatmap_data_pivot):
                if val != 0:
                    ax.text(j, i, int(val), ha="center", va="center", color="black")

        week_labels = ["CW " + str(week) for week in heatmap_data_pivot.columns]
        plt.xticks(np.arange(len(heatmap_data_pivot.columns)), week_labels, rotation=90)
        plt.yticks(np.arange(len(heatmap_data_pivot.index)), heatmap_data_pivot.index)

        plt.colorbar(cax)
        plt.title(
            f"Number of \n {entity_title} \n per calendar week and year from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}",
            loc="center",
        )
        plt.ylabel("Year")
        plt.xlabel("Calendar Week")
        plt.close(fig)

        return fig

    def create_plot_day(
        self, dates_list: List, entity_title: str, show_num: bool = True
    ) -> Figure:
        """Creates a heat map with the number of the entitiy within a calendar
        week per month over all years.

        :param dates_list: list with all dates of the entity type
        :param entity_title: E.g. 'datasets for instrument x'
        :param show_num: Boolean if the number should be shown in the
            heatmap
        :return: Figure with the heatmap with title "Number of \n
            {entity_title} \n per day and week over all months and years"
        """

        dates = dates_list

        days_of_week_dict = {
            1: "Mon",
            2: "Tue",
            3: "Wed",
            4: "Thu",
            5: "Fri",
            6: "Sat",
            7: "Sun",
        }

        df = pd.DataFrame({"Date": dates})
        df["Date"] = pd.to_datetime(df["Date"])
        year, week, day_of_week = zip(*[d.isocalendar() for d in df["Date"]])

        df["Week"] = week
        df["Day"] = day_of_week

        # week per month over all years
        heatmap_data = df.groupby(["Week", "Day"]).size().reset_index(name="Counts")
        heatmap_data_pivot = heatmap_data.pivot(
            index="Day", columns="Week", values="Counts"
        ).fillna(0)

        # Dynamic adjustment of the plot size
        dynamic_height = max(6, len(heatmap_data_pivot.index))
        dynamic_width = max(12, len(heatmap_data_pivot.columns))
        fig, ax = plt.subplots(figsize=(dynamic_width, dynamic_height))
        cax = ax.matshow(heatmap_data_pivot, cmap="coolwarm")

        if show_num:
            for (i, j), val in np.ndenumerate(heatmap_data_pivot):
                if val != 0:
                    ax.text(j, i, int(val), ha="center", va="center", color="black")

        week_labels = ["CW " + str(week) for week in heatmap_data_pivot.columns]
        plt.xticks(np.arange(len(heatmap_data_pivot.columns)), week_labels, rotation=90)

        plt.yticks(
            np.arange(len(heatmap_data_pivot.index)),
            heatmap_data_pivot.index.map(days_of_week_dict),
        )

        plt.colorbar(cax)
        plt.title(
            f"Number of \n {entity_title} \n per day and week over all months and years from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}",
            loc="center",
        )
        plt.ylabel("Day")
        plt.xlabel("Calendar Week")
        plt.close(fig)

        return fig

    def create_plot_instrument_list(
        self,
        instrument_id: int,
        instrument_name: str,
        data,
        statistic_entity: str,
        cutoff: int = 0,
    ) -> Figure:
        """Creates a pie chart for the distribution of the statistic entity
        (e.g. Distribution of experiments of instrument x).

        :param instrument_id: ID of the instrument.
        :param instrument_name: Name of the instrument.
        :param data: Data for the distribution.
        :param statistic_entity: Entity for which the distribution is
            created. (e.g. "experiments")
        :param cutoff: Cutoff value for the distribution.
        :return: Figure with the pie chart with the title "Distribution
            of {statistic_entity} of {instrument_name} (ID:
            {instrument_id}) with cutoff {cutoff}" or "Distribution of
            {statistic_entity} of {instrument_name} (ID:
            {instrument_id})"
        """

        total_number = 0
        for key, value in data.items():
            total_number += value[1]
        filtered_data = {k: v for k, v in data.items() if v[1] >= cutoff}

        if not filtered_data:
            if cutoff > 0:
                information_text = f"No data available for the distribution of {statistic_entity} of {instrument_name} (ID: {instrument_id}) with cutoff {cutoff} from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}"
            else:
                information_text = f"No data available for the distribution of {statistic_entity} of {instrument_name} (ID: {instrument_id}) from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}"
            fig, ax = plt.subplots()
            ax.text(
                0.5,
                0.5,
                information_text,
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )
            ax.axis("off")
            plt.close(fig)

            return fig

        labels = [v[0] for v in filtered_data.values()]
        sizes = [v[1] for v in filtered_data.values()]

        sorted_data = sorted(zip(sizes, labels), reverse=True)
        sorted_sizes, sorted_labels = zip(*sorted_data)

        fig, ax = plt.subplots()
        wedges, texts = ax.pie(sorted_sizes, startangle=90)
        ax.axis("equal")

        # cut off test, if wanted include cutoff parameter in function
        legend_labels = [
            f"{label}: {size} ({round(size / total_number*100, 2)}%)"
            for label, size in zip(sorted_labels, sorted_sizes)
            if size >= cutoff
        ]

        plt.legend(
            wedges,
            legend_labels,
            title="Categories",
            loc="upper center",
            bbox_to_anchor=(0.5, -0.1),
            ncol=4,
            fontsize="small",
        )

        if cutoff > 0:
            plt.title(
                f"Distribution of {statistic_entity} of {instrument_name} (ID: {instrument_id}) with cutoff {cutoff} from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}"
            )
        else:
            plt.title(
                f"Distribution of {statistic_entity} of {instrument_name} (ID: {instrument_id}) from {self._begin_date.strftime('%d/%B/%Y')} to {self._end_date.strftime('%d/%B/%Y')}"
            )

        plt.close(fig)

        return fig
