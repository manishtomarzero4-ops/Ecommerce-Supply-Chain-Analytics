from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-Commerce Supply Chain Analytics", page_icon="📦", layout="wide")
px.defaults.template = "plotly_white"

st.title("📦 E-Commerce Supply Chain Analytics")
st.caption("Interactive portfolio dashboard | Python · Pandas · Plotly · Streamlit")
st.info("Dataset note: this bundled dataset is synthetic and intended for analytics practice, not as evidence about a real company.")

DEFAULT_FILE = Path(__file__).parent / "ecommerce_supply_chain_messy_dataset.csv"
with st.sidebar:
    st.header("Data & filters")
    uploaded = st.file_uploader("Optional: upload a CSV", type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        source_label = uploaded.name
    elif DEFAULT_FILE.exists():
        raw = pd.read_csv(DEFAULT_FILE)
        source_label = DEFAULT_FILE.name
    else:
        st.error("No dataset found. Upload a CSV with the project columns.")
        st.stop()

required = ['product type','SKU','price','availability','number of product sold','revenue generated','stock levels','lead times','lead time','manufacturing lead time','defect rates','inspection results','transportation modes','routes','costs','location']
missing_cols = [c for c in required if c not in raw.columns]
if missing_cols:
    st.error("CSV is missing required columns: " + ", ".join(missing_cols))
    st.stop()

df = raw.drop_duplicates().copy()
for c in df.select_dtypes(include='object').columns:
    df[c] = df[c].astype('string').str.strip()
for c in ['product type','availability','inspection results','transportation modes']:
    df[c] = df[c].str.lower().str.title()
numeric = ['price','number of product sold','revenue generated','stock levels','lead times','lead time','manufacturing lead time','defect rates','costs','manufacturing costs','production volumes','order quantities']
for c in numeric:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')
if 'price' in df: df.loc[df['price'] < 0, 'price'] = np.nan
if 'stock levels' in df: df.loc[df['stock levels'] < 0, 'stock levels'] = np.nan
if 'defect rates' in df: df.loc[(df['defect rates'] < 0) | (df['defect rates'] > .20), 'defect rates'] = np.nan
for c in numeric:
    if c in df and df[c].isna().any(): df[c] = df[c].fillna(df[c].median())
for c in df.select_dtypes(include=['object','string']).columns:
    if df[c].isna().any():
        m = df[c].mode(dropna=True)
        df[c] = df[c].fillna(m.iloc[0] if not m.empty else 'Unknown')
df['stock_status'] = np.select([df['stock levels'] <= 100, df['stock levels'] <= 400], ['Low stock','Moderate stock'], default='Healthy stock')

with st.sidebar:
    st.caption(f"Source: {source_label} · {len(raw):,} raw rows")
    categories = sorted(df['product type'].dropna().unique().tolist())
    locations = sorted(df['location'].dropna().unique().tolist())
    modes = sorted(df['transportation modes'].dropna().unique().tolist())
    chosen_categories = st.multiselect("Product category", categories, default=categories)
    chosen_locations = st.multiselect("Location", locations, default=locations)
    chosen_modes = st.multiselect("Transportation mode", modes, default=modes)
    avail_options = sorted(df['availability'].dropna().unique().tolist())
    chosen_avail = st.multiselect("Availability", avail_options, default=avail_options)
    min_defect, max_defect = st.slider("Defect rate range", 0.0, 0.20, (0.0, 0.20), step=0.01, format="%.0f%%")
    st.caption("Low stock = 100 units or fewer (illustrative threshold).")

filtered = df[
    df['product type'].isin(chosen_categories) &
    df['location'].isin(chosen_locations) &
    df['transportation modes'].isin(chosen_modes) &
    df['availability'].isin(chosen_avail) &
    df['defect rates'].between(min_defect, max_defect)
].copy()
if filtered.empty:
    st.warning("No records match the selected filters. Widen one or more filters to continue.")
    st.stop()

revenue = filtered['revenue generated'].sum()
units = filtered['number of product sold'].sum()
avg_defect = filtered['defect rates'].mean()
avg_supplier = filtered['lead times'].mean()
transport_cost = filtered['costs'].sum()
low_stock_pct = (filtered['stock_status'].eq('Low stock').mean() * 100)

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Revenue generated", f"{revenue:,.0f}")
c2.metric("Units sold (sum)", f"{units:,.0f}")
c3.metric("Records analysed", f"{len(filtered):,}")
c4.metric("Average defect rate", f"{avg_defect:.1%}")
c5.metric("Transport cost (sum)", f"{transport_cost:,.0f}")
st.caption(f"Filtered data: {len(filtered):,} records · Average supplier lead time: {avg_supplier:.1f} days · Low-stock records: {low_stock_pct:.1f}%")

st.subheader("Sales & revenue")
a,b = st.columns(2)
cat = filtered.groupby('product type', as_index=False).agg(revenue=('revenue generated','sum'), units_sold=('number of product sold','sum'), records=('SKU','size'))
with a:
    st.plotly_chart(px.bar(cat.sort_values('revenue',ascending=False), x='product type', y='revenue', color='units_sold', hover_data=['units_sold','records'], title='Revenue by category', labels={'product type':'Category','revenue':'Revenue'}), use_container_width=True)
with b:
    st.plotly_chart(px.pie(cat, names='product type', values='units_sold', hole=.45, title='Unit sales mix'), use_container_width=True)

st.subheader("Inventory & quality")
a,b = st.columns(2)
with a:
    stock = filtered.groupby('stock_status', as_index=False).size()
    st.plotly_chart(px.bar(stock, x='stock_status', y='size', color='stock_status', title='Records by stock status', labels={'size':'Records','stock_status':'Stock status'}), use_container_width=True)
with b:
    quality = filtered.groupby('product type', as_index=False).agg(avg_defect=('defect rates','mean'), records=('SKU','size')).sort_values('avg_defect',ascending=False)
    chart = px.bar(quality, x='product type', y='avg_defect', color='avg_defect', hover_data=['records'], title='Average defect rate by category', labels={'avg_defect':'Average defect rate','product type':'Category'})
    chart.update_yaxes(tickformat='.0%')
    st.plotly_chart(chart, use_container_width=True)

st.subheader("Lead time & transportation")
a,b = st.columns(2)
with a:
    lead = filtered.groupby('product type', as_index=False).agg(supplier=('lead times','mean'), manufacturing=('manufacturing lead time','mean'), additional=('lead time','mean'))
    lead_long = lead.melt(id_vars='product type', var_name='lead_time_type', value_name='days')
    st.plotly_chart(px.bar(lead_long, x='product type', y='days', color='lead_time_type', barmode='group', title='Average lead-time components', labels={'days':'Average days','product type':'Category'}), use_container_width=True)
with b:
    trans = filtered.groupby('transportation modes', as_index=False).agg(total_cost=('costs','sum'), avg_cost=('costs','mean'), records=('SKU','size')).sort_values('total_cost',ascending=False)
    st.plotly_chart(px.bar(trans, x='transportation modes', y='total_cost', color='transportation modes', hover_data=['avg_cost','records'], title='Transportation cost by mode', labels={'total_cost':'Total cost','transportation modes':'Mode'}), use_container_width=True)

st.subheader("Route analysis")
route = filtered.groupby('routes', as_index=False).agg(total_cost=('costs','sum'), avg_cost=('costs','mean'), records=('SKU','size')).sort_values('total_cost',ascending=False)
st.plotly_chart(px.bar(route, x='routes', y='avg_cost', color='total_cost', hover_data=['total_cost','records'], title='Average transport cost by route', labels={'avg_cost':'Average cost','routes':'Route'}), use_container_width=True)

st.subheader("Dynamic business observations")
if not cat.empty:
    top_rev = cat.loc[cat['revenue'].idxmax()]
    top_units = cat.loc[cat['units_sold'].idxmax()]
    top_def = quality.loc[quality['avg_defect'].idxmax()]
    top_mode = trans.loc[trans['total_cost'].idxmax()]
    st.markdown(f"- **Revenue leader:** {top_rev['product type']} with {top_rev['revenue']:,.0f} revenue generated in the current filter.")
    st.markdown(f"- **Unit-sales leader:** {top_units['product type']} with {top_units['units_sold']:,.0f} units summed across records.")
    st.markdown(f"- **Quality watchlist:** {top_def['product type']} has the highest average defect rate ({top_def['avg_defect']:.1%}) in this view.")
    st.markdown(f"- **Transport cost leader:** {top_mode['transportation modes']} has the highest total transport cost ({top_mode['total_cost']:,.0f}) in this view; compare average cost and record count before acting.")

with st.expander("View filtered data and download results"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button("Download filtered CSV", data=filtered.to_csv(index=False).encode('utf-8'), file_name='ecommerce_supply_chain_filtered.csv', mime='text/csv')

st.caption("Interpretation note: the data is synthetic, rows are not necessarily orders, and lead-time fields need business validation. Use these charts to demonstrate an analytical workflow—not to claim real operational performance.")
