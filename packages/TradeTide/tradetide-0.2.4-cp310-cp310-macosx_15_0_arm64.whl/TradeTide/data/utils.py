import os
import pandas as pd


import os
import pandas as pd


def process_csv_with_spread(input_file, output_file):
    """
    Process a CSV file with metadata and a 'spread' column.
    Computes ask and bid prices based on the original prices and the spread.
    Writes the processed data to a new CSV file, preserving metadata.

    Paths are resolved relative to the script file location.

    Parameters:
    - input_file: str, path to the input CSV file relative to this script
    - output_file: str, path to the output CSV file relative to this script
    """
    # Determine the directory of the current script file
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Resolve paths relative to the script file
    input_path = os.path.join(base_dir, input_file)
    output_path = os.path.join(base_dir, output_file)

    # Read and preserve metadata lines and count them
    metadata = []
    with open(input_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                metadata.append(line.rstrip())
            else:
                # Stop at the first non-metadata line
                break
    metadata_count = len(metadata)

    # Load the CSV data, skipping metadata lines so header is correctly read
    df = pd.read_csv(
        input_path,
        skiprows=metadata_count,
        parse_dates=['date']
    )

    # Compute ask (original + spread) and bid (original) columns
    for col in ['open', 'high', 'low', 'close']:
        df[f'ask_{col}'] = df[col] + df['spread']
        df[f'bid_{col}'] = df[col]

    # Reorder and select the desired columns
    df_out = df[[
        'date',
        'ask_open', 'ask_high', 'ask_low', 'ask_close',
        'bid_open', 'bid_high', 'bid_low', 'bid_close'
    ]]

    # Write out the new CSV, including metadata
    with open(output_path, 'w') as f:
        for line in metadata:
            f.write(f"{line}\n")
        df_out.to_csv(f, index=False)

    print(f"Processed {input_path} → {output_path}")


pair = "jpy_usd"

process_csv_with_spread(
    input_file=f'{pair}/2023/data.csv',
    output_file=f'{pair}_2023.csv',
)