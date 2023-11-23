import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='darkgrid')

def create_daily_df(df):
  daily_df = df.resample(rule='D', on='order_purchase_timestamp_x').agg({
      "product_id_x": "nunique",
      "total_price": "sum"
  })
  daily_df = daily_df.reset_index()
  daily_df.rename(columns={
      "product_id_x": "product_count",
      "total_price": "revenue"
  }, inplace=True)

  return daily_df

def create_bycity_df(df):
  bycity_df = df.groupby(by="customer_city").customer_id_x.nunique().reset_index()
  bycity_df.rename(columns={
      "customer_id_x": "customer_count"
  }, inplace=True)

  return bycity_df

def create_bystate_df(df):
  bystate_df = df.groupby(by="customer_state").customer_id_x.nunique().reset_index()
  bystate_df.rename(columns={
      "customer_id_x": "customer_count"
  }, inplace=True)

  return bystate_df

def create_items_df(df):
  sum_items_df = df.groupby("product_category_name").product_weight_g.sum().sort_values(ascending=False).reset_index()
  return sum_items_df

def create_rfm_df(df):
  rfm_df = df.groupby(by="customer_id_x", as_index=False).agg({
      "order_purchase_timestamp_x": "max",
       "order_id": "nunique",
       "total_price": "sum"
  })
  rfm_df.columns = ["customer_id_x", "max_order_timestamp", "frequency", "monetary"]

  rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
  recent_date = df["order_purchase_timestamp_x"].dt.date.max()
  rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
  rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

  return rfm_df

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_purchase_timestamp_x", "order_delivered_customer_date_x"]
all_df.sort_values(by="order_purchase_timestamp_x", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])

#Membuat komponen filter

min_date = all_df["order_purchase_timestamp_x"].min()
max_date = all_df["order_purchase_timestamp_x"].max()

st.set_page_config(
  page_title="Try Dashboard",
  page_icon="📊",
  layout="wide", 
  initial_sidebar_state="expanded"
)

with st.sidebar:
  # Menambahkan logo
  st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
  #st.link_button("Go to Website", "https://www.dicoding.com/")
  
  # Mengambil start_date & end_date dari date_input
  start_date = pd.Timestamp(st.sidebar.date_input("Start date", all_df["order_purchase_timestamp_x"].min().date()))
  end_date = pd.Timestamp(st.sidebar.date_input("End date", all_df["order_purchase_timestamp_x"].max().date()))
  
main_df = all_df[(all_df["order_purchase_timestamp_x"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp_x"] <= str(end_date))]

#Memanggil semua function yang telah dibuat

daily_df = create_daily_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
sum_items_df = create_items_df(main_df)
rfm_df = create_rfm_df(main_df)

#Melengkapi dashboard dengan visualisasi data

st.snow()
st.header('Dicoding Collection Dashboard :stars:', divider='gray')

st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
  total_orders = daily_df.product_count.sum()
  st.metric("Total Orders", value=total_orders)

with col2:
  total_revenue = format_currency(daily_df.revenue.sum(), "AUD ", locale='es_CO')
  st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(
    daily_df["order_purchase_timestamp_x"],
    daily_df["product_count"],
    marker='o',
    linewidth=2,
    color="#4169E1"
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Customer Demographics")

col1, col2 = st.columns(2)

with col1:
  fig, ax = plt.subplots(figsize=(15,10))
  colors = ["#000080", "#6495ED", "#6495ED", "#6495ED", "#6495ED"]

  sns.barplot(
      x="customer_count",
      y="customer_city",
      data=bycity_df.sort_values(by="customer_count", ascending=False).head(5),
      palette=colors,
      ax=ax
  )

  ax.set_title("City", loc="center", fontsize=35)
  ax.set_ylabel(None)
  ax.set_xlabel(None)
  ax.tick_params(axis='x', labelsize=35)
  ax.tick_params(axis='y', labelsize=30)
  st.pyplot(fig)

with col2:

  fig, ax = plt.subplots(figsize=(18,10))
  colors = ["#000080", "#6495ED", "#6495ED", "#6495ED", "#6495ED"]

  sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False).head(5),
    palette=colors,
    ax=ax
  )

  ax.set_title("State", loc="center", fontsize=35)
  ax.set_ylabel(None)
  ax.set_xlabel(None)
  ax.tick_params(axis='x', labelsize=35)
  ax.tick_params(axis='y', labelsize=30)
  st.pyplot(fig)

st.subheader("Best Weight and Light Products")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10,5))

colors = ["#FFA500", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"]

sns.barplot(x="product_weight_g", y="product_category_name", data=sum_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Weight Products", loc="center", fontsize=15)
ax[0].tick_params(axis='y', labelsize=15)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(x="product_weight_g", y="product_category_name", data=sum_items_df.sort_values(by="product_weight_g", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Light Products", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=15)
ax[1].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
  avg_recency = round(rfm_df.recency.mean(), 1)
  st.metric("Average Recency (days)", value=avg_recency)

with col2:
  avg_frequency = round(rfm_df.frequency.mean(), 2)
  st.metric("Average Frequency", value=avg_frequency)

with col3:
  avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD ", locale='es_CO')
  st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30,15))
colors = ["#000080", "#6495ED", "#6495ED", "#6495ED", "#6495ED"]

sns.barplot(y="recency", x="customer_id_x", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=35)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id_x", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=35)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id_x", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=35)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
st.pyplot(fig)

st.caption("Copyright(c) Dicoding 2023")
