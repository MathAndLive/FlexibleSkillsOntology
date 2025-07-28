import asyncio
import random
import time
import pandas as pd
import json
from config import *
from mistral import call_mistral, ServiceTierCapacityExceeded
from storage import SkillStorage

sem = asyncio.Semaphore(MAX_CONCURRENCY)
storage = SkillStorage()


class AllTasksCompleted(Exception):
    pass


async def process_row(job_id: str, job_text: str):
    async with sem:
        if job_id in storage.processed_ids:
            return

        attempt = 1
        while attempt < RETRIES:
            try:
                print(f"[{job_id}] attempt #{attempt}")
                result = await call_mistral(job_text)

                if not result:
                    wait = 1.5 * attempt * random.random()
                    print(f"[{job_id}] no result, retry in {wait:.1f}s")
                    await asyncio.sleep(wait)
                    continue

                try:
                    parsed = json.loads(result)
                    if not isinstance(parsed, list):
                        raise ValueError("Response is not a list")

                    h_skills, s_skills = [], []
                    for item in parsed:
                        skill = item.get("s", "").strip()
                        typ = item.get("t", "").upper()
                        if not skill or typ not in {"H", "S"}:
                            continue

                        await storage.add_skill(skill, typ)
                        if typ == "H":
                            h_skills.append(skill)
                        else:
                            s_skills.append(skill)

                    await storage.save_job_result(job_id, h_skills, s_skills)
                    print(f"[{job_id}] H={len(h_skills)} S={len(s_skills)}")
                    return

                except (json.JSONDecodeError, ValueError) as e:
                    print(f"[{job_id}] JSON error: {e}")
                    await asyncio.sleep(1)
                    continue

            except ServiceTierCapacityExceeded as e:
                backoff = min(32, 2 ** (attempt * random.random()))
                print(f"[{job_id}] capacity exceeded, waiting {backoff:.1f}s")
                await asyncio.sleep(backoff)
                continue

        print(f"[{job_id}] failed after {RETRIES} retries")


async def main():
    df_iter = pd.read_csv(INPUT_CSV, dtype={"_id": str}, chunksize=BATCH_SIZE, encoding="utf-8-sig")

    all_done = True

    for chunk in df_iter:
        tasks = []
        for _, row in chunk.iterrows():
            jid = row["_id"]
            if jid in storage.processed_ids:
                continue
            tasks.append(asyncio.create_task(process_row(jid, row["description"])))

        if tasks:
            all_done = False
            await asyncio.gather(*tasks)

    if all_done:
        raise AllTasksCompleted()


async def run_with_restart():
    while True:
        print(f"Запуск main() в {time.strftime('%H:%M:%S')}")
        try:
            await asyncio.wait_for(main(), timeout=RESTART_INTERVAL_SECONDS)
        except AllTasksCompleted:
            print("Все задачи выполнены, перезапуск не требуется")
            break
        except asyncio.TimeoutError:
            print(f"{RESTART_INTERVAL_SECONDS // 60} минут прошло - перезапуск")
        except Exception as e:
            print(f"Ошибка в main: {e}")
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(run_with_restart())
    except KeyboardInterrupt:
        print("Скрипт остановлен вручную")
