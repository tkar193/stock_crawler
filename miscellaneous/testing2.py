import csv
import pandas as pd


ignore_ticker = ["ACAC", "ACTC", "CCZ", "CATM", "CMCTP", "CLNY", "CRSA", "DSE", "EFF", "FCRZ", "FAII", "FSKR", "GFNSZ", "GFNCP", "HCAPZ", "HEC", "HWCPL", "HWCC", "MYT", "OBLN", "PBY", "SSPK", "STAY", "SVMK", "SYX", "TCBIP", "TCBIL", "VGAC"]

def check_symbol_info(ticker, company_name):

    if "^" in ticker or "/" in ticker:
        return False

    ignore_ticker_set = set(ignore_ticker)

    if ticker in ignore_ticker_set:
        return False

    if "Class B" in company_name or "ETF" in company_name or "warrant" in company_name.lower() or "unit" in company_name.lower():
        return False

    last_word = company_name.split(" ")[-1]

    if "Unit" in last_word or "Warrant" in last_word:
        return False


    return True




filename = "data/nasdaq_screener_1623726528918.csv"
# filename = "data/entire_ticker_list.csv"
fileout = "data/entire_ticker_list.csv"
# fileout = "data/entire_ticker_list_test.csv"

df = pd.read_csv(filename)

new_df = pd.DataFrame(columns = df.columns)

j = 0

for i in range(len(df)):
    row = df.iloc[i,:]
    print(i)
    ticker = row["Symbol"]
    company_name = row["Name"]
    if check_symbol_info(ticker, company_name):
    
        print(ticker)
        

        new_df = new_df.append(row, ignore_index = True)

print(new_df)

new_df.to_csv(fileout)
