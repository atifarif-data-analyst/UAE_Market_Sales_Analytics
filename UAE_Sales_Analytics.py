"""
UAESales Analytics Dashboard  —  Streamlit + Pandas + Plotly
==============================================================
A fully interactive sales dashboard for UAE Market (UAE digital-services data,
2023-2024). All metrics are computed in Pandas; charts are Plotly.

Run:
    pip install -r requirements.txt
    streamlit run app.py

Author: Atif Arif
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from pathlib import Path

# --------------------------------------------------------------------------- #
#  PAGE CONFIG + LIGHT STYLING
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="UAE Sales Analytics Dashboard",
                   page_icon="\U0001F4CA", layout="wide")



# --------------------------------------------------------------------------- #
#  CONSTANTS
# --------------------------------------------------------------------------- #
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
PALETTE = ['#6366f1', '#f59e0b', '#10b981', '#0ea5e9',
           '#ec4899', '#8b5cf6', '#f97316', '#14b8a6']
CITY_COLORS = {'Dubai': '#6366f1', 'Abu Dhabi': '#0ea5e9', 'Ajman': '#10b981',
               'Al Ain': '#f59e0b', 'Sharjah': '#ec4899'}
ACCENT = '#f59e0b'
GRID = 'rgba(26,31,60,.08)'

# Shared Plotly display config — guarantees the mode bar, zoom, pan and
# hover stay enabled on every chart (passed to each st.plotly_chart call).
PLOTLY_CONFIG = {"displayModeBar": True, "scrollZoom": True,
                 "displaylogo": False, "staticPlot": False}


# --------------------------------------------------------------------------- #
#  DATA LOADING
# --------------------------------------------------------------------------- #
@st.cache_data
def load_data(filename: str = "UAE_sales_data.csv") -> pd.DataFrame:
    """Load the sales CSV and add a margin-amount column.

    margin_pct is stored as a rate (0.30 = 30%); the margin AMOUNT in
    currency is sales * margin_pct, computed once here so every chart
    can sum it directly.
    """
    csv_path = Path(__file__).parent / filename
    df = pd.read_csv(csv_path)
    df["year"] = df["year"].astype(str)
    df["margin_amt"] = df["sales"] * df["margin_pct"]
    # Make month sort calendar-correct, not alphabetical.
    df["month"] = pd.Categorical(df["month"], categories=MONTHS, ordered=True)
    return df


def fmt_k(n: float) -> str:
    """Format a number as 1.2M / 34.5K / 980 for compact display."""
    if n >= 1e6:
        return f"{n/1e6:.2f}M"
    if n >= 1e3:
        return f"{n/1e3:.1f}K"
    return f"{round(n):,}"

def summarize(data: pd.DataFrame, dim: str) -> pd.DataFrame:
    """Group by one dimension and return sales, margin amount, order count,
    and margin %. This is the Pandas equivalent of the original groupBy()."""
    g = (data.groupby(dim, observed=True)
         .agg(sales=("sales", "sum"),
              margin=("margin_amt", "sum"),
              orders=("sales", "size"))
         .reset_index())
    g["margin_pct"] = (g["margin"] / g["sales"] * 100).round(1)
    return g.sort_values("sales", ascending=False)


def style_fig(fig, height=360):
    # Resolve text color from the active Streamlit theme so labels stay
    # visible in both light and dark mode. Falls back to a mid-grey that
    # reads acceptably on either background.
    try:
        text_color = st.get_option("theme.textColor") or "#94a3b8"
    except Exception:
        text_color = "#94a3b8"

    # If this chart has a title, reserve extra top room and pin the title
    # cleanly above the plot/legend so it can't overlap surrounding content.
    has_title = bool(getattr(fig.layout.title, "text", None))
    top_margin = 70 if has_title else 40
    if has_title:
        fig.update_layout(
            title=dict(x=0, xanchor="left", y=0.98, yanchor="top",
                       font=dict(color=text_color, size=16)),
            # legend sits below the title, inside the reserved top margin
            legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
        )

    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=top_margin, b=10),
        # Transparent backgrounds let the chart inherit the page color
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=text_color, size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(bgcolor="#1a1f3c", font_color="white"),
    )
    # Explicitly color axis titles AND tick labels so neither disappears
    fig.update_xaxes(gridcolor=GRID, zeroline=False,
                     title_font_color=text_color, tickfont_color=text_color)
    fig.update_yaxes(gridcolor=GRID, zeroline=False,
                     title_font_color=text_color, tickfont_color=text_color)
    return fig


df = load_data()

# --------------------------------------------------------------------------- #
#  HEADER
# --------------------------------------------------------------------------- #
st.markdown(
    '<div class="aic-banner"><h1>\U0001F4CA UAE Market Sales Analytics</h1>'
    '<p>UAE digital-services performance &middot; 2023&ndash;2024 &middot; '
    'revenue, margin &amp; customer intelligence</p></div>',
    unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
#  SIDEBAR — GLOBAL FILTERS
# --------------------------------------------------------------------------- #
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Year", ["All"] + sorted(df["year"].unique()))
city = st.sidebar.selectbox("City", ["All"] + sorted(df["city"].unique()))

# Build a boolean mask — the Pandas equivalent of the original getFiltered().
mask = pd.Series(True, index=df.index)
if year != "All":
    mask &= df["year"] == year
if city != "All":
    mask &= df["city"] == city
fdf = df[mask]

st.sidebar.markdown("---")
st.sidebar.download_button(
    "\u2b07 Export filtered data (CSV)",
    data=fdf.to_csv(index=False).encode("utf-8"),
    file_name="AIC_Sales_Export.csv", mime="text/csv")
st.sidebar.caption(f"{len(fdf):,} of {len(df):,} records shown")

# --------------------------------------------------------------------------- #
#  TABS
# --------------------------------------------------------------------------- #
tab_overview, tab_customers, tab_breakdown, tab_story = st.tabs(
    ["\U0001F4C8 Overview", "\U0001F465 Customers",
     "\U0001F9E9 Breakdown", "\U0001F4D6 Story"])

# ============================ OVERVIEW ===================================== #
with tab_overview:
    total_sales = fdf["sales"].sum()
    total_margin = fdf["margin_amt"].sum()
    total_cost = total_sales - total_margin
    margin_pct = (total_margin / total_sales * 100) if total_sales else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Sales", fmt_k(total_sales))
    k2.metric("Total Cost", fmt_k(total_cost))
    k3.metric("Total Margin", fmt_k(total_margin))
    k4.metric("Margin %", f"{margin_pct:.1f}%")
    k5.metric("Orders", f"{len(fdf):,}")

    st.markdown("---")

    # --- Monthly combo: bar (metric) + margin% line ---------------------- #
    left, right = st.columns([0.62, 0.38])

    with left:
        metric = st.radio("Bar metric", ["Sales", "Cost", "Margin"],
                          horizontal=True, key="ov_metric")
        yoy = st.checkbox("Compare 2023 vs 2024", value=False)

        monthly = (fdf.groupby("month", observed=True)
                   .agg(sales=("sales", "sum"), margin=("margin_amt", "sum"))
                   .reindex(MONTHS).fillna(0))
        monthly["cost"] = monthly["sales"] - monthly["margin"]
        monthly["mpct"] = (monthly["margin"] /
                           monthly["sales"].replace(0, pd.NA) * 100).fillna(0)

        fig = go.Figure()
        if yoy:
            # Ignore the year filter here so both years are always comparable;
            # still respect the city filter.
            ydf = df[df["city"] == city] if city != "All" else df
            for yr, clr in [("2023", "#bfdbfe"), ("2024", "#c7d2fe")]:
                s = (ydf[ydf["year"] == yr].groupby("month", observed=True)["sales"]
                     .sum().reindex(MONTHS, fill_value=0))
                fig.add_bar(x=MONTHS, y=s.values, name=yr, marker_color=clr,
                            marker_line=dict(color="#6366f1", width=1.5))
        else:
            col_key, col_clr = {"Sales": ("sales", "#6366f1"),
                                "Cost": ("cost", "#0ea5e9"),
                                "Margin": ("margin", "#10b981")}[metric]
            fig.add_bar(x=MONTHS, y=monthly[col_key].values, name=metric,
                        marker_color=col_clr, opacity=0.85,
                        text=[fmt_k(v) for v in monthly[col_key].values],
                        textposition="outside")
        fig.add_scatter(x=MONTHS, y=monthly["mpct"].values, name="Margin %",
                        yaxis="y2", mode="lines+markers",
                        line=dict(color=ACCENT, width=2.5))
        fig.update_layout(
            title="Monthly Performance",
            yaxis2=dict(overlaying="y", side="right", range=[0, 50],
                        ticksuffix="%", showgrid=False),
            barmode="group")
        style_fig(fig, 400)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key="ov_monthly")

    with right:
        st.markdown("##### Sales by City")
        cg = summarize(fdf, "city")
        figc = go.Figure(go.Bar(
            x=cg["sales"], y=cg["city"], orientation="h",
            marker_color=[CITY_COLORS.get(c, "#6366f1") for c in cg["city"]],
            text=[fmt_k(v) for v in cg["sales"]], textposition="outside"))
        figc.update_layout(yaxis=dict(autorange="reversed"),
                           title="Revenue per city")
        style_fig(figc, 400)
        st.plotly_chart(figc, use_container_width=True, config=PLOTLY_CONFIG, key="ov_city")

    # --- Dynamic breakdown selector -------------------------------------- #
    st.markdown("##### Breakdown explorer")
    dim = st.selectbox(
        "Group by", ["service", "dept", "package", "sale_type",
                     "cust_source", "cust_type", "customer"], index=0)
    g = summarize(fdf, dim).head(15)
    figd = go.Figure()
    figd.add_bar(x=g[dim], y=g["sales"], name="Sales", opacity=0.85,
                 marker_color=[PALETTE[i % len(PALETTE)] for i in range(len(g))],
                 text=[fmt_k(v) for v in g["sales"]], textposition="outside")
    figd.add_scatter(x=g[dim], y=g["margin_pct"], name="Margin %", yaxis="y2",
                     mode="lines+markers", line=dict(color=ACCENT, width=2.5))
    figd.update_layout(
        yaxis2=dict(overlaying="y", side="right", range=[0, 50],
                    ticksuffix="%", showgrid=False),
        title=f"Sales & margin by {dim.replace('_', ' ')}")
    style_fig(figd, 380)
    st.plotly_chart(figd, use_container_width=True, config=PLOTLY_CONFIG, key="ov_breakdown")


# ============================ CUSTOMERS ==================================== #
with tab_customers:
    st.markdown("### Customer Intelligence")

    f1, f2, f3, f4 = st.columns(4)
    ctype = f1.selectbox("Customer Type", ["All"] + sorted(df["cust_type"].unique()))
    csrc = f2.selectbox("Source", ["All"] + sorted(df["cust_source"].unique()))
    stype = f3.selectbox("Sale Type", ["All"] + sorted(df["sale_type"].unique()))
    search = f4.text_input("Search customer name")

    cdf = fdf.copy()
    if ctype != "All":
        cdf = cdf[cdf["cust_type"] == ctype]
    if csrc != "All":
        cdf = cdf[cdf["cust_source"] == csrc]
    if stype != "All":
        cdf = cdf[cdf["sale_type"] == stype]
    if search:
        cdf = cdf[cdf["customer"].str.contains(search, case=False, na=False)]

    cust = summarize(cdf, "customer")
    st.caption(f"\U0001F465 {len(cust)} customers match")

    lc, rc = st.columns(2)
    with lc:
        st.markdown("##### Leaderboard")
        board = cust.copy()
        board.insert(0, "Rank", range(1, len(board) + 1))
        board["Sales"] = board["sales"].map(fmt_k)
        board["Margin %"] = board["margin_pct"].astype(str) + "%"
        st.dataframe(
            board[["Rank", "customer", "Sales", "Margin %", "orders"]]
            .rename(columns={"customer": "Customer", "orders": "Orders"}),
            hide_index=True, use_container_width=True, height=440)

    with rc:
        st.markdown("##### Value vs Margin (each dot = a customer)")
        if len(cust):
            avg = cust["sales"].mean()

            def quadrant(row):
                if row.sales >= avg and row.margin_pct >= 30.5:
                    return "#6366f1"   # high value, high margin  (stars)
                if row.sales < avg and row.margin_pct >= 30.5:
                    return "#f59e0b"   # low value, high margin
                if row.sales >= avg:
                    return "#0ea5e9"   # high value, low margin
                return "#ef4444"       # low value, low margin

            cust["color"] = cust.apply(quadrant, axis=1)
            figs = go.Figure(go.Scatter(
                x=cust["sales"], y=cust["margin_pct"], mode="markers",
                marker=dict(size=14, color=cust["color"],
                            line=dict(width=1.5, color="white")),
                text=cust["customer"],
                hovertemplate="%{text}<br>Sales %{x:,.0f}"
                              "<br>Margin %{y}%<extra></extra>"))
            figs.add_vline(x=avg, line_dash="dash", line_color="#94a3b8")
            figs.add_hline(y=30.5, line_dash="dash", line_color="#94a3b8")
            figs.update_layout(xaxis_title="Total Sales \u2192",
                               yaxis_title="Margin % \u2192")
            figs.update_yaxes(range=[20, 45], ticksuffix="%")
            style_fig(figs, 440)
            st.plotly_chart(figs, use_container_width=True, config=PLOTLY_CONFIG, key="cust_scatter")


# ============================ BREAKDOWN ==================================== #
with tab_breakdown:
    st.markdown("### Portfolio Breakdown")
    b1, b2 = st.columns(2)

    with b1:
        st.markdown("##### Department mix")
        dg = summarize(fdf, "dept")
        figdept = go.Figure(go.Pie(
            labels=dg["dept"], values=dg["sales"], hole=0.6,
            marker=dict(colors=PALETTE, line=dict(color="white", width=3)),
            textinfo="label+percent"))
        style_fig(figdept, 360)
        st.plotly_chart(figdept, use_container_width=True, config=PLOTLY_CONFIG, key="pf_dept")

        st.markdown("##### Sales by service")
        sg = summarize(fdf, "service")
        figsvc = go.Figure(go.Bar(
            x=sg["service"], y=sg["sales"], opacity=0.85,
            marker_color=[PALETTE[i % len(PALETTE)] for i in range(len(sg))],
            text=[fmt_k(v) for v in sg["sales"]], textposition="outside"))
        style_fig(figsvc, 340)
        st.plotly_chart(figsvc, use_container_width=True, config=PLOTLY_CONFIG, key="pf_service")

    with b2:
        st.markdown("##### Sale type")
        stg = summarize(fdf, "sale_type")
        figst = go.Figure(go.Pie(
            labels=stg["sale_type"], values=stg["sales"], hole=0.6,
            marker=dict(colors=["#6366f1", "#f59e0b"],
                        line=dict(color="white", width=3)),
            textinfo="label+percent"))
        style_fig(figst, 360)
        st.plotly_chart(figst, use_container_width=True, config=PLOTLY_CONFIG, key="pf_saletype")

        st.markdown("##### Sales by package")
        pg = summarize(fdf, "package")
        figpkg = go.Figure(go.Bar(
            x=pg["sales"], y=pg["package"], orientation="h", opacity=0.85,
            marker_color=[PALETTE[i % len(PALETTE)] for i in range(len(pg))],
            text=[fmt_k(v) for v in pg["sales"]], textposition="outside"))
        figpkg.update_layout(yaxis=dict(autorange="reversed"))
        style_fig(figpkg, 340)
        st.plotly_chart(figpkg, use_container_width=True, config=PLOTLY_CONFIG, key="pf_package")


# ============================ STORY ======================================== #
with tab_story:
    s23 = df[df["year"] == "2023"]["sales"].sum()
    s24 = df[df["year"] == "2024"]["sales"].sum()
    growth = (s24 - s23) / s23 * 100 if s23 else 0
    ts = fdf["sales"].sum()
    tm = fdf["margin_amt"].sum()
    mp = tm / ts * 100 if ts else 0

    top_city = summarize(fdf, "city").iloc[0]
    cust_all = summarize(fdf, "customer")
    top_cust = cust_all.iloc[0]
    best_dept = summarize(fdf, "dept").sort_values("margin_pct",
                                                   ascending=False).iloc[0]
    repeat = summarize(fdf, "sale_type").iloc[0]
    repeat_pct = repeat["sales"] / ts * 100 if ts else 0

    st.markdown(f"## From {fmt_k(s23)} to {fmt_k(s24)} — a {growth:.1f}% growth story")
    st.write(f"Across 2023-2024, AIC generated {fmt_k(ts)} in the current view "
             f"at a {mp:.1f}% margin, spread over 5 UAE cities.")

    c1, c2, c3 = st.columns(3)
    c1.info(f"\U0001F3D9 **Top market** — {top_city['city']} "
            f"({top_city['sales']/ts*100:.1f}% of revenue)")
    c2.success(f"\U0001F48E **Best-margin dept** — {best_dept['dept']} "
               f"at {best_dept['margin_pct']}%")
    c3.warning(f"\u2B50 **Top customer** — {top_cust['customer']} "
               f"({top_cust['sales']/ts*100:.1f}% of revenue)")
    c4, c5, c6 = st.columns(3)
    c4.info("\U0001F680 **Seasonality** — H2 beats H1 every year; July peaks.")
    c5.success(f"\U0001F501 **Loyalty** — repeat sales = {repeat_pct:.0f}% of revenue.")
    c6.warning("\u26A0 **Watch** — SEO & Ads sit near 25% margin, below the average.")

    st.markdown("##### 24-month revenue trajectory")
    labels, vals = [], []
    for yr in ("2023", "2024"):
        for m in MONTHS:
            labels.append(f"{m} '{yr[2:]}")
            vals.append(fdf[(fdf["month"] == m) & (fdf["year"] == yr)]["sales"].sum())
    figtl = go.Figure(go.Scatter(
        x=labels, y=vals, mode="lines+markers",
        fill="tozeroy",
        line=dict(color="#6366f1", width=2.5),
        marker=dict(size=7),
        customdata=[fmt_k(v) for v in vals],
        hovertemplate="<b>%{x}</b><br>Revenue: %{customdata}<extra></extra>"))
    style_fig(figtl, 320)
    figtl.update_layout(hovermode="x unified")
    st.plotly_chart(figtl, use_container_width=True, config=PLOTLY_CONFIG, key="story_trajectory")

    s1, s2 = st.columns(2)
    with s1:
        st.markdown("##### Service mix by year")
        mix = (fdf.groupby(["year", "service"], observed=True)["sales"]
               .sum().reset_index())
        figmix = px.bar(mix, x="year", y="sales", color="service",
                        color_discrete_sequence=PALETTE, barmode="stack")
        figmix.update_traces(
            hovertemplate="<b>%{fullData.name}</b> (%{x})"
                          "<br>Revenue: %{y:,.0f}<extra></extra>")
        style_fig(figmix, 340)
        st.plotly_chart(figmix, use_container_width=True, config=PLOTLY_CONFIG, key="story_servicemix")
    with s2:
        st.markdown("##### Top 5 customers")
        top5 = cust_all.head(5)
        fig5 = go.Figure(go.Bar(
            x=top5["customer"].str.split().str[0], y=top5["sales"],
            marker_color=PALETTE[:5], opacity=0.85,
            text=[fmt_k(v) for v in top5["sales"]], textposition="outside"))
        style_fig(fig5, 340)
        st.plotly_chart(fig5, use_container_width=True, config=PLOTLY_CONFIG, key="story_top5")

st.caption("Built with Streamlit, Pandas & Plotly · data: UAE sales 2023-2024")
