import pandas as pd, matplotlib.pyplot as plt
from Libs.utils import FuzzyClean, GetStateNameByPincode
from Model.data import StateUtNames, UnionTerritories

# Load All The CSV
df1 = pd.read_csv("Dataset/aadhar_enrolment/api_data_aadhar_enrolment_0_500000.csv")
df2 = pd.read_csv("Dataset/aadhar_enrolment/api_data_aadhar_enrolment_500000_1000000.csv")
df3 = pd.read_csv("Dataset/aadhar_enrolment/api_data_aadhar_enrolment_1000000_1006029.csv")
df = pd.concat([df1, df2, df3], ignore_index=True)

# Cleaning
# Convert Object to DateTime
df['date'] = pd.to_datetime(df['date'],dayfirst=True)
# It keeps only rows where at least one person enrolled
df = df[(df['age_0_5'] > 0) | (df['age_5_17'] > 0) | (df['age_18_greater'] > 0)]
# Clean the State
df['state'] = df['state'].str.replace(r'\s+', ' ', regex=True).str.strip().str.title()
bad_states = df.loc[~df['state'].isin(StateUtNames), 'state'].unique()
fix_states = {s: FuzzyClean(s, StateUtNames) for s in bad_states}
df['state'] = df['state'].replace(fix_states)
bad_states = df.loc[~df['state'].isin(StateUtNames), ['state', 'pincode']]
fix_states = {
    s: GetStateNameByPincode(p)
    for s, p in zip(bad_states['state'], bad_states['pincode'])
}
df['state'] = df['state'].replace(fix_states)
# Remove Bad State Name
df = df[df['state'] != 'Unknown']
# Removing Union Territories due to less population
df = df[~df['state'].isin(UnionTerritories)]


# Insight A
df["total"] = (
    df["age_0_5"] + df["age_5_17"] + df["age_18_greater"]
)
state_totals = df.groupby("state")["total"].sum()
total_india = state_totals.sum()
state_percent = (state_totals / total_india) * 100
plt.figure(figsize=(12,6))
ax = state_percent.sort_values(ascending=False).plot(kind='bar')
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f%%')
plt.title("Percentage Share of Aadhaar Enrolments by State")
plt.xlabel("State")
plt.ylabel("Share of Enrolments (%)")
plt.tight_layout()
plt.show()

# North India is driving most of the new Aadhaar enrolments, mainly because states like Uttar Pradesh and Bihar have large populations.
# Southern states are adding fewer new users because most people already have Aadhaar, while the Northeast stays low due to small populations and harder-to-reach areas.
# This uneven growth can cause problems later — crowded enrolment centres in big states and slow access in remote places.
# To fix this, India needs more mobile enrolment teams, better digital systems in villages, and smarter data checks. This will help make Aadhaar easier to get for everyone, no matter where they live.


# Insight B
df['month_name'] = df['date'].dt.month_name()
month_order = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
]
monthly_summary = (
    df.groupby('month_name')['total']
    .sum()
    .reindex(month_order)
)
plt.figure(figsize=(12,6))
ax = monthly_summary.plot(kind='bar')
for container in ax.containers:
    ax.bar_label(container)
plt.title("Aadhaar Enrolment by Month")
plt.xlabel("Month")
plt.ylabel("Total Enrolments")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# The observed peaks in Aadhaar enrolments during September to November indicate periods of increased demand, 
# likely driven by government enrolment drives and administrative deadlines. 
# During these months, higher staffing levels and extended enrolment operations would be required to efficiently manage the workload. 
# In contrast, months showing zero enrolments, such as January, February, and August, 
# are the result of data unavailability or reporting gaps rather than a complete halt in enrolment activities or reduced staffing.