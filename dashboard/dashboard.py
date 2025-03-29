import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st
import plotly.express as px
from datetime import datetime
from babel.numbers import format_currency

sns.set_style("darkgrid")


# Helper function
# No 1
def create_daily_orders(df):
    daily_orders_df = df.resample(rule="D", on="order_purchase_date").agg(
        {"order_id": "nunique", "price": "sum"}
    )
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(
        columns={"order_id": "order_count", "price": "revenue"}, inplace=True
    )
    return daily_orders_df


# No 2
def create_sum_order_itmes(df):
    sum_order_items_df = (
        df.groupby("product_category_name_english")
        .order_item_id.sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    return sum_order_items_df


# No 3
def create_customers_spend_money(df):
    customers_spend_df = df.resample(rule="ME", on="order_purchase_date").agg(
        {"payment_value": "sum"}
    )
    customers_spend_df.index = customers_spend_df.index.strftime("%B %Y")
    customers_spend_df = customers_spend_df.round().reset_index()
    customers_spend_df.rename(columns={"payment_value": "total_spend"}, inplace=True)
    return customers_spend_df


# No 4
def create_customer_review_score(df):
    customer_review_df = (
        df.groupby(by="product_category_name_english")
        .agg({"review_score": "mean"})
        .reset_index()
        .sort_values(by="review_score", ascending=False)
    )
    customer_review_df.review_score = round(customer_review_df.review_score, 1)
    return customer_review_df


# No 5
# a
def create_customer_by_payment_type(df):
    by_payment_type_df = (
        df.groupby(by="payment_type").customer_id.nunique().reset_index()
    )
    by_payment_type_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    by_payment_type_df = by_payment_type_df.sort_values(
        by="customer_count", ascending=False
    )
    return by_payment_type_df


# b
def create_customer_by_city(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    bycity_df = bycity_df.sort_values(by="customer_count", ascending=False)
    return bycity_df


# c
def create_customer_by_state(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    bystate_df = bystate_df.sort_values(by="customer_count", ascending=False)
    return bystate_df


# No 6
def create_customer_density_map(dataframe):
    # Create density map figure
    fig = px.density_map(
        dataframe,
        lat="geolocation_lat",
        lon="geolocation_lng",
        z="customer_count",
        radius=15,
        center=dict(lat=-14.2350, lon=-51.9253),
        zoom=3.4,
        color_continuous_scale="Greens",
        map_style="carto-voyager",
        template="plotly_white",
    )
    # Update figure layout
    fig.update_layout(
        width=600,
        height=700,
        margin={"r": 1, "t": 1, "l": 1, "b": 1},
        paper_bgcolor="#009600",
    )
    # Update colorbar location and orientation
    fig.update_coloraxes(
        showscale=True,
        colorbar=dict(
            len=0.4,
            yanchor="top",
            y=1,
            xanchor="center",
            orientation="h",
            thickness=10,
            title="Customer Count",
            title_side="top",
            title_font_size=14,
            title_font_weight=700,
        ),
    )
    return fig


# Load cleaned data
all_df = pd.read_csv("./dashboard/all_data.csv")
map_df = pd.read_csv("./dashboard/map_data.csv")

# Change data type
datetime_columns = [
    "order_purchase_date",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "review_creation_date",
    "review_answer_date",
    "shipping_limit_date",
]
all_df.sort_values(by="order_purchase_date", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Dashboard title
st.header("Brazilian E-commerce Dashboard :sparkles:")

# Filter data
min_date = all_df["order_purchase_date"].min()
max_date = all_df["order_purchase_date"].max()

# Sidebar
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image(
        "https://raw.githubusercontent.com/ykbintang/ecommerce-dashboard/refs/heads/main/dashboard/assets/logo.png"
    )

    # Membuat inputan tanggal
    start_date = st.date_input(
        "Pilih tangal awal", value=min_date, min_value=min_date, max_value=max_date
    )
    end_date = st.date_input(
        "Pilih tanggal akhir", value=max_date, min_value=min_date, max_value=max_date
    )

    # Validasi agar start_date tidak lebih besar dari end_date
    if start_date > end_date:
        st.error("Tanggal awal tidak boleh lebih besar dari tanggal akhir!")

    # Menampilkan hasil yang dipilih
    st.write("Rentang tanggal yang dipilih:\n\n", start_date, "-", end_date)


main_df = all_df[
    (all_df["order_purchase_date"] >= str(start_date))
    & (all_df["order_purchase_date"] <= str(end_date))
]

# Menyiapkan berbagai dataframe
daily_orders_df = create_daily_orders(main_df)
sum_order_items_df = create_sum_order_itmes(main_df)
customers_spend_df = create_customers_spend_money(main_df)
customer_review_df = create_customer_review_score(main_df)
by_payment_type_df = create_customer_by_payment_type(main_df)
bycity_df = create_customer_by_city(main_df)
bystate_df = create_customer_by_state(main_df)

# 1. Plot Number of daily orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "R$ ", locale="es_CO"
    )
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_date"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#009600",
)
ax.set_ylabel("Order Count", fontsize=20)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=20)
st.pyplot(fig)

# 2. Product performance
st.subheader("Best and Worst Performing Product by Number of Sales")

colors = ["#009600", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
sns.barplot(
    data=sum_order_items_df.head(),
    x="order_item_id",
    y="product_category_name_english",
    hue="product_category_name_english",
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=35)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=40)
ax[0].tick_params(axis="x", labelsize=40)

sns.barplot(
    data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(),
    x="order_item_id",
    y="product_category_name_english",
    hue="product_category_name_english",
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=35)
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=40)
ax[1].tick_params(axis="x", labelsize=40)
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
st.pyplot(fig)

