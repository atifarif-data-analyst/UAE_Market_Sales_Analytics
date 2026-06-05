# Data Dictionary

The app runs on `data/UAE_sales_data.csv` — **480 records, 12 columns**, covering
a UAE digital-services agency's sales across **2023–2024** and **5 emirates**.

| Column | Type | Description |
|---|---|---|
| `month` | Text | Month abbreviation (Jan–Dec), sorted calendar-correct in the app |
| `year` | Integer | 2023 or 2024 |
| `customer` | Text | Client name (32 distinct customers) |
| `cust_type` | Text | Company or Individual |
| `service` | Text | Social Media, Ads, App Dev, Web Dev, SEO |
| `dept` | Text | Marketing, Design, Copywriting |
| `city` | Text | Dubai, Abu Dhabi, Ajman, Al Ain, Sharjah |
| `sales` | Decimal | Revenue for the record (AED) |
| `margin_pct` | Decimal | Margin rate (e.g. 0.30 = 30%) |
| `sale_type` | Text | New Sale or Repeat Sale |
| `cust_source` | Text | Walk in, Ads, Organic |
| `package` | Text | Monthly, Quarterly, Bi Annual, Annual |

## Derived in the app

| Field | How it's computed |
|---|---|
| `margin_amt` | `sales × margin_pct` — the margin in currency, added at load time |
| Total Sales / Margin / Cost | Sums of `sales`, `margin_amt`, and their difference over the filtered set |
| Margin % | `Total Margin / Total Sales × 100` |
| Orders | Row count of the filtered set |
| Monthly aggregates | Group by `month` (reindexed to calendar order) |
| YoY growth | 2024 sales vs 2023 sales |
| Customer quadrant | Each customer classified by sales (vs average) and margin % (vs 30.5% line) |
