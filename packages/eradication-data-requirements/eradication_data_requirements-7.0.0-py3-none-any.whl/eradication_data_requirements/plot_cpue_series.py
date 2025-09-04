from geci_plots import roundup, order_magnitude
import numpy as np
import matplotlib.pyplot as plt


def plot_comparative_yearly_cpue(socorro_data, guadalupe_data):
    seasons, seasons_labels, ticks_positions = get_ticks_info(socorro_data.index.values)
    seasons_guadalupe, _, _ = get_ticks_info(guadalupe_data.index.values)
    fontsize = 20

    _, ax = plt.subplots(figsize=(23, 10), tight_layout=True)
    max_cpue = max(socorro_data["cpue"].max(), guadalupe_data["cpue"].max())
    config_yearly_cpue_plot(fontsize, max_cpue, seasons_labels, ticks_positions, ax)
    ax = plot_cpue_series(socorro_data, seasons, ax, label="Socorro")
    ax = plot_cpue_series(guadalupe_data, seasons_guadalupe, ax, label="Guadalupe")
    plt.legend(fontsize="xx-large")
    return ax


def plot_cumulative_series_cpue(fontsize, cpue_df):
    seasons_index = cpue_df.index.values
    seasons, seasons_labels, ticks_positions = get_ticks_info(seasons_index)

    _, ax = plt.subplots(1, 2, figsize=(23, 10), tight_layout=True)
    max_cpue = max(cpue_df["cpue"])
    config_yearly_cpue_plot(fontsize, max_cpue, seasons_labels, ticks_positions, ax[0])
    plot_cpue_series(cpue_df, seasons, ax[0])

    ax[1].plot(seasons, cpue_df["cumulative_cpue"], "-o", linewidth=2)
    ax[1].set_xticks(ticks_positions)
    ax[1].set_xticklabels(seasons_labels, size=fontsize)
    ax[1].tick_params(axis="both", labelsize=fontsize)
    ax[1].spines["right"].set_visible(False)
    ax[1].spines["top"].set_visible(False)
    max_cum_cpue = max(cpue_df["cumulative_cpue"])
    cum_cpue_limit = roundup(max_cum_cpue, 10 ** order_magnitude(max_cum_cpue))
    ax[1].set_ylim(0, cum_cpue_limit)
    ax[1].set_ylabel("Cumulative CPUE", fontsize=fontsize)
    ax[1].set_xlim(ticks_positions[0] - 1, ticks_positions[-1])
    return ax


def plot_yearly_cpue(fontsize, cpue_df):
    seasons, seasons_labels, ticks_positions = get_ticks_info(cpue_df.Season.values)

    _, ax = plt.subplots(tight_layout=True)
    max_cpue = max(cpue_df["cpue"])
    config_yearly_cpue_plot(fontsize, max_cpue, seasons_labels, ticks_positions, ax)
    return plot_cpue_series(cpue_df, seasons, ax)


def plot_cpue_series(cpue_df, seasons, ax, label=None):
    ax.plot(seasons, cpue_df["cpue"], "-o", linewidth=2, label=label)
    return ax


def config_yearly_cpue_plot(fontsize, max_cpue, seasons_labels, ticks_positions, ax):
    ax.set_xticks(ticks_positions)
    ax.set_xticklabels(seasons_labels, size=fontsize)
    ax.tick_params(axis="both", labelsize=fontsize)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    cpue_limit = roundup(max_cpue, 10 ** order_magnitude(max_cpue))
    ax.set_ylim(0, cpue_limit)
    ax.set_ylabel("Catch Per Unit Effort (CPUE)", fontsize=fontsize)
    ax.set_xlim(ticks_positions[0] - 1, ticks_positions[-1])


def get_ticks_info(seasons):
    seasons_labels = [*seasons, ""]
    ticks_positions = np.arange(seasons[0], seasons[-1] + 2)
    ticks_positions[-1] = ticks_positions[-1] + 0.25
    return seasons, seasons_labels, ticks_positions


def calculate_cpue_and_cumulative_by_season(effort_capture_df):
    extract_year(effort_capture_df)
    effort_capture_df = effort_capture_df[effort_capture_df["Season"] >= 2014]
    column_name = "Season"
    return calculate_cpue_and_cumulative_by_column(effort_capture_df, column_name)


def calculate_cpue_and_cumulative_by_flight(effort_capture_df):
    column_name = "No_vuelo"
    return calculate_cpue_and_cumulative_by_column(effort_capture_df, column_name)


def calculate_cpue_and_cumulative_by_column(effort_capture_df, column_name):
    data_grouped_by_column = effort_capture_df.groupby(by=column_name).sum(numeric_only=False)
    data_grouped_by_column["cpue"] = (
        data_grouped_by_column["Capturas"] / data_grouped_by_column["Esfuerzo"]
    )
    data_grouped_by_column["cumulative_cpue"] = data_grouped_by_column["cpue"].cumsum()
    return data_grouped_by_column


def extract_year(effort_capture_df):
    effort_capture_df["Season"] = effort_capture_df["Fecha"].str[:4]
    effort_capture_df["Season"] = np.array([int(season) for season in effort_capture_df["Season"]])
