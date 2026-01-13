import pandas as pd, matplotlib.pyplot as plt
from Libs.utils import GetBadDistricts, FuzzyClean

# Load All The CSV
df1 = pd.read_csv("Dataset/aadhar_demographic/api_data_aadhar_demographic_0_500000.csv")
df2 = pd.read_csv("Dataset/aadhar_demographic/api_data_aadhar_demographic_500000_1000000.csv")
df3 = pd.read_csv("Dataset/aadhar_demographic/api_data_aadhar_demographic_1000000_1500000.csv")
df4 = pd.read_csv("Dataset/aadhar_demographic/api_data_aadhar_demographic_1500000_2000000.csv")
df5 = pd.read_csv("Dataset/aadhar_demographic/api_data_aadhar_demographic_2000000_2071700.csv")
df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

# Cleaning
# Convert Object to DateTime
df['date'] = pd.to_datetime(df['date'],dayfirst=True)
# Clean the District
df['district'] = df['district'].str.replace(r'\s+', ' ', regex=True).str.strip().str.title()
bad_districts = GetBadDistricts(districts=df['district'])
lgd = pd.read_csv("Dataset/local-gov-directory.csv")
lgd_districts = lgd["District Name (In English)"].str.replace(r'\s+', ' ', regex=True).str.strip().str.title()
fix_districts = {s: FuzzyClean(s, lgd_districts) for s in bad_districts}
df['district'] = df['district'].replace(fix_districts)

# SPIKE DETECTION
df["total"] = df["demo_age_5_17"] + df["demo_age_17_"]
daily_updates = (
    df.groupby('date')['total']
    .sum()
    .sort_index()
)
mean_updates = daily_updates.mean()
std_updates = daily_updates.std()
threshold = mean_updates + 2 * std_updates
spike_dates = daily_updates[daily_updates > threshold]

# PLOT 
plt.figure(figsize=(12, 6))
plt.plot(daily_updates.index, daily_updates.values, marker='o', label="Daily Updates")
# Highlight spikes
plt.scatter(spike_dates.index, spike_dates.values, zorder=5)
plt.title("Daily Aadhaar Update Volume")
plt.xlabel("Date")
plt.ylabel("Total Updates")
plt.grid(True)

# Top-10 districts
if not spike_dates.empty:
    spike_date = spike_dates.index[0]

    district_breakdown = (
        df[df['date'] == spike_date]
        .groupby('district')['total']
        .sum()
        .sort_values(ascending=False)
    )

    top10 = district_breakdown.head(10)

    heading = f"Top 10 Districts\n({spike_date.date()})\n"
    body = "\n".join([f"{d}: {v:,}" for d, v in top10.items()])
    text = heading + body

    plt.gca().text(
        0.98, 0.98,
        text,
        transform=plt.gca().transAxes,
        ha='right',
        va='top',
        fontsize=9,
        color='black',
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor="white",
            edgecolor="black",
            alpha=1.0
        ),
        fontweight='bold'
    )


plt.tight_layout()
plt.show()


# The data shows a very large increase in Aadhaar updates on 1 March 2025. This increase happened only for one day and then quickly returned to normal levels. 
# This means the spike was likely caused by a planned government activity or deadline, not by regular daily demand. 
# Most of the updates came from a few big and well-equipped districts, while many other districts contributed much less. 
# Overall, the system handled the sudden workload well, but the results show that Aadhaar update capacity is uneven across districts.