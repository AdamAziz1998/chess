import csv
import argparse
import logging
import multiprocessing
import concurrent.futures
from typing import Set, Dict
from tqdm import tqdm
from database import Database
from worker import transform_game_batch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- CHUNK SETTINGS ---
# To run games 0 to 10M: START_INDEX = 0, STOP_AFTER = 10_000_000
# To run games 10M to 20M: START_INDEX = 10_000_000, STOP_AFTER = 20_000_000
START_INDEX = 0
STOP_AFTER = 5_000_000
# ----------------------

DB_BATCH_SIZE = 10000  # Increased for big data
WORKER_PROCESSES = multiprocessing.cpu_count() - 1 or 1


def sync_to_db(db: Database, all_fens: Set[str], all_moves: Dict):
    required_fens = all_fens.copy()
    for (fen_before, fen_after) in all_moves.keys():
        required_fens.add(fen_before)
        required_fens.add(fen_after)

    if not required_fens:
        return

    # Step 1: Resolve IDs
    # Note: We only check the DB for what isn't in Python's memory
    unknown_fens = [f for f in required_fens if f not in db.fen_cache]

    if unknown_fens:
        from psycopg2.extras import execute_values
        args_list = [(f,) for f in unknown_fens]

        # Optimized SQL for Chunking:
        # We still need the IDs back, but we want to avoid heavy locking
        query = """
                INSERT INTO Position (fen_position)
                VALUES %s ON CONFLICT (fen_position) DO \
                UPDATE SET fen_position = EXCLUDED.fen_position \
                    RETURNING fen_position, id \
                """
        chunk_size = 10000
        for i in range(0, len(args_list), chunk_size):
            chunk = args_list[i: i + chunk_size]
            execute_values(db.cur, query, chunk)
            for row in db.cur.fetchall():
                db.fen_cache[row['fen_position']] = row['id']

    # Step 2: Prepare Moves
    bulk_move_data = []
    for (fen_before, fen_after), stats in all_moves.items():
        b_id = db.fen_cache.get(fen_before)
        a_id = db.fen_cache.get(fen_after)
        if b_id is not None and a_id is not None:
            bulk_move_data.append((b_id, a_id, stats["san"], stats["w"], stats["b"], stats["d"]))

    # Step 3: Insert Moves
    if bulk_move_data:
        db.insert_moves_batch(bulk_move_data)
    db.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    args = parser.parse_args()

    print(f"🚀 Processing games {START_INDEX} to {STOP_AFTER}...")

    pending_fens = set()
    pending_moves = {}
    games_accumulated = 0
    current_line = 0

    with Database() as db:
        # !!! REMOVED db.clear_all_data() TO PRESERVE PROGRESS !!!
        db.create_tables()

        with concurrent.futures.ProcessPoolExecutor(max_workers=WORKER_PROCESSES) as executor:
            with open(args.csv, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header

                chunk_size = 2500
                batch_buffer = []
                futures = []

                pbar = tqdm(total=(STOP_AFTER - START_INDEX), desc="Chunk Progress")

                for row in reader:
                    # Skip until we reach our starting point
                    if current_line < START_INDEX:
                        current_line += 1
                        continue

                    if current_line >= STOP_AFTER:
                        break

                    current_line += 1
                    batch_buffer.append(row[-2])

                    if len(batch_buffer) >= chunk_size:
                        futures.append(executor.submit(transform_game_batch, list(batch_buffer)))
                        batch_buffer = []

                        if len(futures) >= WORKER_PROCESSES * 2:
                            done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
                            for fut in done:
                                futures.remove(fut)
                                fens, moves = fut.result()
                                pending_fens.update(fens)
                                for k, v in moves.items():
                                    if k not in pending_moves:
                                        pending_moves[k] = v.copy()
                                    else:
                                        pending_moves[k]["w"] += v["w"]
                                        pending_moves[k]["b"] += v["b"]
                                        pending_moves[k]["d"] += v["d"]

                                games_accumulated += chunk_size
                                pbar.update(chunk_size)

                                if games_accumulated >= DB_BATCH_SIZE:
                                    sync_to_db(db, pending_fens, pending_moves)
                                    pending_fens.clear()
                                    pending_moves.clear()
                                    games_accumulated = 0

                # Cleanup remaining...
                for fut in concurrent.futures.as_completed(futures):
                    fens, moves = fut.result()
                    pending_fens.update(fens)  # ... aggregation logic ...

                if pending_moves:
                    sync_to_db(db, pending_fens, pending_moves)

                pbar.close()
                print(f"✅ Chunk Complete. Next START_INDEX should be {current_line}")


if __name__ == "__main__":
    main()