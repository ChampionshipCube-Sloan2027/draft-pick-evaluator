"""
Injury Body Map feature
--------------------------------------
Streamlit + Plotly component for displaying reported player injuries on a
simplified front/back body map.

Install:
    pip install streamlit pandas plotly

CSV expected at player_injuries.csv with these columns:
    player_name,body_region,injury,status,report_date,body_view,source_url,notes

Integrate into an existing Streamlit app:
    from injury_map import render_injury_map
    render_injury_map(player_name=selected_player_name)

Or run this file directly as a small test app:
    streamlit run injury_map.py
"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DEFAULT_CSV = Path(__file__).with_name("player_injuries.csv")

REQUIRED_COLUMNS = [
    "player_name", "body_region", "injury", "status",
    "report_date", "body_view", "source_url", "notes"
]

# Approximate locations on a simplified diagram, not anatomical or medical data.
# x and y are in a 0–100 coordinate space.
REGION_COORDS = {
    "head": (50, 88),
    "neck": (50, 79),
    "left_shoulder": (39, 75),
    "right_shoulder": (61, 75),
    "left_arm": (31, 64),
    "right_arm": (69, 64),
    "left_elbow": (27, 56),
    "right_elbow": (73, 56),
    "left_wrist": (23, 47),
    "right_wrist": (77, 47),
    "chest": (50, 69),
    "upper_back": (50, 69),
    "ribs": (50, 61),
    "lower_back": (50, 54),
    "abdomen": (50, 57),
    "left_hip": (44, 47),
    "right_hip": (56, 47),
    "left_thigh": (44, 36),
    "right_thigh": (56, 36),
    "left_knee": (43, 25),
    "right_knee": (57, 25),
    "left_calf": (43, 16),
    "right_calf": (57, 16),
    "left_ankle": (42, 7),
    "right_ankle": (58, 7),
    "left_foot": (37, 3),
    "right_foot": (63, 3),
}

# Terms used to assign a display colour. These colours indicate reported status,
# not a medical assessment of injury severity.
RED_TERMS = ("out", "ruled out", "season-ending", "season ending", "indefinitely")
ORANGE_TERMS = ("doubtful", "questionable", "day-to-day", "day to day", "probable", "limited")


def _status_colour(status):
    value = str(status or "").strip().lower()
    if any(term in value for term in RED_TERMS):
        return "#dc4545"
    if any(term in value for term in ORANGE_TERMS):
        return "#e99b22"
    return "#8a96a3"


def load_injuries(csv_path=DEFAULT_CSV):
    """Load injury rows and validate the expected columns."""
    path = Path(csv_path)
    if not path.exists():
        return pd.DataFrame(columns=REQUIRED_COLUMNS), (
            f"Couldn't find {path.name}. Create it using the supplied CSV template."
        )

    try:
        df = pd.read_csv(path).fillna("")
    except Exception as exc:
        return pd.DataFrame(columns=REQUIRED_COLUMNS), f"Couldn't read {path.name}: {exc}"

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        return pd.DataFrame(columns=REQUIRED_COLUMNS), (
            "Your injury CSV is missing these columns: " + ", ".join(missing)
        )

    # Normalise text values so filtering is less fragile.
    for column in REQUIRED_COLUMNS:
        df[column] = df[column].astype(str).str.strip()

    df["body_region"] = df["body_region"].str.lower().str.replace(" ", "_")
    df["body_view"] = df["body_view"].str.lower().str.strip()
    return df, None


def _add_silhouette(fig, x_offset, title):
    """Draw a deliberately simplified, schematic body silhouette."""
    # Head
    fig.add_shape(type="circle", x0=x_offset + 44, x1=x_offset + 56,
                  y0=82, y1=94, line=dict(color="#8793a0", width=2),
                  fillcolor="rgba(135,147,160,0.12)")
    # Torso
    torso_x = [43, 57, 60, 56, 55, 45, 44, 40, 43]
    torso_y = [79, 79, 66, 53, 47, 47, 53, 66, 79]
    fig.add_trace(go.Scatter(
        x=[x + x_offset for x in torso_x], y=torso_y, mode="lines",
        fill="toself", fillcolor="rgba(135,147,160,0.12)",
        line=dict(color="#8793a0", width=2), hoverinfo="skip",
        showlegend=False
    ))
    # Arms
    for x0, x1, x2 in [(41, 33, 25), (59, 67, 75)]:
        fig.add_trace(go.Scatter(
            x=[x0+x_offset, x1+x_offset, x2+x_offset],
            y=[76, 61, 46], mode="lines",
            line=dict(color="#8793a0", width=7), hoverinfo="skip",
            showlegend=False
        ))
    # Legs
    for hip, knee, ankle in [(45, 43, 42), (55, 57, 58)]:
        fig.add_trace(go.Scatter(
            x=[hip+x_offset, knee+x_offset, ankle+x_offset],
            y=[47, 24, 7], mode="lines",
            line=dict(color="#8793a0", width=9), hoverinfo="skip",
            showlegend=False
        ))
    # Feet
    for foot_x in [38, 62]:
        fig.add_trace(go.Scatter(
            x=[foot_x+x_offset, foot_x+x_offset+5],
            y=[3, 3], mode="lines", line=dict(color="#8793a0", width=6),
            hoverinfo="skip", showlegend=False
        ))
    fig.add_annotation(x=x_offset+50, y=98, text=title, showarrow=False,
                       font=dict(size=14, color="#8793a0"))


def _body_figure(rows):
    fig = go.Figure()
    _add_silhouette(fig, 0, "FRONT")
    _add_silhouette(fig, 120, "BACK")

    marker_rows = []
    for _, row in rows.iterrows():
        region = row["body_region"]
        if region not in REGION_COORDS:
            continue
        view = row["body_view"] if row["body_view"] in ("front", "back") else "front"
        x, y = REGION_COORDS[region]
        if view == "back":
            x += 120
        marker_rows.append({
            "x": x,
            "y": y,
            "region": region.replace("_", " ").title(),
            "injury": row["injury"] or "Injury not specified",
            "status": row["status"] or "Status not specified",
            "date": row["report_date"] or "Date not provided",
            "notes": row["notes"] or "No additional notes",
            "source": row["source_url"] or "No source URL provided",
            "colour": _status_colour(row["status"]),
        })

    if marker_rows:
        mdf = pd.DataFrame(marker_rows)
        fig.add_trace(go.Scatter(
            x=mdf["x"], y=mdf["y"], mode="markers",
            marker=dict(
                size=17, color=mdf["colour"], opacity=0.95,
                line=dict(color="white", width=1.5), symbol="circle"
            ),
            customdata=mdf[["region", "injury", "status", "date", "notes", "source"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "Reported status: %{customdata[2]}<br>"
                "Report date: %{customdata[3]}<br>"
                "%{customdata[4]}<br>"
                "Source: %{customdata[5]}<extra></extra>"
            ),
            showlegend=False
        ))

    fig.update_layout(
        height=480,
        margin=dict(l=8, r=8, t=32, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=[-5, 245], fixedrange=True),
        yaxis=dict(visible=False, range=[0, 101], fixedrange=True,
                   scaleanchor="x", scaleratio=1),
        hoverlabel=dict(align="left"),
    )
    return fig, len(marker_rows)


def render_injury_map(player_name=None, csv_path=DEFAULT_CSV):
    """
    Render the injury map inside an existing Streamlit app.

    Args:
        player_name: Selected player's name. If None, a dropdown is shown.
        csv_path: Optional path to the injury CSV.
    """
    st.subheader("Player Health Map")
    st.caption(
        "Reported injury information only — this visual does not diagnose injuries "
        "or independently determine medical severity."
    )

    df, error = load_injuries(csv_path)
    if error:
        st.warning(error)
        st.info("Expected CSV columns: " + ", ".join(REQUIRED_COLUMNS))
        return

    if df.empty:
        st.info("No injury records are in the CSV yet.")
        return

    names = sorted([name for name in df["player_name"].unique() if name])
    if not names:
        st.info("No player names were found in the injury CSV.")
        return

    if player_name is None or not str(player_name).strip():
        selected_name = st.selectbox("Choose a player", names, key="injury_map_player")
    else:
        # Case-insensitive match to accommodate different name casing.
        matches = [name for name in names if name.casefold() == str(player_name).strip().casefold()]
        selected_name = matches[0] if matches else None
        if selected_name is None:
            st.info(f"No injury rows found for {player_name}.")
            return

    player_rows = df[df["player_name"].str.casefold() == selected_name.casefold()].copy()
    if player_rows.empty:
        st.info("No injury records found for this player.")
        return

    # Summary counts are descriptive counts of records, not a risk score.
    c1, c2, c3 = st.columns(3)
    c1.metric("Recorded injuries", len(player_rows))
    c2.metric("Current-status records", int(player_rows["status"].str.lower().isin(
        ["out", "doubtful", "questionable", "probable", "available", "day-to-day", "day to day"]
    ).sum()))
    c3.metric("Sources linked", int((player_rows["source_url"].str.strip() != "").sum()))

    fig, mapped_count = _body_figure(player_rows)
    if mapped_count:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.warning(
            "The player's injury rows don't have any recognised body_region values. "
            "Use one of the supported values listed in the CSV template."
        )

    st.markdown("**Colour key**")
    st.markdown(
        '<span style="color:#dc4545">● Red</span> Reported as out / ruled out / '
        'indefinitely unavailable &nbsp;&nbsp; '
        '<span style="color:#e99b22">● Orange</span> Questionable / doubtful / '
        'probable / day-to-day &nbsp;&nbsp; '
        '<span style="color:#8a96a3">● Grey</span> Other or unspecified status',
        unsafe_allow_html=True
    )

    st.markdown("**Reported injury records**")
    display_columns = ["body_region", "injury", "status", "report_date", "body_view", "source_url", "notes"]
    table = player_rows[display_columns].rename(columns={
        "body_region": "Body region",
        "injury": "Reported injury",
        "status": "Reported status",
        "report_date": "Report date",
        "body_view": "Body view",
        "source_url": "Source URL",
        "notes": "Notes",
    })
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.caption(
        "The body diagram is schematic. Injury location is based on the body_region "
        "field you enter; colour is based on the reported status field."
    )


# Allows this file to run on its own for a quick test, without affecting the main app.
if __name__ == "__main__":
    st.set_page_config(page_title="NBA Player Health Map", layout="wide")
    st.title("NBA Player Health Map — Feature Test")
    st.write("Use this standalone page to test the feature before integrating it.")
    render_injury_map()
