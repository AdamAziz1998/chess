import pandas as pd
print("running")
# Path to your CSS file
file_path = "assets/data/GM_games_dataset.csv"

pd.set_option("display.max_colwidth", None)

# Load in chunks of 1 million rows
chunk_iter = pd.read_csv(file_path, chunksize=1_000_000)
print("csv read")
for i, chunk in enumerate(chunk_iter):
    print(f"Chunk {i}, shape: {chunk.shape}")
    print(chunk["pgn"].head(3))  # preview first 3 rows
    # You can also process/save chunk here instead of keeping it all in memory
