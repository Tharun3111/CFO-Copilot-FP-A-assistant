import pandas as pd
from pathlib import Path

# Read Excel
excel_file = 'data.xlsx'
output_dir = Path('fixtures')

# Create output directory if it doesn't exist
output_dir.mkdir(exist_ok=True)

# Convert each sheet
sheets = ['actuals', 'budget', 'cash', 'fx']

for sheet_name in sheets:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    output_path = output_dir / f'{sheet_name}.csv'
    df.to_csv(output_path, index=False)
    print(f"✅ Created {output_path}")

print("\n🎉 All CSV files created successfully!")