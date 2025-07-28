import asyncio
import aiofiles

from config import *


class SkillStorage:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.processed_ids = self._load_set(PROCESSED_IDS)
        self.hard_skills = self._load_set(HARD_PATH)
        self.soft_skills = self._load_set(SOFT_PATH)

        for path in [PROCESSED_IDS, HARD_PATH, SOFT_PATH, OUTPUT_TXT]:
            dir = os.path.dirname(path)
            if dir and not os.path.exists(dir):
                os.makedirs(dir, exist_ok=True)

    @staticmethod
    def _load_set(path: str) -> set:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return set(line.strip().lower() for line in f if line.strip())
            except Exception as e:
                print(f"Error loading {path}: {e}")
        return set()

    async def add_skill(self, skill: str, skill_type: str):
        """Добавляет навык в соответствующее хранилище, если его там нет"""
        skill_lower = skill.lower()
        target_set = self.hard_skills if skill_type == "H" else self.soft_skills
        target_path = HARD_PATH if skill_type == "H" else SOFT_PATH

        async with self.lock:
            if skill_lower not in target_set:
                target_set.add(skill_lower)
                async with aiofiles.open(target_path, "a", encoding="utf-8") as f:
                    await f.write(f"{skill}\n")

    async def save_job_result(self, job_id: str, h_skills: list, s_skills: list):
        """Сохраняет результат обработки вакансии"""
        async with self.lock:
            if job_id not in self.processed_ids:
                self.processed_ids.add(job_id)
                async with aiofiles.open(PROCESSED_IDS, "a", encoding="utf-8") as f:
                    await f.write(f"{job_id}\n")

            async with aiofiles.open(OUTPUT_TXT, "a", encoding="utf-8") as f:
                line = f"{job_id} | {';'.join(h_skills)} | {';'.join(s_skills)}\n"
                await f.write(line)