# 3. Customers spend money
st.subheader("Customers Spend Money per Month")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    customers_spend_df["order_purchase_date"],
    customers_spend_df["total_spend"],
    marker="o",
    linewidth=2,
    color="#009600",
)
ax.set_ylabel("Real Brasil (R$)", fontsize=20)
ax.tick_params(axis="y", labelsize=15)
ax.tick_params(axis="x", labelsize=15, rotation=45)
plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
st.pyplot(fig)

# 4. Customers review score
st.subheader("Top 5 Category Product with Highest Review Score")

fig, ax = plt.subplots(figsize=(16, 8))
ax = sns.barplot(
    data=customer_review_df.head(),
    x="review_score",
    y="product_category_name_english",
    hue="product_category_name_english",
    palette=colors,
)
ax.set_ylabel(None)
ax.set_xlabel("Review Score", fontsize=25)
ax.tick_params(axis="y", labelsize=25)
ax.tick_params(axis="x", labelsize=25)
st.pyplot(fig)

# 5. Customer demographics
st.subheader("Customer Demographics")

# By Payment type
fig, ax = plt.subplots(figsize=(10, 4))
colors_ = ["#009600", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    data=by_payment_type_df,
    x="payment_type",
    y="customer_count",
    hue="payment_type",
    palette=colors_,
)
ax.set_title("by Payment Type", fontsize=15)
ax.set_ylabel("Customer Count", fontsize=10)
ax.set_xlabel(None)
ax.tick_params(axis="y", labelsize=10)
ax.tick_params(axis="x", labelsize=10)
st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    # By city
    fig, ax = plt.subplots(figsize=(10, 8.5))
    sns.barplot(
        data=bycity_df.head(),
        x="customer_count",
        y="customer_city",
        hue="customer_city",
        palette=colors,
    )
    ax.set_title("by City", fontsize=25)
    ax.set_ylabel(None)
    ax.set_xlabel("Customer Count", fontsize=20)
    ax.tick_params(axis="y", labelsize=25)
    ax.tick_params(axis="x", labelsize=20)
    st.pyplot(fig)

with col2:
    # By state
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.barplot(
        data=bystate_df.head(),
        x="customer_count",
        y="customer_state",
        hue="customer_state",
        palette=colors,
    )
    ax.set_title("by State", fontsize=25)
    ax.set_ylabel(None)
    ax.set_xlabel("Customer Count", fontsize=20)
    ax.tick_params(axis="y", labelsize=20)
    ax.tick_params(axis="x", labelsize=20)
    st.pyplot(fig)


# 6. Customer density map
st.subheader("Customer Density Map")
fig = create_customer_density_map(map_df)
st.plotly_chart(fig)

# Membuat copyright dinamis
current_year = datetime.now().year
st.caption(
    f"Copyright © {current_year} Brazilian E-commerce Dashboard. Made with :heart: by **binn.fnc**"
)
