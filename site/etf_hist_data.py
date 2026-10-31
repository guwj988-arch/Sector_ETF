import pandas as pd

sheet_id = "1F-8T7Y8ndpcDgm0oQI3Xr-LrZhKqqAKgvzaovjagf7g"
gid = "738960490"

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

df = pd.read_csv(url)

#df["Date"] = pd.to_datetime(df["Date"])

df = df.set_index("Date")
df = df.drop(df.index[0])
df.to_csv(r"C:\Users\kguke\Documents\WGu\ETF Forecasting\etf_price.csv")

print(df.tail())