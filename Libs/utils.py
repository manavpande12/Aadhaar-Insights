import pandas as pd
from thefuzz import process

df = pd.read_csv("Dataset/india-post-pincode.csv")
df['statename'] = df['statename'].str.strip().str.title()
df['pincode'] = df['pincode'].astype(str)
pin_to_state = df.set_index('pincode')['statename'].to_dict()


def FuzzyClean(raw,data):
  match, score = process.extractOne(raw, data)
  return match if score >= 85 else raw

def GetStateNameByPincode(pincode):
    pin = str(pincode)
    if pin in pin_to_state:
        return pin_to_state[pin]
    else:
        return "Unknown"
