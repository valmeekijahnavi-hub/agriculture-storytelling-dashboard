import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Agriculture Storytelling Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM DESIGN - inspired by the first PDF
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp { background: #f3f6fb; }
    [data-testid="stSidebar"] {
        background: #142b4d;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #e7eef9 !important;
    }
    .brand {
        font-size: 27px;
        line-height: 1.05;
        font-weight: 800;
        color: white;
        padding: 12px 4px 24px 4px;
        letter-spacing: .5px;
    }
    .page-title {
        color: #17365f;
        font-size: 29px;
        font-weight: 800;
        margin-bottom: 2px;
    }
    .page-subtitle {
        color: #6b7890;
        font-size: 13px;
        margin-bottom: 18px;
    }
    .story {
        background: #e8f0fb;
        border-left: 5px solid #2f65a5;
        padding: 13px 16px;
        border-radius: 7px;
        margin: 10px 0 14px 0;
        color: #17365f;
    }
    .story-title {
        color: #214f86;
        font-weight: 800;
        font-size: 14px;
        margin-bottom: 5px;
    }
    .story-body {
        color: #344b68;
        font-size: 13px;
    }
    .small-note {
        color: #718096;
        font-size: 11px;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e1e8f0;
        padding: 13px 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(20,43,77,.04);
    }
    div[data-testid="stMetricLabel"] { color: #718096; }
    div[data-testid="stMetricValue"] { color: #17365f; }
    h2, h3 { color: #17365f !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA LOADING AND CLEANING
# ---------------------------------------------------------
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_csv("crop_production.csv")

    # Clean column names
    data.columns = data.columns.str.strip()

    required = [
        "State_Name", "District_Name", "Crop_Year",
        "Season", "Crop", "Area", "Production"
    ]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(
            "The CSV is missing these required columns: "
            + ", ".join(missing)
        )

    for col in ["Area", "Production", "Crop_Year"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["Crop_Year"])
    data["Crop_Year"] = data["Crop_Year"].astype(int)
    data["Area"] = data["Area"].fillna(0)
    data["Production"] = data["Production"].fillna(0)

    for col in ["State_Name", "District_Name", "Season", "Crop"]:
        data[col] = data[col].astype("string").str.strip()

    data = data.dropna(subset=["State_Name", "District_Name", "Season", "Crop"])
    return data

# File uploader is optional; the default file is crop_production.csv
with st.sidebar:
    st.markdown('<div class="brand">🌾 AGRI<br>STORY</div>', unsafe_allow_html=True)
    st.markdown("### Dashboard")
    uploaded_file = st.file_uploader(
        "Upload agriculture CSV (optional)",
        type=["csv"],
        help="If no file is uploaded, the app reads crop_production.csv from this folder."
    )

try:
    df = load_data(uploaded_file)
except FileNotFoundError:
    st.error("Could not find crop_production.csv. Keep the CSV file in the same folder as app.py, or upload it using the sidebar.")
    st.stop()
except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

# ---------------------------------------------------------
# GLOBAL SIDEBAR FILTERS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("### Filters")

    states = sorted(df["State_Name"].dropna().unique().tolist())
    selected_states = st.multiselect(
        "State(s)", states, default=states, key="states_filter"
    )
    state_source = df[df["State_Name"].isin(selected_states)] if selected_states else df.iloc[0:0]

    districts = sorted(state_source["District_Name"].dropna().unique().tolist())
    selected_districts = st.multiselect(
        "District(s)", districts, default=districts, key="districts_filter"
    )

    year_values = sorted(df["Crop_Year"].dropna().unique().tolist())
    if year_values:
        selected_years = st.slider(
            "Crop year range",
            min_value=int(min(year_values)),
            max_value=int(max(year_values)),
            value=(int(min(year_values)), int(max(year_values)))
        )
    else:
        selected_years = (0, 0)

    season_values = sorted(df["Season"].dropna().unique().tolist())
    selected_seasons = st.multiselect(
        "Season(s)", season_values, default=season_values, key="seasons_filter"
    )

    crop_source = state_source.copy()
    if selected_districts:
        crop_source = crop_source[crop_source["District_Name"].isin(selected_districts)]
    if selected_seasons:
        crop_source = crop_source[crop_source["Season"].isin(selected_seasons)]
    crop_values = sorted(crop_source["Crop"].dropna().unique().tolist())
    selected_crops = st.multiselect(
        "Crop(s)", crop_values, default=crop_values, key="crops_filter"
    )

    st.markdown("---")
    st.caption("All dashboard pages use the same filtered dataset.")
    st.caption("Change a filter to update every KPI and chart.")

# ---------------------------------------------------------
# APPLY ALL FILTERS TO ONE DATAFRAME
# ---------------------------------------------------------
filtered_df = df.copy()

if selected_states:
    filtered_df = filtered_df[filtered_df["State_Name"].isin(selected_states)]
if selected_districts:
    filtered_df = filtered_df[filtered_df["District_Name"].isin(selected_districts)]
filtered_df = filtered_df[
    filtered_df["Crop_Year"].between(selected_years[0], selected_years[1])
]
if selected_seasons:
    filtered_df = filtered_df[filtered_df["Season"].isin(selected_seasons)]
if selected_crops:
    filtered_df = filtered_df[filtered_df["Crop"].isin(selected_crops)]

if filtered_df.empty:
    st.warning("No records match the selected filters. Select more states, districts, seasons, or crops.")
    st.stop()

# ---------------------------------------------------------
# COMMON HEADER AND KPI CARDS
# ---------------------------------------------------------
page = st.sidebar.radio(
    "DASHBOARD PAGES",
    ["Overview", "Production Trends", "Crop Insights", "State Analysis"]
)

total_production = filtered_df["Production"].sum()
total_area = filtered_df["Area"].sum()
crop_count = filtered_df["Crop"].nunique()
state_count = filtered_df["State_Name"].nunique()

page_titles = {
    "Overview": ("Agriculture Overview | What is happening across Indian agriculture?",
                 "A guided story from overall production to patterns that can support better agricultural decisions."),
    "Production Trends": ("Production Trends | How is crop production changing?",
                          "Explore changes in agricultural production over the selected crop years."),
    "Crop Insights": ("Crop Insights | Which crops contribute the most?",
                      "Compare crop production and understand how production is distributed across crops."),
    "State Analysis": ("State Analysis | Where is agricultural production concentrated?",
                       "Compare states and districts to identify areas with higher recorded production.")
}
title, subtitle = page_titles[page]

st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("TOTAL PRODUCTION", f"{total_production:,.0f}")
k2.metric("TOTAL CULTIVATED AREA", f"{total_area:,.0f}")
k3.metric("NUMBER OF CROPS", f"{crop_count:,}")
k4.metric("STATES COVERED", f"{state_count:,}")

st.markdown(
    f'<div class="small-note">Selected crop years: {selected_years[0]}–{selected_years[1]} '
    f'| Records analysed: {len(filtered_df):,}</div>',
    unsafe_allow_html=True
)
st.markdown("---")

# Consistent chart styling
chart_template = "plotly_white"
navy = "#244f86"
blue = "#5d91cf"
light_blue = "#a9c5e8"

# ---------------------------------------------------------
# PAGE 1 - EXECUTIVE OVERVIEW
# ---------------------------------------------------------
if page == "Overview":
    year_data = (
        filtered_df.groupby("Crop_Year", as_index=False)["Production"]
        .sum().sort_values("Crop_Year")
    )
    season_data = (
        filtered_df.groupby("Season", as_index=False)["Production"]
        .sum().sort_values("Production", ascending=False)
    )
    crop_data = (
        filtered_df.groupby("Crop", as_index=False)["Production"]
        .sum().sort_values("Production", ascending=False).head(8)
    )

    left, right = st.columns([1.65, 1])
    with left:
        st.subheader("1. Production momentum across years")
        fig = px.line(
            year_data, x="Crop_Year", y="Production", markers=True,
            labels={"Crop_Year": "Crop year", "Production": "Production"},
            template=chart_template
        )
        fig.update_traces(line=dict(color=navy, width=3), marker=dict(size=7))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=15, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("2. Production by season")
        fig = px.bar(
            season_data, x="Production", y="Season", orientation="h",
            labels={"Production": "Production", "Season": "Season"},
            template=chart_template
        )
        fig.update_traces(marker_color=blue)
        fig.update_layout(height=360, yaxis={"categoryorder": "total ascending"},
                          margin=dict(l=10, r=10, t=15, b=10))
        st.plotly_chart(fig, use_container_width=True)

    if not crop_data.empty:
        leading_crop = crop_data.iloc[0]["Crop"]
        share = crop_data.iloc[0]["Production"] / total_production * 100 if total_production else 0
        st.markdown(
            f'<div class="story"><div class="story-title">STORY 01 | Production is led by {leading_crop}</div>'
            f'<div class="story-body">{leading_crop} is the leading crop in the current selection, '
            f'contributing {share:.1f}% of the selected dataset production. '
            f'Compare the yearly trend and seasonal distribution to understand the wider pattern.</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("**How to read this:** Start with the KPI cards, then compare yearly production with the contribution of each season.")
    st.caption("Decision prompt: Which seasons or years deserve closer investigation? The charts show patterns, not the causes behind them.")

    st.subheader("Top crops in the selected data")
    fig = px.bar(crop_data, x="Crop", y="Production", template=chart_template,
                 labels={"Crop": "Crop", "Production": "Production"})
    fig.update_traces(marker_color=navy)
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=15, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PAGE 2 - PRODUCTION TRENDS
# ---------------------------------------------------------
elif page == "Production Trends":
    year_data = (
        filtered_df.groupby("Crop_Year", as_index=False)["Production"]
        .sum().sort_values("Crop_Year")
    )
    st.subheader("Annual crop production trend")
    fig = px.line(
        year_data, x="Crop_Year", y="Production", markers=True,
        labels={"Crop_Year": "Crop year", "Production": "Total production"},
        template=chart_template
    )
    fig.update_traces(line=dict(color=navy, width=3), marker=dict(size=8))
    fig.update_layout(height=440, margin=dict(l=10, r=10, t=15, b=10))
    st.plotly_chart(fig, use_container_width=True)

    if len(year_data) >= 2:
        first_value = year_data.iloc[0]["Production"]
        last_value = year_data.iloc[-1]["Production"]
        if first_value:
            change = ((last_value - first_value) / abs(first_value)) * 100
            direction = "increased" if change >= 0 else "decreased"
            story_text = (
                f"Between {int(year_data.iloc[0]['Crop_Year'])} and "
                f"{int(year_data.iloc[-1]['Crop_Year'])}, recorded production "
                f"{direction} by {abs(change):.1f}% in the selected records."
            )
        else:
            story_text = "The first year has zero recorded production, so percentage change cannot be calculated reliably."
    else:
        story_text = "Select a wider year range to compare production across multiple years."

    st.markdown(
        f'<div class="story"><div class="story-title">STORY 02 | What changed over time?</div>'
        f'<div class="story-body">{story_text} This describes the observed data and does not establish why the change occurred.</div></div>',
        unsafe_allow_html=True
    )

    st.subheader("Year-wise production details")
    st.dataframe(year_data, use_container_width=True, hide_index=True)
    st.markdown("**Decision prompt:** Were there unusual peaks or dips? Check rainfall, crop mix, policy, and market information before explaining their causes.")

# ---------------------------------------------------------
# PAGE 3 - CROP INSIGHTS
# ---------------------------------------------------------
elif page == "Crop Insights":
    crop_data = (
        filtered_df.groupby("Crop", as_index=False)["Production"]
        .sum().sort_values("Production", ascending=False)
    )
    top_crop_data = crop_data.head(10)
    left, right = st.columns([1.45, 1])

    with left:
        st.subheader("Top 10 crops by production")
        fig = px.bar(
            top_crop_data.sort_values("Production"),
            x="Production", y="Crop", orientation="h",
            labels={"Production": "Production", "Crop": "Crop"},
            template=chart_template
        )
        fig.update_traces(marker_color=navy)
        fig.update_layout(height=460, margin=dict(l=10, r=10, t=15, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Production contribution")
        fig = px.pie(
            top_crop_data, names="Crop", values="Production",
            hole=0.42, template=chart_template
        )
        fig.update_layout(height=460, margin=dict(l=5, r=5, t=15, b=10),
                          legend=dict(orientation="h", y=-0.12))
        st.plotly_chart(fig, use_container_width=True)

    if not crop_data.empty:
        top = crop_data.iloc[0]
        top_share = top["Production"] / total_production * 100 if total_production else 0
        st.markdown(
            f'<div class="story"><div class="story-title">STORY 03 | The leading crop is {top["Crop"]}</div>'
            f'<div class="story-body">{top["Crop"]} has the highest recorded production in the selected data, '
            f'with {top_share:.1f}% of total production. High production does not automatically mean high profit or best suitability.</div></div>',
            unsafe_allow_html=True
        )

    st.subheader("Crop production summary")
    summary = (
        filtered_df.groupby("Crop", as_index=False)
        .agg(Area=("Area", "sum"), Production=("Production", "sum"))
        .sort_values("Production", ascending=False)
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.markdown("**Decision prompt:** Which crops dominate production, and are there crops with comparatively smaller production that may need separate study?")

# ---------------------------------------------------------
# PAGE 4 - STATE ANALYSIS
# ---------------------------------------------------------
elif page == "State Analysis":
    state_data = (
        filtered_df.groupby("State_Name", as_index=False)
        .agg(Production=("Production", "sum"), Area=("Area", "sum"))
        .sort_values("Production", ascending=False)
    )
    top_states = state_data.head(10)

    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Top states by production")
        fig = px.bar(
            top_states.sort_values("Production"),
            x="Production", y="State_Name", orientation="h",
            labels={"Production": "Production", "State_Name": "State"},
            template=chart_template
        )
        fig.update_traces(marker_color=navy)
        fig.update_layout(height=440, margin=dict(l=10, r=10, t=15, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Cultivated area by state")
        fig = px.bar(
            top_states.sort_values("Area"),
            x="Area", y="State_Name", orientation="h",
            labels={"Area": "Cultivated area", "State_Name": "State"},
            template=chart_template
        )
        fig.update_traces(marker_color=blue)
        fig.update_layout(height=440, margin=dict(l=10, r=10, t=15, b=10))
        st.plotly_chart(fig, use_container_width=True)

    if not state_data.empty:
        leading_state = state_data.iloc[0]["State_Name"]
        st.markdown(
            f'<div class="story"><div class="story-title">STORY 04 | {leading_state} leads the current selection</div>'
            f'<div class="story-body">{leading_state} has the highest recorded production among the states currently shown. '
            f'Compare production with cultivated area before drawing conclusions about productivity.</div></div>',
            unsafe_allow_html=True
        )

    st.subheader("Area versus production")
    scatter = filtered_df.copy()
    if len(scatter) > 12000:
        scatter = scatter.sample(12000, random_state=42)
    fig = px.scatter(
        scatter, x="Area", y="Production", color="Season",
        hover_data=["State_Name", "District_Name", "Crop", "Crop_Year"],
        labels={"Area": "Cultivated area", "Production": "Production"},
        template=chart_template
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=15, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Decision prompt:** Which states have both high production and large cultivated areas? Additional data is needed to compare productivity, profitability, or causes.")

    st.subheader("State-wise summary")
    st.dataframe(state_data, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# DOWNLOAD FILTERED RECORDS
# ---------------------------------------------------------
st.markdown("---")
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download filtered agriculture data",
    data=csv_data,
    file_name="filtered_agriculture_data.csv",
    mime="text/csv"
)
st.caption("Agriculture Data Visualization & Storytelling | Built with Python, Pandas, Plotly and Streamlit")
