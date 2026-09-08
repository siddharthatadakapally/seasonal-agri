"""
Seasonal Agriculture Performance Analysis — Streamlit App
Interactive companion to the Seasonal_Agriculture_Performance_Analysis notebook.
Run with:  uv run streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Seasonal Agriculture Performance Analysis",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

SEASON_ORDER = ["Kharif", "Rabi", "Zaid"]
SEASON_COLORS = {"Kharif": "#2E7D32", "Rabi": "#F9A825", "Zaid": "#C62828"}

DATA_PATH = "data/seasonal_agriculture_performance_dataset.csv"


# --------------------------------------------------------------------------------------
# Data loading & cleaning (mirrors the notebook)
# --------------------------------------------------------------------------------------
@st.cache_data
def load_data():
    df_raw = pd.read_csv(DATA_PATH)
    missing_before = df_raw.isnull().sum()
    missing_before = missing_before[missing_before > 0]
    duplicates = int(df_raw.duplicated().sum())

    df = df_raw.copy()
    fill_cols = ["Rainfall_mm", "Soil_Moisture_pct", "Yield_Tonnes_Ha"]
    medians = {}
    for col in fill_cols:
        if col in df.columns:
            med = df[col].median()
            medians[col] = med
            df[col] = df[col].fillna(med)

    return df_raw, df, missing_before, duplicates, medians


df_raw, df, missing_before, duplicates, medians = load_data()

numeric_cols_for_corr = [
    "Rainfall_mm", "Avg_Temperature_C", "Humidity_pct", "Soil_Moisture_pct",
    "Fertilizer_kg_ha", "Yield_Tonnes_Ha", "Profit_INR",
    "Water_Efficiency_t_per_1000m3", "Disease_Pest_Risk_pct",
]
numeric_cols_for_corr = [c for c in numeric_cols_for_corr if c in df.columns]


# --------------------------------------------------------------------------------------
# Sidebar — navigation & global filters
# --------------------------------------------------------------------------------------
st.sidebar.title("🌾 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Data Cleaning",
        "Categorical Exploration",
        "Season-wise Comparison",
        "Profit & Loss",
        "Crop Yield",
        "Irrigation & Water Efficiency",
        "Correlation with Yield",
        "Key Insights",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filters (apply to charts below)")
season_filter = st.sidebar.multiselect("Season", SEASON_ORDER, default=SEASON_ORDER)
state_filter = st.sidebar.multiselect(
    "State", sorted(df["State"].unique()), default=sorted(df["State"].unique())
)
crop_filter = st.sidebar.multiselect(
    "Crop", sorted(df["Crop"].unique()), default=sorted(df["Crop"].unique())
)

fdf = df[
    df["Season"].isin(season_filter)
    & df["State"].isin(state_filter)
    & df["Crop"].isin(crop_filter)
]
if fdf.empty:
    st.sidebar.warning("No rows match the current filters — showing full dataset instead.")
    fdf = df

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(fdf):,}** of **{len(df):,}** farm records")


# --------------------------------------------------------------------------------------
# Page: Overview
# --------------------------------------------------------------------------------------
if page == "Overview":
    st.title("🌾 Seasonal Agriculture Performance Analysis")
    st.markdown(
        """
        This app studies how farming performance changes across different seasons
        (**Kharif**, **Rabi**, and **Zaid**). The dataset covers weather conditions,
        soil properties, resource usage, and financial outcomes for thousands of farms,
        so we can explore how season affects yield, cost, profit, and water usage.
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Farm records", f"{len(df):,}")
    c2.metric("Columns", f"{df.shape[1]}")
    c3.metric("States covered", df["State"].nunique())
    c4.metric("Crops covered", df["Crop"].nunique())

    st.subheader("Sample of the data")
    st.dataframe(df.head(20), width='stretch')

    st.subheader("Summary statistics")
    st.dataframe(df.describe().round(2), width='stretch')

    with st.expander("Column data types"):
        dtypes_df = pd.DataFrame({"Column": df.dtypes.index, "Type": df.dtypes.astype(str).values})
        st.dataframe(dtypes_df, width='stretch', hide_index=True)


