import pandas as pd

# LOAD ALL CSV FILES
df1 = pd.read_csv("Dataset/aadhar_biometric/api_data_aadhar_biometric_0_500000.csv")
df2 = pd.read_csv("Dataset/aadhar_biometric/api_data_aadhar_biometric_500000_1000000.csv")
df3 = pd.read_csv("Dataset/aadhar_biometric/api_data_aadhar_biometric_1000000_1500000.csv")
df4 = pd.read_csv("Dataset/aadhar_biometric/api_data_aadhar_biometric_1500000_1861108.csv")
df = pd.concat([df1, df2, df3, df4], ignore_index=True)

# CLEANING
df['date'] = pd.to_datetime(df['date'], dayfirst=True)
# Sort only by pincode + date
df = df.sort_values(['pincode', 'date'])

# PINCODE-LEVEL DUPLICATE LOAD SHADOW DETECTION
dup_check = (
    df.groupby(
        ['pincode', 'bio_age_5_17', 'bio_age_17_']
    )
    .agg(date_count=('date', 'nunique'))
    .reset_index()
)
# Same biometric values repeated across multiple dates
duplicate_load_shadow = dup_check[dup_check['date_count'] > 1].copy()
# Severity Added
duplicate_load_shadow['severity'] = duplicate_load_shadow['date_count'].apply(
    lambda x: 'High' if x >= 3 else 'Medium'
)
# Proof So Merged
shadow_details = df.merge(
    duplicate_load_shadow[
        ['pincode', 'bio_age_5_17', 'bio_age_17_']
    ],
    on=['pincode', 'bio_age_5_17', 'bio_age_17_'],
    how='inner'
).sort_values(['pincode', 'bio_age_5_17', 'bio_age_17_', 'date'])
# Metrics
shadow_rate = (
    duplicate_load_shadow
    .groupby('severity')
    .size()
    .reset_index(name='pincode_count')
)

# OUTPUT
print("\nDUPLICATE LOAD SHADOW ANALYSIS (PINCODE LEVEL)")
print("=====================================================================================")
print(f"Total records analysed        : {len(df)}")
print(f"Total unique pincodes         : {df['pincode'].nunique()}")
# The same pincode reports exactly the same biometric update values
print(f"Pincodes with shadow anomaly  : {duplicate_load_shadow['pincode'].nunique()}")
# Total number of repeated-value patterns
print(f"Total shadow instances        : {len(duplicate_load_shadow)}")
shadow_percentage = (
    duplicate_load_shadow['pincode'].nunique()
    / df['pincode'].nunique()
) * 100
print(f"Shadow penetration rate       : {shadow_percentage:.2f}%")

print("\nSEVERITY BREAKDOWN")
print("=====================================================================================")
print(shadow_rate.to_string(index=False))

print("\nPIN CODES WITH MOST REPEATED DATA (HIGH SEVERITY)")
print("=====================================================================================")
print(
    duplicate_load_shadow
    .query("severity == 'High'")
    .sort_values('date_count', ascending=False)
    .head(10).to_string(index=False)
)

if not duplicate_load_shadow.empty:
    sample = duplicate_load_shadow.iloc[0]

    print("\nREPEATED BIOMETRIC VALUES ACROSS DATES (PROOF)")
    print("=====================================================================================")
    print(
        shadow_details[
            (shadow_details['pincode'] == sample['pincode']) &
            (shadow_details['bio_age_5_17'] == sample['bio_age_5_17']) &
            (shadow_details['bio_age_17_'] == sample['bio_age_17_'])
        ] .sort_values('date') [['date', 'pincode', 'bio_age_5_17', 'bio_age_17_']].to_string(index=False)
    )

print("\nSUMMARY)")
print("=====================================================================================")
print(
    "This analysis found a hidden issue in the Aadhaar biometric update data.\n"
    "For many pincodes, the same biometric values are repeated on multiple different dates,\n"
    "which should not happen in real-life updates. Biometric updates are event-based, so the\n"
    "numbers should change over time. This repeating pattern strongly suggests duplicate data\n"
    "loading or replay during data processing.\n"
    "Identifying these repeated patterns helps detect data quality problems early and makes\n"
    "the system more reliable and accurate.",
    
)
