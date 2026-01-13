import pandas as pd
from thefuzz import process

_original_extractOne = process.extractOne

def extractOne_2tuple(*args, **kwargs):
    result = _original_extractOne(*args, **kwargs)
    return result[0], result[1] 

process.extractOne = extractOne_2tuple

def FuzzyClean(raw,data):
  match, score = process.extractOne(raw, data)
  return match if score >= 85 else raw

df = pd.read_csv("Dataset/india-post-pincode.csv")
df['statename'] = df['statename'].str.strip().str.title()
df['pincode'] = df['pincode'].astype(str)
pin_to_state = df.set_index('pincode')['statename'].to_dict()
def GetStateNameByPincode(pincode):
    pin = str(pincode)
    if pin in pin_to_state:
        return pin_to_state[pin]
    else:
        return "Unknown"


lgd = pd.read_csv("Dataset/local-gov-directory.csv")
def GetBadDistricts(districts):
    df_districts = districts.str.lower()
    lgd_districts = lgd["District Name (In English)"].str.replace(r'\s+', ' ', regex=True).str.strip().str.lower()
    bad_districts = sorted(set(df_districts) - set(lgd_districts))
    return [d.title() for d in bad_districts]
