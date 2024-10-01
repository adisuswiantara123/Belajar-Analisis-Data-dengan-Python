import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style for Seaborn
sns.set(style='dark')

# Read the cleaned CSV files
day_df = pd.read_csv("dashboard/cleaned_day_data.csv")
hour_df = pd.read_csv("dashboard/cleaned_hour_data.csv")

# Convert the 'date' column to datetime
day_df['date'] = pd.to_datetime(day_df['date'])
hour_df['date'] = pd.to_datetime(hour_df['date'])

# Sidebar for filtering
with st.sidebar:
    st.image("https://storage.googleapis.com/gweb-uniblog-publish-prod/original_images/image1_hH9B4gs.jpg")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=day_df['date'].min(),
        max_value=day_df['date'].max(),
        value=[day_df['date'].min(), day_df['date'].max()]
    )

# Filter datasets based on the selected date range
main_day_df = day_df[(day_df['date'] >= pd.Timestamp(start_date)) & 
                      (day_df['date'] <= pd.Timestamp(end_date))]
main_hour_df = hour_df[(hour_df['date'] >= pd.Timestamp(start_date)) & 
                        (hour_df['date'] <= pd.Timestamp(end_date))]

# 1. Weather Impact on Total Users by Season
st.header("Pengaruh Cuaca terhadap Jumlah Pengguna Sepeda di Berbagai Musim")

# Convert 'weather_condition' to string if not already
main_day_df['weather_condition'] = main_day_df['weather_condition'].astype(str)

# Aggregate data based on season and weather condition
weather_season_users = main_day_df.groupby(['season', 'weather_condition']).agg({
    'total_users': 'sum'
}).reset_index()

# Mapping weather conditions to clearer descriptions
weather_labels = {'1': 'Cerah', '2': 'Berkabut', '3': 'Hujan'}
weather_season_users['weather_condition'] = weather_season_users['weather_condition'].map(weather_labels)

# Create bar plot
fig, ax = plt.subplots(figsize=(12, 8))
sns.barplot(x='season', y='total_users', hue='weather_condition', data=weather_season_users, palette='muted', ax=ax)
ax.set_ylabel('Jumlah Total Pengguna Sepeda', fontsize=14)
ax.set_xlabel('Musim', fontsize=14)

# Season labels
season_labels = {0: 'Musim Dingin', 1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur'}
ax.set_xticklabels([season_labels.get(int(x), x) for x in ax.get_xticks()], fontsize=12)
ax.legend(title='Kondisi Cuaca', title_fontsize='13', fontsize='12')
ax.set_title('Pengaruh Cuaca terhadap Jumlah Total Pengguna Sepeda', fontsize=16)
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# 2. Correlation Analysis
st.header("Analisis Korelasi antara Suhu, Kelembaban, Kecepatan Angin, dan Jumlah Penyewaan Sepeda")

# Prepare data for correlation
data_for_correlation = main_day_df[['temp', 'humidity', 'windspeed', 'total_users']]
correlation_data = data_for_correlation.corr()

# Create heatmap
plt.figure(figsize=(12, 8))
heatmap = sns.heatmap(correlation_data, 
                       annot=True, 
                       cmap='coolwarm', 
                       fmt='.2f', 
                       square=True, 
                       cbar_kws={"shrink": .8})
heatmap.set_xticklabels(['Suhu', 'Kelembaban', 'Kecepatan Angin', 'Total Pengguna'], fontsize=12)
heatmap.set_yticklabels(['Suhu', 'Kelembaban', 'Kecepatan Angin', 'Total Pengguna'], fontsize=12)
plt.title('Heatmap Korelasi antara Suhu, Kelembaban, Kecepatan Angin, dan Jumlah Penyewaan Sepeda', fontsize=16)
st.pyplot(plt)

# Scatter plots
scatter_features = ['temp', 'humidity', 'windspeed']
for feature in scatter_features:
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=feature, y='total_users', data=main_day_df, alpha=0.6)
    plt.title(f'Hubungan antara {feature.capitalize()} dan Jumlah Penyewaan Sepeda', fontsize=16)
    plt.xlabel(feature.capitalize(), fontsize=14)
    plt.ylabel('Jumlah Penyewaan Sepeda', fontsize=14)
    st.pyplot(plt)

# 3. Usage Patterns
st.header("Pola Penggunaan Sepeda Selama Hari Kerja vs Hari Libur")

# Merge working day information
day_df_renamed = main_day_df.rename(columns={'workingday': 'day_workingday'})
hour_df = main_hour_df.merge(day_df_renamed[['date', 'day_workingday']], on='date', how='left')
hour_df['day_type'] = hour_df['day_workingday'].apply(lambda x: 'Hari Kerja' if x == 1 else 'Hari Libur')

# Group data by hour and day type
hourly_usage = hour_df.groupby(['hr', 'day_type']).agg({'total_users': 'mean'}).reset_index()

# Create line plot
plt.figure(figsize=(12, 6))
sns.lineplot(x='hr', y='total_users', hue='day_type', data=hourly_usage, marker='o')
plt.title('Pola Penggunaan Sepeda Selama Hari Kerja vs Hari Libur Berdasarkan Waktu', fontsize=16)
plt.xlabel('Jam', fontsize=14)
plt.ylabel('Rata-rata Jumlah Pengguna Sepeda', fontsize=14)
plt.xticks(ticks=range(0, 24), labels=[f'{hour}:00' for hour in range(0, 24)], rotation=45)
plt.legend(title='Jenis Hari', title_fontsize='13', fontsize='12')
plt.grid(True)
plt.tight_layout()
st.pyplot(plt)
