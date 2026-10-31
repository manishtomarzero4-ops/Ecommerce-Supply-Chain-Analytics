# E-Commerce Supply Chain Analytics

An end-to-end Data Analyst portfolio project using Python, Pandas, Plotly and Streamlit. The project audits a messy dataset, cleans it, explores sales, inventory, lead times, product quality and transportation costs, and presents the results in an interactive dashboard.

> **Important:** the included data is synthetic and generated for practice. Do not describe it as real company data.

## Files
- `Ecommerce_Supply_Chain_Analytics.ipynb` — end-to-end notebook with data audit, cleaning, EDA, interactive Plotly charts, insights and export.
- `app.py` — interactive Streamlit dashboard with filters, charts, dynamic observations and CSV download.
- `ecommerce_supply_chain_messy_dataset.csv` — bundled raw synthetic dataset.
- `requirements.txt` — Python dependencies.

## Run the notebook
1. Extract the project folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Open `Ecommerce_Supply_Chain_Analytics.ipynb` in Jupyter Notebook/JupyterLab.
4. Run cells from top to bottom. The CSV must stay beside the notebook.

## Run the interactive dashboard locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
The dashboard opens in your browser. Use sidebar filters to explore categories, locations, transport modes, availability and defect-rate range. You can also upload a compatible CSV.

## Deploy the dashboard
Push `app.py`, `requirements.txt`, and `ecommerce_supply_chain_messy_dataset.csv` to a GitHub repository. In Streamlit Community Cloud, create an app from that repository, choose `app.py` as the main file, and deploy. Do not upload private/customer data.

## Analytical scope
- Data-quality audit: missingness, duplicate rows, inconsistent categories and invalid values.
- Sales: category revenue and units sold.
- Inventory: stock status and availability.
- Lead times: supplier, manufacturing and additional lead-time fields.
- Quality: defect rates and inspection outcomes.
- Logistics: transportation modes and routes.

## Important limitations
The dataset has no real dates or order IDs, so it cannot support time-series trends, on-time delivery rate, true order-level profit or customer retention. SKU values may repeat across generated records. The notebook documents assumptions such as the low-stock threshold and defect-rate outlier rule.

## Resume-ready project bullet
**E-Commerce Supply Chain Analytics | Python, Pandas, Plotly, Streamlit** — Cleaned and analysed a synthetic supply-chain dataset; investigated sales, inventory, lead times, defect rates and logistics costs; built an interactive dashboard with filters, KPI summaries and downloadable data.
