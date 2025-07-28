import os

API_KEYS = [
    os.getenv("MISTRAL_API_KEY_1", "P10U4w3ek6sSfbUcXZqB9oIpk7Pykn6G"),
    os.getenv("MISTRAL_API_KEY_2", "qiI6zL53ziYoQWmdUhlSkLorHbDDHKQM"),
]

MODEL = "mistral-large-latest"
INPUT_CSV = "../1_filtration/results/filtered_vacancies.csv.gz"
OUTPUT_TXT = "results/results.txt"
PROCESSED_IDS = "results/processed_ids.txt"
HARD_PATH = "results/hard.txt"
SOFT_PATH = "results/soft.txt"

BATCH_SIZE = 25
MAX_CONCURRENCY = 10
RETRIES = 3
RESTART_INTERVAL_SECONDS = 15 * 60
