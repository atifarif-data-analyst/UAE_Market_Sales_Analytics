# 📊 UAE Market Sales Analytics Dashboard

An interactive sales-analytics dashboard for the UAE digital-services market (2023–2024), built with **Streamlit**, **Pandas**, and **Plotly**. All metrics are computed in Pandas and rendered as fully interactive Plotly charts with zoom, pan, hover tooltips, and a global filter layer.

> **Live demo:** _add your Streamlit Cloud link here_

---

## ✨ Features

- **Global filters** — slice the entire dashboard by **Year** and **City** from the sidebar; every chart and KPI updates instantly.
- **Four analysis tabs**
  - **📈 Overview** — headline KPIs (total sales, margin, margin %, orders), monthly revenue vs. margin trend, and a sales-by-city breakdown.
  - **👥 Customers** — customer leaderboard plus a value-vs-margin scatter where each dot is a customer.
  - **🧩 Breakdown** — portfolio mix by department, service, sale type, and package.
  - **📖 Story** — narrative insights: 24-month revenue trajectory, service mix by year, and top-5 customers.
- **Interactive charts** — unified hover tooltips, compact `K`/`M` value formatting, theme-aware text colour for light/dark mode, and a persistent Plotly mode bar.
- **Export** — download the currently filtered dataset as CSV from the sidebar.

---

## 🛠 Tech Stack

| Layer | Tools |
|-------|-------|
| App framework | Streamlit |
| Data wrangling | Pandas |
| Visualisation | Plotly (Graph Objects + Express) |
| Language | Python 3.9+ |

---

## 📂 Project Structure

```
.
├── app.py                 # main dashboard application
├── UAE_sales_data.csv     # source dataset (2023–2024)
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/uae-sales-analytics.git
cd uae-sales-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## 📑 Dataset

Tabular sales records for UAE digital-services covering 2023–2024, with fields including `month`, `year`, `customer`, `cust_type`, `service`, `dept`, `city`, `sales`, `margin_pct`, `sale_type`, `cust_source`, and `package`. A `margin_amt` column (`sales × margin_pct`) is derived at load time so every chart can sum margin directly.

---

## 📈 Key Metrics Computed

- Total revenue, total margin, and blended margin %
- Order counts and repeat-business share
- Monthly revenue and margin trajectory across 24 months
- Per-city, per-department, per-service, and per-package contribution
- Customer-level value and margin profiling

---

## 👤 Author

**Atif Arif** — Physicist & Data Analyst

---

## 📜 License

Released under the MIT License. See [`LICENSE`](LICENSE) for details.
