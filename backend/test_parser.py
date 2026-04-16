from utils.parser import parse_pdf

df = parse_pdf("data/sample.pdf")
print("\nFINAL DATAFRAME:\n")
print(df)