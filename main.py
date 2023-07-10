from collections import defaultdict
from datetime import datetime
import os
import requests
from glob import glob
import click
import time


rate_limit = 5
sleep_time = 1 / rate_limit


def get_last_timestamp(save_dir):
    save_paths = list(glob(os.path.join(save_dir, "*.csv")))
    save_paths.sort(key=lambda date: datetime.strptime(os.path.basename(date).replace(".csv", ""), "%Y-%m-%d"))
    if len(save_paths) > 0:
        with open(save_paths[-1], "r") as file:
            lines = file.readlines()
            headers = lines[0].strip().split(",")
            last_values = lines[-1].strip().split(",")
            last_record = {header: value for header, value in zip(headers, last_values)}
            last_timestamp = int(last_record["timestamp"])
            return last_timestamp


def download(slug, from_timestamp, until_timestamp, size, data_dir):
    save_dir = f"{data_dir}/{slug}"
    last_timestamp = get_last_timestamp(save_dir)
    if last_timestamp is not None:
        from_timestamp = last_timestamp + 1
        print(f"Resuming download from timestamp {from_timestamp}...")
    os.makedirs(save_dir, exist_ok=True)
    size = max(5001, size)
    size = min(100_000, size)
    url = f"https://api.syve.ai/v1/filter/{slug}"
    start_time = time.time()
    total = 0

    while True:
        if from_timestamp is None:
            break
        params = {
            "filterby": "timestamp",
            "gte": from_timestamp,
            "lte": until_timestamp,
            "sort": "asc",
            "size": size,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
        }
        # headers = {}
        res = requests.get(url, headers=headers, params=params)
        records = res.json()
        if len(records) == 0:
            break
        # Update from_timestamp for next iteration:
        if len(records) == size:
            from_timestamp = records[-1]["timestamp"]
        else:
            from_timestamp = None

        records_map = defaultdict(lambda: [])
        for record in records:
            timestamp = record["timestamp"]
            # Ensure no duplicates:
            if from_timestamp is not None and timestamp == from_timestamp:
                continue
            save_path = f"{save_dir}/{datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')}.csv"
            records_map[save_path].append(record)

        for save_path, records in records_map.items():
            if not os.path.exists(save_path):
                with open(save_path, "w+") as f:
                    f.write(",".join([str(x) for x in records[0].keys()]) + "\n")
            with open(save_path, "a+") as f:
                for record in records:
                    f.write(",".join([str(x) for x in record.values()]) + "\n")
            total += len(records)
            print(
                f"[Took-{time.time() - start_time:.2f}] [Block-{records[-1]['block_number']}] [Total-{total:,}] Saved {len(records)} records to: ",
                save_path,
            )
        # time.sleep(sleep_time)


@click.command()
@click.argument(
    "slug",
    type=click.Choice(["blocks", "erc20", "prices_usd"]),
)
@click.option(
    "--from-timestamp",
    type=int,
    default=int(datetime.now().timestamp()) - 30 * 86400,
    help="The time to start downloding from in UNIX timestamp seconds. Defaults 30 days ago.",
)
@click.option(
    "--until-timestamp",
    type=int,
    default=int(datetime.now().timestamp()),
    help="The time to stop downloading at in UNIX timestamp seconds. Defaults to now.",
)
@click.option(
    "--size",
    type=int,
    default=10000,
    help="The number of records to download per request. Defaults to 10,000.",
)
@click.option(
    "--data-dir",
    type=str,
    default=f"{os.getcwd()}/data",
    help="The directory where data is stored. Defaults to ./data.",
)
def main(slug, from_timestamp, until_timestamp, size, data_dir):
    download(slug, from_timestamp, until_timestamp, size, data_dir)


if __name__ == "__main__":
    main()