# --------------------------------------------------------------------------------------
# Page: Data Cleaning
# --------------------------------------------------------------------------------------
elif page == "Data Cleaning":
    st.title("🧹 Missing Values & Duplicates")

    st.subheader("Missing values before cleaning")
    if missing_before.empty:
        st.success("No missing values found in the raw dataset.")
    else:
        miss_df = missing_before.reset_index()
        miss_df.columns = ["Column", "Missing Count"]
        st.dataframe(miss_df, width='stretch', hide_index=True)
        st.markdown(
            "These are numeric columns, so missing values were filled with the "
            "**column median** rather than dropping rows (which would have thrown "
            "away otherwise-usable data)."
        )
        med_df = pd.DataFrame({"Column": medians.keys(), "Median used": [round(v, 2) for v in medians.values()]})
        st.dataframe(med_df, width='stretch', hide_index=True)

    st.subheader("Duplicate rows")
    if duplicates == 0:
        st.success("No duplicate rows found — nothing to remove.")
    else:
        st.warning(f"{duplicates} duplicate rows found.")

    st.subheader("Missing values after cleaning")
    st.success(f"Total missing values remaining: **{int(df.isnull().sum().sum())}**")


# --------------------------------------------------------------------------------------
# Page: Categorical Exploration
# --------------------------------------------------------------------------------------
elif page == "Categorical Exploration":
    st.title("📊 Categorical Exploration")

    st.markdown(
        "The dataset covers **8 states**, **8 crops**, and **3 seasons** "
        "(Kharif, Rabi, Zaid). Kharif has the most records, followed by Rabi, "
        "then Zaid — Zaid is a short season grown by fewer farmers."
    )

    col1, col2 = st.columns(2)
    with col1:
        season_counts = fdf["Season"].value_counts().reindex(SEASON_ORDER).dropna()
        fig = px.bar(
            season_counts, x=season_counts.index, y=season_counts.values,
            color=season_counts.index, color_discrete_map=SEASON_COLORS,
            labels={"x": "Season", "y": "Count"}, title="Number of Farm Records per Season",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width='stretch')

    with col2:
        crop_counts = fdf["Crop"].value_counts()
        fig = px.bar(
            crop_counts, x=crop_counts.index, y=crop_counts.values,
            labels={"x": "Crop", "y": "Count"}, title="Number of Farm Records per Crop",
        )
        st.plotly_chart(fig, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        state_counts = fdf["State"].value_counts()
        fig = px.bar(
            state_counts, x=state_counts.index, y=state_counts.values,
            labels={"x": "State", "y": "Count"}, title="Number of Farm Records per State",
        )
        st.plotly_chart(fig, width='stretch')

    with col4:
        irr_counts = fdf["Irrigation_Method"].value_counts()
        fig = px.pie(
            irr_counts, names=irr_counts.index, values=irr_counts.values,
            title="Irrigation Method Share",
        )
        st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------------------
# Page: Season-wise Comparison
# --------------------------------------------------------------------------------------
elif page == "Season-wise Comparison":
    st.title("🌦️ Season-wise Comparison")

    season_avg = (
        fdf.groupby("Season")[
            ["Rainfall_mm", "Avg_Temperature_C", "Humidity_pct", "Yield_Tonnes_Ha",
             "Fertilizer_kg_ha", "Profit_INR", "Water_Efficiency_t_per_1000m3",
             "Disease_Pest_Risk_pct"]
        ]
        .mean()
        .round(2)
        .reindex(SEASON_ORDER)
        .dropna(how="all")
    )
    st.subheader("Average metrics by season")
    st.dataframe(season_avg, width='stretch')

    st.markdown(
        """
        - **Kharif** season has the highest rainfall (monsoon-driven) and the highest average yield.
        - **Kharif** also shows the highest disease/pest risk — humid, rainy conditions favor both crop growth and disease.
        - **Zaid** season has the lowest rainfall, as expected for the summer season.
        """
    )

    st.subheader("Yield distribution by season")
    fig = px.box(
        fdf, x="Season", y="Yield_Tonnes_Ha", color="Season",
        category_orders={"Season": SEASON_ORDER}, color_discrete_map=SEASON_COLORS,
        title="Yield Distribution by Season (Tonnes/Hectare)",
    )
    st.plotly_chart(fig, width='stretch')

    st.subheader("Rainfall & temperature by season")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(
            fdf, x="Season", y="Rainfall_mm", color="Season",
            category_orders={"Season": SEASON_ORDER}, color_discrete_map=SEASON_COLORS,
            title="Rainfall by Season",
        )
        st.plotly_chart(fig, width='stretch')
    with c2:
        fig = px.box(
            fdf, x="Season", y="Avg_Temperature_C", color="Season",
            category_orders={"Season": SEASON_ORDER}, color_discrete_map=SEASON_COLORS,
            title="Temperature by Season",
        )
        st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------------------
# Page: Profit & Loss
# --------------------------------------------------------------------------------------
elif page == "Profit & Loss":
    st.title("💰 Profit & Loss Analysis")

    overall_loss_pct = round((fdf["Profit_INR"] < 0).mean() * 100, 2)
    st.metric("Farms currently running at a loss", f"{overall_loss_pct}%")

    loss_pct = (
        fdf.groupby("Season").apply(lambda x: (x["Profit_INR"] < 0).mean() * 100)
        .round(2)
        .reindex(SEASON_ORDER)
        .dropna()
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Profit summary statistics by season")
        st.dataframe(fdf.groupby("Season")["Profit_INR"].describe().round(2), width='stretch')
    with c2:
        st.subheader("% of loss-making farms by season")
        fig = px.bar(
            loss_pct, x=loss_pct.index, y=loss_pct.values, color=loss_pct.index,
            color_discrete_map=SEASON_COLORS,
            labels={"x": "Season", "y": "% Farms in Loss"},
            title="Percentage of Loss-Making Farms by Season",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width='stretch')

    st.markdown(
        """
        Almost half of all farms are running at a loss. Broken down by season, **Zaid**
        has the highest share of loss-making farms — likely because it depends more on
        irrigation (lower rainfall), which raises costs, while yields stay comparatively low.
        """
    )

    st.subheader("Profit distribution")
    fig = px.histogram(
        fdf, x="Profit_INR", color="Season", category_orders={"Season": SEASON_ORDER},
        color_discrete_map=SEASON_COLORS, barmode="overlay", opacity=0.6,
        title="Profit Distribution by Season",
    )
    fig.add_vline(x=0, line_dash="dash", line_color="black")
    st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------------------
# Page: Crop Yield
# --------------------------------------------------------------------------------------
elif page == "Crop Yield":
    st.title("🌱 Average Yield by Crop")

    crop_yield = fdf.groupby("Crop")["Yield_Tonnes_Ha"].mean().sort_values(ascending=False).round(2)
    fig = px.bar(
        crop_yield, x=crop_yield.index, y=crop_yield.values,
        labels={"x": "Crop", "y": "Yield (Tonnes/Hectare)"},
        title="Average Yield by Crop", color=crop_yield.values, color_continuous_scale="Greens",
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')

    st.markdown(
        """
        **Sugarcane** shows a much higher average yield than the other crops — that's
        expected, since sugarcane is naturally a high-yield crop measured in tonnes/ha.
        The remaining crops (Maize, Rice, Wheat, etc.) fall in a similar, smaller range.
        """
    )

    st.subheader("Explore a single crop")
    chosen_crop = st.selectbox("Pick a crop", sorted(fdf["Crop"].unique()))
    crop_df = fdf[fdf["Crop"] == chosen_crop]
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg yield (t/ha)", round(crop_df["Yield_Tonnes_Ha"].mean(), 2))
    c2.metric("Avg profit (₹)", f"{crop_df['Profit_INR'].mean():,.0f}")
    c3.metric("Records", len(crop_df))
    fig = px.box(
        crop_df, x="Season", y="Yield_Tonnes_Ha", color="Season",
        category_orders={"Season": SEASON_ORDER}, color_discrete_map=SEASON_COLORS,
        title=f"{chosen_crop} — Yield by Season",
    )
    st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------------------
# Page: Irrigation & Water Efficiency
# --------------------------------------------------------------------------------------
elif page == "Irrigation & Water Efficiency":
    st.title("💧 Irrigation Method & Water Efficiency")

    irrigation_eff = fdf.groupby("Irrigation_Method")["Water_Efficiency_t_per_1000m3"].mean().round(2)
    irrigation_eff = irrigation_eff.sort_values(ascending=False)
    fig = px.bar(
        irrigation_eff, x=irrigation_eff.index, y=irrigation_eff.values,
        labels={"x": "Irrigation Method", "y": "Water Efficiency (t per 1000 m³)"},
        title="Water Efficiency by Irrigation Method", color=irrigation_eff.index,
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width='stretch')

    st.markdown(
        """
        **Rainfed** farms show the highest water-efficiency value, followed by **Drip**,
        then **Sprinkler**; **Flood** irrigation has the lowest efficiency — expected, since
        flood irrigation typically uses far more water relative to the yield it produces.
        Drip irrigation's strong efficiency also matches what's generally taught about
        micro-irrigation methods.
        """
    )

    st.subheader("Water used vs. yield")
    fig = px.scatter(
        fdf, x="Water_Used_m3", y="Yield_Tonnes_Ha", color="Irrigation_Method",
        opacity=0.6, title="Water Used vs. Yield, by Irrigation Method",
        labels={"Water_Used_m3": "Water Used (m³)", "Yield_Tonnes_Ha": "Yield (t/ha)"},
    )
    st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------------------
# Page: Correlation with Yield
# --------------------------------------------------------------------------------------
elif page == "Correlation with Yield":
    st.title("🔗 Correlation with Yield")

    corr = fdf[numeric_cols_for_corr].corr().round(2)
    fig = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Correlation Heatmap",
    )
    fig.update_layout(height=650)
    st.plotly_chart(fig, width='stretch')

    st.markdown(
        """
        **Water efficiency** has the strongest correlation with yield — farms that use
        water more efficiently tend to produce more per hectare. Profit is moderately
        correlated with yield. Interestingly, rainfall, temperature, humidity, soil
        moisture, and fertilizer usage all show weak correlation with yield in this
        dataset — somewhat surprising, since rainfall might be expected to matter more directly.
        """
    )

    st.subheader("Seed quality across seasons")
    seed_q = fdf.groupby("Season")["Seed_Quality_Score"].mean().round(2).reindex(SEASON_ORDER).dropna()
    st.dataframe(seed_q.rename("Avg Seed Quality Score"), width='stretch')
    st.caption(
        "Seed quality score stays roughly constant across seasons, so it's unlikely to "
        "be a major driver of the season-to-season differences seen elsewhere."
    )


# --------------------------------------------------------------------------------------
# Page: Key Insights
# --------------------------------------------------------------------------------------
elif page == "Key Insights":
    st.title("🔑 Key Insights")

    st.markdown(
        """
        - **Kharif** season has the highest rainfall, the highest average yield, and also
          the highest disease/pest risk — monsoon conditions help crops grow but also
          raise disease risk.
        - **Zaid** season has the lowest rainfall and lowest yield, and the highest
          percentage of loss-making farms — the riskiest season financially.
        - Almost **half of all farms** in the dataset are running at a loss, which is a
          bigger concern than the seasonal differences alone.
        - **Water efficiency** is the strongest numeric driver of yield; irrigation method
          matters more than rainfall itself, with **Rainfed** and **Drip** methods
          outperforming **Flood** irrigation.
        - **Sugarcane** stands out with much higher yield than other crops, but that's an
          artifact of how sugarcane yield is measured, not a fundamentally different crop
          economics story.
        - **Seed quality** is fairly constant across seasons, so it doesn't explain the
          differences in yield or profitability between seasons.
        """
    )

    st.info(
        "Use the sidebar filters to slice these findings by state, crop, or season, "
        "and revisit any page to see how the numbers shift."
    )
