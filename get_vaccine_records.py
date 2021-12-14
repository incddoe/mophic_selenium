# python get_vaccine_records.py -input_file -cid_column -output_file

from app import get_vaccine_records, columns
from sys import argv
import pandas as pd


if __name__ == "__main__":
    from configparser import ConfigParser

    conf = ConfigParser()
    conf.read("config.ini", encoding="utf8")
    logins = conf._sections['credentials']

    filename = argv[1]
    filetype = filename.split(".")[-1]
    if filetype in ["xlsx", "xls"]:
        cids = pd.read_excel(filename, dtype={argv[2]: "str"})[argv[2]]
    elif filetype == "csv":
        cids = pd.read_csv(filename, dtype={argv[2]: "str"})[argv[2]]
    cid = cids.iloc[0]
    print(cid)
    status, vaccine_records = get_vaccine_records(cid, logins)
    print(status, vaccine_records)


    # select only valid rows (for successful query)
    if status == 1:

        # having person records but no vaccine records exist
        if (vaccine_records.shape == (1,22)) and (vaccine_records.notnull().sum(axis=1).sum() == 1):
            vaccine_records = pd.DataFrame([['ไม่มีประวัติได้รับวัคซีน' for col in columns]], columns=columns)
            vaccine_records['cid'] = cid
        else:
            valid_rows = (vaccine_records.index + 1).astype('str') == vaccine_records['ลำดับ']
            vaccine_records = vaccine_records[valid_rows]

    # create blank dataframe (for unsuccessful query)
    elif status == 0:
        vaccine_records = pd.DataFrame([[None for col in columns]], columns=columns)
        vaccine_records['cid'] = cid

    print(status, vaccine_records)

    for cid in cids.iloc[1:]:
        print(cid)
        status, vaccine_record = get_vaccine_records(cid, logins)
        print(status, vaccine_record)


        # select only valid rows (for successful query)
        if status == 1:

            # having person records but no vaccine records exist
            if (vaccine_record.shape == (1,22)) and (vaccine_record.notnull().sum(axis=1).sum() == 1):
                vaccine_record = pd.DataFrame([['ไม่มีประวัติได้รับวัคซีน' for col in columns]], columns=columns)
                vaccine_record['cid'] = cid
            else:
                valid_rows = (vaccine_record.index + 1).astype('str') == vaccine_record['ลำดับ']
                vaccine_record = vaccine_record[valid_rows]

    # create blank dataframe (for unsuccessful query)
        elif status == 0:
            vaccine_record = pd.DataFrame([[None for col in columns]], columns=columns)
            vaccine_record['cid'] = cid

        print(status, vaccine_record)

        vaccine_records = pd.concat([vaccine_records, vaccine_record])

        vaccine_records.to_csv(argv[3], index=False)
