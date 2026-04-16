import pdfplumber
import pandas as pd

def parse_pdf(file_path):
    all_rows = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()

            if table:
                headers = table[0]  # first row = column names
                
                for row in table[1:]:
                    all_rows.append(row)

    df = pd.DataFrame(all_rows, columns=headers)
    
    print(df.head())  # just to check
    return df