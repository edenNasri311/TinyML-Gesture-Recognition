import pandas as pd

# קריאת קובץ ה-CSV
df = pd.read_csv('right_labeled/labeled_data_2024-03-13_11-32-10.csv')

# מציאת הערכים המינימליים והמקסימליים עבור כל עמודה בנפרד
min_values = df.min()
max_values = df.max()

print("Minimum values for each column:")
print(min_values)
print("\nMaximum values for each column:")
print(max_values)
