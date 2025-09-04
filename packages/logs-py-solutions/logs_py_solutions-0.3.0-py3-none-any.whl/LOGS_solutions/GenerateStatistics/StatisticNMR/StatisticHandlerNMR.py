import logging
import sys
from abc import abstractmethod
from datetime import datetime
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from LOGS.LOGS import LOGS
from matplotlib.figure import Figure

from ..Common.CommonHandler import CommonHandler
from ..Common.DateHandler import DateHandler


class StatisticHandlerNMR(CommonHandler):
    """Abstract class for creating statistics."""

    def __init__(
        self,
        logs: LOGS,
        begin_date: datetime,
        end_date: datetime,
        target_path: str,
        logger: logging.Logger,
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API,
        :param begin_date: Lowest date limit for statistics to be created.
        :param end_date: Highest date limit for statistics to be created.
        :param target_path: Path where all datasets should be saved.
        """

        super().__init__(logs, begin_date, end_date, target_path)
        self._logger = logger

    @abstractmethod
    def create_statistic(self):
        """Method for generating the statistics."""

    def create_plot_comparison_heatmap_duration(
        self, entity_dict: Dict, entity_type: str
    ) -> Figure:
        """Creates a heatmap with the totalized duration times of the different entities. (Intended for measurement times of instruments)

        :param entity_dict: dict with all entities and their duration times (e.g. {instrument1: [(date1, time), (date2,time), ...], instrument2: [(date1, time), (date2, time), ...]})
        :param entity_type: type of the entity (e.g. 'datasets for instrument x')
        :return: plot
        """
        if not entity_dict:
            self._logger.warning(
                "No data available for the statistics of the following entity type: %s.",
                entity_type,
            )
            return

        for entity, dates in entity_dict.items():
            if not dates:
                self._logger.warning(
                    "No data available for the statistics of the following entity: %s.",
                    entity,
                )
                return

        try:
            df = pd.DataFrame(
                [
                    {
                        "Instrument": f"{records[0]} (ID: {key})",
                        "Year": acq_time.year,
                        "Time": duration,
                    }
                    for key, records in entity_dict.items()
                    for duration, acq_time, operators in records[1:]
                ]
            )
        except ValueError as e:
            self._logger.error("Error creating DataFrame for %s: %s", entity_type, e)
            return

        heatmap_instrument_pivot_table = df.pivot_table(
            index="Year",
            columns="Instrument",
            values="Time",
            aggfunc="sum",
            fill_value=0,
        )

        total_time_year = 31557600.0  # seconds per year: approx. 31557600.0 (based on 365.2422 days per year)

        heatmap_instrument_pivot_table = (
            (heatmap_instrument_pivot_table / total_time_year * 100)
            .clip(upper=101)
            .round(3)
        )

        dynamic_width = max(10, len(heatmap_instrument_pivot_table.columns))
        dynamic_height = max(6, len(heatmap_instrument_pivot_table.index))

        fig, ax = plt.subplots(figsize=(dynamic_width, dynamic_height))
        cax = ax.matshow(heatmap_instrument_pivot_table, cmap="coolwarm")

        for (i, j), val in np.ndenumerate(heatmap_instrument_pivot_table):
            if not pd.isna(val):
                if val > 0:
                    if float(f"{val:.1f}") < 0.1:
                        ax.text(
                            j,
                            i,
                            "<0.1%",
                            ha="center",
                            va="center",
                            color="black",
                        )
                    elif val > 100:
                        ax.text(
                            j,
                            i,
                            ">100%",
                            ha="center",
                            va="center",
                            color="black",
                        )
                    else:
                        ax.text(
                            j,
                            i,
                            f"{val:.1f}%",
                            ha="center",
                            va="center",
                            color="black",
                        )
                else:
                    ax.text(
                        j,
                        i,
                        f"{val:.1f}%",
                        ha="center",
                        va="center",
                        color="black",
                    )
            else:
                ax.text(
                    j,
                    i,
                    "",
                    ha="center",
                    va="center",
                    color="black",
                )

        plt.xticks(
            np.arange(len(heatmap_instrument_pivot_table.columns)),
            heatmap_instrument_pivot_table.columns,
            rotation=90,
        )
        plt.yticks(
            np.arange(len(heatmap_instrument_pivot_table.index)),
            heatmap_instrument_pivot_table.index,
        )

        plt.colorbar(cax)
        plt.title(
            f"Utilization of instruments [aggregated experiment durations/year in %] of datasets acquired between {self._begin_date.strftime('%d/%B/%Y')} and {self._end_date.strftime('%d/%B/%Y')}",
            loc="center",
        )
        plt.xlabel("Instrument")
        plt.ylabel("Year")
        plt.close()

        return fig

    def create_plot_year_duration(
        self, dates_list: List, entity_type: str
    ) -> Dict[str, Figure]:
        """Creates a block diagram of the duration time for each year, based on 365.2422 days per year.

        :param dates_list: list with all dates of the entity type.
        :param entity_type: E.g. 'datasets for instrument x'.
        """

        if not dates_list:
            self._logger.warning(
                "No data available for the statistics of the following entity type: %s.",
                entity_type,
            )
            return

        dates = dates_list

        fig_dict = {}
        if not isinstance(dates[0], tuple):
            self._logger.error("No data to plot for duration per year.")
            sys.exit(0)

        df = pd.DataFrame(dates, columns=["duration", "acq_time", "operators"])
        df["acq_time"] = pd.to_datetime(df["acq_time"])
        df = df.sort_values(by="acq_time")
        df["Year"] = df["acq_time"].dt.year
        counts_per_year = df.groupby("Year").agg({"duration": "sum"}).reset_index()
        years = counts_per_year["Year"].astype(str)

        for i, value in enumerate(counts_per_year["duration"].values):
            # seconds per year: approx. 31557600.0 (based on 365.2422 days per year)
            data = [value, 31557600.0 - value]
            if data[1] < 0:
                labels = ["In use (over 100%)"]
                data = [value]
                colors = ["#a71e69"]
            elif data[1] == 0:
                labels = ["In use"]
                data = [value]
                colors = ["#a71e69"]
            elif data[1] == 31557600.0:
                labels = ["No use"]
                data = [0]
                colors = ["#83929c"]
            else:
                labels = ["In use", "No use"]
            colors = ["#a71e69", "#83929c"]

            if data == [0]:
                fig, ax = plt.subplots()
                ax.text(
                    0.5,
                    0.5,
                    f"There is no recorded usage for {entity_type} in the year {years[i]}. This may be due to the duration being zero, not specified, or no activity occurring during that period.",
                    horizontalalignment="center",
                    verticalalignment="center",
                    transform=ax.transAxes,
                )
                ax.axis("off")

            else:
                fig, ax = plt.subplots()
                wedges, texts, autotexts = ax.pie(
                    data,
                    labels=labels,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=colors,
                    textprops={"color": "white"},
                )
                ax.axis("equal")

                for text, label in zip(texts, labels):
                    if label == "In use" or label == "In use (over 100%)":
                        text.set_color("#a71e69")
                    if label == "No use":
                        text.set_color("#83929c")

                plt.title(
                    f"Utilization of {entity_type} in {years[i]} [aggregated experiment duration/year, in %] <br> Aggregated utilization: {DateHandler.seconds_to_dhms(value)}"
                )

            fig_dict[years[i]] = fig
            plt.close()

        return fig_dict

    def create_plot_year_month_duration(
        self, dates_list: List, entity_type: str
    ) -> Dict[str, Figure]:
        """Creates a pie chart of the duration time for each month in a year, based on the standard number of seconds per month, without considering leap years

        :param dates_list: list with all dates of the entity type
        :param entity_type: E.g. 'datasets for instrument x'

        :return: Plot
        """

        if not dates_list:
            self._logger.warning(
                "No data available for the statistics of the following entity type: %s.",
                entity_type,
            )
            return

        if not isinstance(dates_list[0], tuple):
            self._logger.error("ERROR: No data to plot for duration per month.")
            sys.exit(0)

        dates = dates_list
        fig_dict = {}
        month_total_seconds = {
            "01": 2678400,
            "02": 2419200,  # normal, no leap year
            "03": 2678400,
            "04": 2592000,
            "05": 2678400,
            "06": 2592000,
            "07": 2678400,
            "08": 2678400,
            "09": 2592000,
            "10": 2678400,
            "11": 2592000,
            "12": 2678400,
        }

        df = pd.DataFrame(dates, columns=["duration", "acq_time", "operators"])

        df["acq_time"] = pd.to_datetime(df["acq_time"])
        df = df.sort_values(by="acq_time")
        df["Year"] = df["acq_time"].dt.year
        df["Month"] = df["acq_time"].dt.month
        counts_per_year_month = (
            df.groupby(["Year", "Month"]).agg({"duration": "sum"}).reset_index()
        )
        counts_per_year_month["Year-Month"] = counts_per_year_month.apply(
            lambda x: f"{x['Year']}-{x['Month']:02d}", axis=1
        )
        year_month = counts_per_year_month["Year-Month"]

        for i, value in enumerate(counts_per_year_month["duration"].values):
            year = year_month[i].split("-")[0]
            month = year_month[i].split("-")[1]
            data = [value, month_total_seconds[month] - value]
            if data[1] < 0:
                labels = ["In use (over 100%)"]
                data = [value]
                colors = ["#a71e69"]
            elif data[1] == 0:
                labels = ["In use"]
                data = [value]
                colors = ["#a71e69"]
            elif data[1] == month_total_seconds[month]:
                labels = ["No use"]
                data = [0]
                colors = ["#83929c"]
            else:
                labels = ["In use", "No use"]

            if data == [0]:
                fig, ax = plt.subplots()
                ax.text(
                    0.5,
                    0.5,
                    f"There is no recorded usage for {entity_type} in {month}/{year}. This may be due to the duration being zero, not specified, or no activity occurring during that period.",
                    horizontalalignment="center",
                    verticalalignment="center",
                    transform=ax.transAxes,
                )
                ax.axis("off")
            else:
                colors = ["#a71e69", "#83929c"]

                fig, ax = plt.subplots()
                wedges, texts, autotexts = ax.pie(
                    data,
                    labels=labels,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=colors,
                    textprops={"color": "white"},
                )
                ax.axis("equal")

                for text, label in zip(texts, labels):
                    if label == "In use" or label == "In use (over 100%)":
                        text.set_color("#a71e69")
                    if label == "No use":
                        text.set_color("#83929c")

                plt.title(
                    f"Utilization of {entity_type} in {month}/{year} [aggregated experiment duration/month per year in %] <br> Aggregated utilization: {DateHandler.seconds_to_dhms(value)}"
                )
            fig_dict[year_month[i]] = fig
            plt.close()

        return fig_dict

    def create_plot_year_calendarWeek_duration(
        self, dates_list: List, entity_type: str
    ) -> Dict[str, Figure]:
        """Creates a pie chart with the duration time
        within a calendar week per year, based on a standardized week length (without considering daylight saving time or partial weeks).

        ::param dates_list: list with all dates of the entity type
        :param entity_type: E.g. 'datasets for instrument x'
        """

        if not dates_list:
            self._logger.warning(
                "No data available for the statistics of the following entity type: %s.",
                entity_type,
            )
            return

        if not isinstance(dates_list[0], tuple):
            self._logger.error("ERROR: No data to plot for duration per calendar week.")
            sys.exit(0)

        dates = dates_list
        fig_dict = {}

        df = pd.DataFrame(dates, columns=["duration", "acq_time", "operators"])
        df["acq_time"] = pd.to_datetime(df["acq_time"])
        df = df.sort_values(by="acq_time")
        year, week, day_of_week = zip(*[d.isocalendar() for d in df["acq_time"]])
        df["Year"] = year
        df["CalendarWeek"] = week

        counts_per_year_calendarWeek = (
            df.groupby(["Year", "CalendarWeek"]).agg({"duration": "sum"}).reset_index()
        )
        counts_per_year_calendarWeek["Year-CalendarWeek"] = (
            counts_per_year_calendarWeek.apply(
                lambda x: f"{x['Year']}-{x['CalendarWeek']:02d}", axis=1
            )
        )
        year_calendarWeek = counts_per_year_calendarWeek["Year-CalendarWeek"]

        for i, value in enumerate(counts_per_year_calendarWeek["duration"].values):
            year = year_calendarWeek[i].split("-")[0]
            calendar_week = year_calendarWeek[i].split("-")[1]
            # seconds per calendar week: 604800
            data = [value, 604800 - value]
            if data[1] < 0:
                labels = ["In use (over 100%)"]
                data = [value]
                colors = ["#a71e69"]
            elif data[1] == 0:
                labels = ["In use"]
                data = [value]
                colors = ["#a71e69"]
            elif data[1] == 604800:
                labels = ["No use"]
                data = [0]
                colors = ["#83929c"]
            else:
                labels = ["In use", "No use"]

            if data == [0]:
                fig, ax = plt.subplots()
                ax.text(
                    0.5,
                    0.5,
                    f"There is no recorded usage for {entity_type} in CW{calendar_week}/{year}. This may be due to the duration being zero, not specified, or no activity occurring during that period.",
                    horizontalalignment="center",
                    verticalalignment="center",
                    transform=ax.transAxes,
                )
                ax.axis("off")
            else:
                colors = ["#a71e69", "#83929c"]

                fig, ax = plt.subplots()
                wedges, texts, autotexts = ax.pie(
                    data,
                    labels=labels,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=colors,
                    textprops={"color": "white"},
                )
                ax.axis("equal")

                for text, label in zip(texts, labels):
                    if label == "In use" or label == "In use (over 100%)":
                        text.set_color("#a71e69")
                    if label == "No use":
                        text.set_color("#83929c")

                plt.title(
                    f"Utilization of {entity_type} in CW{calendar_week}/{year} [aggregated experiment duration/calendar week per year in %] <br> Aggregated utilization: {DateHandler.seconds_to_dhms(value)}"
                )

            fig_dict[year_calendarWeek[i]] = fig
            plt.close()

        return fig_dict

    ### Plot functions for StatisticsInstrumentsNMR ###

    def create_plot_instrument_num(
        self,
        instrument_id: int,
        instrument_name: str,
        data,
    ) -> Figure:
        """Creates a pie chart for the distribution of the data.

        :param instrument_id: ID of the instrument.
        :param instrument_name: Name of the instrument.
        :param data: Data for the distribution.
        :param statistic_entity: Entity for which the distribution is created.
        :param cutoff: Cutoff value for the distribution.

        :return: Figure with the pie chart.
        """

        filtered_data = data

        if not filtered_data:
            information_text = f"No data available for the distribution of different types of NMR experiments of {instrument_name} (ID: {instrument_id}) of datasets acquired between {self._begin_date.strftime('%d/%B/%Y')} and {self._end_date.strftime('%d/%B/%Y')}."
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
            plt.close()
            return fig

        labels = filtered_data.keys()
        sizes = filtered_data.values()

        fig, ax = plt.subplots()
        wedges, texts = ax.pie(sizes, startangle=90)
        ax.axis("equal")

        # cut off test, if wanted include cutoff parameter in function
        legend_labels = [f"{label}: {size}" for label, size in zip(labels, sizes)]
        # end cut off test

        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(
            sizes,
            # labels=legend_labels,
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.axis("equal")
        ax.legend(
            legend_labels,
            loc="center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=2,
            fontsize=10,
        )

        plt.title(
            f"Types of NMR experiments (Instrument: {instrument_name} , ID: {instrument_id}) of datasets acquired between {self._begin_date.strftime('%d/%B/%Y')} and {self._end_date.strftime('%d/%B/%Y')}",
        )

        plt.close()
        return fig
