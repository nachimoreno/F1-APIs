import altair as alt
import pandas as pd
import streamlit as st
from src.fetch_results import fetch_and_save_all_races_up_to
from src.knapsack import find_best_two_team_lineups

st.set_page_config(
    page_title="F1 Fantasy Solver",
    page_icon="🏎️",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_available_options() -> tuple[list[str], list[str]]:
    """
    Load a broad set of available driver and constructor names from the local data
    so the exclusion multiselects can be populated before a solve is run.
    """
    from src.fetch_results import get_driver_and_team_info

    driver_info, team_info = get_driver_and_team_info()
    available_drivers = sorted(driver_info.keys())
    available_teams = sorted(team_info.keys())
    return available_drivers, available_teams


@st.cache_data(show_spinner=False)
def build_driver_summary_dataframe(
    driver_info: dict, risk_penalty: float
) -> pd.DataFrame:
    from src.knapsack import (
        average_points,
        risk_adjusted_points,
        standard_deviation,
        total_points,
    )

    driver_rows = []
    for driver_name, driver_values in driver_info.items():
        points_by_session = driver_values["points"]
        driver_rows.append(
            {
                "Driver": driver_name,
                "Cost": round(driver_values["cost"], 1),
                "Average Points": round(average_points(points_by_session), 2),
                "Std Dev": round(standard_deviation(points_by_session), 2),
                "Risk Adjusted": round(
                    risk_adjusted_points(points_by_session, risk_penalty), 2
                ),
                "Historical Total": round(total_points(points_by_session), 2),
                "Races Counted": len(points_by_session),
                "Average DNF Loss": round(driver_values["avg_dnf_loss"], 2),
            }
        )

    driver_dataframe = pd.DataFrame(driver_rows)
    return driver_dataframe.sort_values(
        by="Risk Adjusted", ascending=False
    ).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_team_summary_dataframe(team_info: dict, risk_penalty: float) -> pd.DataFrame:
    from src.knapsack import (
        average_points,
        risk_adjusted_points,
        standard_deviation,
        total_points,
    )

    team_rows = []
    for team_name, team_values in team_info.items():
        points_by_session = team_values["points"]
        team_rows.append(
            {
                "Constructor": team_name,
                "Cost": round(team_values["cost"], 1),
                "Average Points": round(average_points(points_by_session), 2),
                "Std Dev": round(standard_deviation(points_by_session), 2),
                "Risk Adjusted": round(
                    risk_adjusted_points(points_by_session, risk_penalty), 2
                ),
                "Historical Total": round(total_points(points_by_session), 2),
                "Races Counted": len(points_by_session),
                "Average DNF Loss": round(team_values["avg_dnf_loss"], 2),
            }
        )

    team_dataframe = pd.DataFrame(team_rows)
    return team_dataframe.sort_values(by="Risk Adjusted", ascending=False).reset_index(
        drop=True
    )


def build_lineups_dataframe(lineups: list[dict]) -> pd.DataFrame:
    lineup_rows = []
    for lineup_index, lineup in enumerate(lineups, start=1):
        lineup_rows.append(
            {
                "Lineup Rank": lineup_index,
                "Drivers": ", ".join(lineup["drivers"]),
                "Constructors": ", ".join(lineup["teams"]),
                "2x Driver": lineup["two_x_driver"],
                "2x Bonus": lineup["two_x_bonus"],
                "Projected Total": lineup["projected_total_score"],
                "Risk Adjusted": lineup["lineup_risk_adjusted_score"],
                "Historical Total": lineup["historical_total_points"],
                "Total Cost": lineup["total_cost"],
                "Overlap DNF Penalty": lineup.get("overlap_dnf_penalty"),
                "Adjusted Projected Total": lineup.get(
                    "adjusted_projected_total_score"
                ),
            }
        )

    return pd.DataFrame(lineup_rows)


def render_single_lineup_card(
    lineup: dict,
    title: str,
    show_overlap_metrics: bool = False,
) -> None:
    with st.container(border=True):
        st.subheader(title)

        if show_overlap_metrics:
            (
                metric_column_1,
                metric_column_2,
                metric_column_3,
                metric_column_4,
                metric_column_5,
            ) = st.columns(5)
            metric_column_1.metric("Projected Total", lineup["projected_total_score"])
            metric_column_2.metric(
                "Adj. Projected",
                lineup.get(
                    "adjusted_projected_total_score", lineup["projected_total_score"]
                ),
            )
            metric_column_3.metric(
                "Risk Adjusted", lineup["lineup_risk_adjusted_score"]
            )
            metric_column_4.metric(
                "Historical Total", lineup["historical_total_points"]
            )
            metric_column_5.metric("Total Cost", lineup["total_cost"])

            overlap_penalty = lineup.get("overlap_dnf_penalty")
            if overlap_penalty is not None:
                st.caption(f"Overlap DNF penalty applied: {overlap_penalty}")
        else:
            metric_column_1, metric_column_2, metric_column_3, metric_column_4 = (
                st.columns(4)
            )
            metric_column_1.metric("Projected Total", lineup["projected_total_score"])
            metric_column_2.metric(
                "Risk Adjusted", lineup["lineup_risk_adjusted_score"]
            )
            metric_column_3.metric(
                "Historical Total", lineup["historical_total_points"]
            )
            metric_column_4.metric("Total Cost", lineup["total_cost"])

        details_column_1, details_column_2 = st.columns(2)
        with details_column_1:
            st.markdown("**Drivers**")
            for driver_name in lineup["drivers"]:
                two_x_suffix = (
                    " **(2x)**" if driver_name == lineup["two_x_driver"] else ""
                )
                st.markdown(f"- {driver_name}{two_x_suffix}")

        with details_column_2:
            st.markdown("**Constructors**")
            for team_name in lineup["teams"]:
                st.markdown(f"- {team_name}")

        st.caption(f"2x bonus contribution: {lineup['two_x_bonus']}")


def render_two_team_lineup_cards(
    first_lineups: list[dict],
    second_lineups: list[dict],
) -> None:
    if not first_lineups:
        st.warning("No valid lineups were found for the selected constraints.")
        return

    for lineup_index, first_lineup in enumerate(first_lineups, start=1):
        second_lineup = second_lineups[lineup_index - 1]

        st.markdown(f"### Lineup Pair #{lineup_index}")
        first_team_column, second_team_column = st.columns(2)

        with first_team_column:
            render_single_lineup_card(
                lineup=first_lineup,
                title="Team 1",
                show_overlap_metrics=False,
            )

        with second_team_column:
            render_single_lineup_card(
                lineup=second_lineup,
                title="Team 2",
                show_overlap_metrics=True,
            )


st.title("🏎️ F1 Fantasy Solver")

with st.sidebar:
    st.header("Solver Settings")

    budget = st.number_input(
        "Budget",
        min_value=0.0,
        value=100.0,
        step=0.1,
        help="Budget available for the lineup.",
    )

    risk_penalty = st.slider(
        "Risk Penalty",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Higher values penalize volatile drivers and constructors more.",
    )

    top_n = st.number_input(
        "Top N Lineups",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        help="Number of best lineup pairs to return.",
    )

    try:
        available_drivers, available_teams = load_available_options()
    except Exception:
        available_drivers, available_teams = [], []

    exclude_drivers = st.multiselect(
        "Exclude Drivers",
        options=available_drivers,
        default=[],
        help="Equivalent to `--exclude_drivers`.",
    )

    exclude_teams = st.multiselect(
        "Exclude Constructors",
        options=available_teams,
        default=[],
        help="Equivalent to `--exclude_teams`.",
    )

    run_solver = st.button("Run Solver", type="primary", use_container_width=True)


if "solver_results" not in st.session_state:
    st.session_state.solver_results = None


if run_solver:
    try:
        with st.status("Running solver...", expanded=True) as solver_status:
            st.write("Fetching data from fantasy.formula1.com...")
            fetch_and_save_all_races_up_to(24)

            st.write("Computing best two-team lineups...")
            driver_info, team_info, first_lineups, second_lineups = (
                find_best_two_team_lineups(
                    excluded_drivers=exclude_drivers,
                    excluded_teams=exclude_teams,
                    budget=float(budget),
                    top_n=int(top_n),
                    risk_penalty=float(risk_penalty),
                    verbosity=0,
                )
            )

            st.session_state.solver_results = {
                "driver_info": driver_info,
                "team_info": team_info,
                "first_lineups": first_lineups,
                "second_lineups": second_lineups,
                "risk_penalty": float(risk_penalty),
                "budget": float(budget),
                "excluded_drivers": exclude_drivers,
                "excluded_teams": exclude_teams,
            }
            solver_status.update(
                label="Solver complete", state="complete", expanded=False
            )
    except Exception as error:
        st.session_state.solver_results = None
        st.error(f"Solver run failed: {error}")
        raise error


solver_results = st.session_state.solver_results

if solver_results is None:
    st.info("Set your inputs in the sidebar and click **Run Solver**.")
else:
    driver_info = solver_results["driver_info"]
    team_info = solver_results["team_info"]
    first_lineups = solver_results["first_lineups"]
    second_lineups = solver_results["second_lineups"]
    selected_risk_penalty = solver_results["risk_penalty"]

    summary_column_1, summary_column_2, summary_column_3, summary_column_4 = st.columns(
        4
    )
    summary_column_1.metric("Returned Lineup Pairs", len(first_lineups))
    summary_column_2.metric("Budget", round(solver_results["budget"], 2))
    summary_column_3.metric("Excluded Drivers", len(solver_results["excluded_drivers"]))
    summary_column_4.metric(
        "Excluded Constructors", len(solver_results["excluded_teams"])
    )

    lineups_tab, drivers_tab, constructors_tab = st.tabs(
        ["Best Lineups", "Driver Model View", "Constructor Model View"]
    )

    with lineups_tab:
        render_two_team_lineup_cards(first_lineups, second_lineups)

    with drivers_tab:
        driver_summary_dataframe = build_driver_summary_dataframe(
            driver_info, selected_risk_penalty
        )

        st.dataframe(
            driver_summary_dataframe, use_container_width=True, hide_index=True
        )

        chart_dataframe = driver_summary_dataframe[
            ["Driver", "Average Points", "Risk Adjusted"]
        ]

        chart = (
            alt.Chart(chart_dataframe)
            .transform_fold(
                ["Average Points", "Risk Adjusted"],
                as_=["Metric", "Points"],
            )
            .mark_bar()
            .encode(
                x=alt.X("Driver:N", sort=None, title="Driver"),
                y=alt.Y("Points:Q", title="Points"),
                color=alt.Color("Metric:N", title="Metric"),
                xOffset=alt.XOffset("Metric:N"),
                tooltip=[
                    alt.Tooltip("Driver:N"),
                    alt.Tooltip("Metric:N"),
                    alt.Tooltip("Points:Q", format=".2f"),
                ],
            )
        )

        st.altair_chart(chart, use_container_width=True)

    with constructors_tab:
        team_summary_dataframe = build_team_summary_dataframe(
            team_info, selected_risk_penalty
        )
        st.dataframe(team_summary_dataframe, use_container_width=True, hide_index=True)

        chart_dataframe = team_summary_dataframe[
            ["Constructor", "Average Points", "Risk Adjusted"]
        ]

        chart = (
            alt.Chart(chart_dataframe)
            .transform_fold(
                ["Average Points", "Risk Adjusted"],
                as_=["Metric", "Points"],
            )
            .mark_bar()
            .encode(
                x=alt.X("Constructor:N", sort=None, title="Constructor"),
                y=alt.Y("Points:Q", title="Points"),
                color=alt.Color("Metric:N", title="Metric"),
                xOffset=alt.XOffset("Metric:N"),
                tooltip=[
                    alt.Tooltip("Constructor:N"),
                    alt.Tooltip("Metric:N"),
                    alt.Tooltip("Points:Q", format=".2f"),
                ],
            )
        )

        st.altair_chart(chart, use_container_width=True)
