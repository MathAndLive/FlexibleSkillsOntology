import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util

ETALON_PATH = "etalon.txt"
INPUT_FILE = r"..\5_clusterization\results\result.csv"
OUTPUT_FILE = "results/result.csv"

SIM_THRESHOLD = 0.8
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device=DEVICE)


def read_etalon_skills(file_path):
    skills = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            skill = line.strip()
            if skill:
                skills.append(skill)
    return skills


etalon_skills = read_etalon_skills(ETALON_PATH)
etalon_embeds = model.encode(etalon_skills,
                             convert_to_tensor=True,
                             normalize_embeddings=True)


def filter_skills(skill_str):
    """Замена на слово из эталона"""
    if pd.isna(skill_str) or not skill_str.strip():
        return ""

    skills = [s.strip() for s in skill_str.split(';') if s.strip()]
    if not skills:
        return ""

    skill_embeds = model.encode(skills,
                                convert_to_tensor=True,
                                normalize_embeddings=True)

    cos_scores = util.cos_sim(skill_embeds, etalon_embeds)

    filtered_skills = []
    for i, skill in enumerate(skills):
        max_score, best_match_idx = torch.max(cos_scores[i], dim=0)
        max_score = max_score.item()

        if max_score >= SIM_THRESHOLD:
            best_match = etalon_skills[best_match_idx]
            filtered_skills.append(best_match)

    return ';'.join(filtered_skills)


# def filter_skills(skill_str):
#     """Оставляем слова, похожие на эталон"""
#     if pd.isna(skill_str) or not skill_str.strip():
#         return ""

#     skills = [s.strip() for s in skill_str.split(';') if s.strip()]
#     if not skills:
#         return ""

#     skill_embeds = model.encode(skills,
#                                 convert_to_tensor=True,
#                                 normalize_embeddings=True)

#     cos_scores = util.cos_sim(skill_embeds, etalon_embeds)

#     max_scores, _ = torch.max(cos_scores, dim=1)

#     filtered_skills = [
#         skill
#         for skill, score in zip(skills, max_scores.cpu().numpy())
#         if score >= SIM_THRESHOLD
#     ]

#     return ';'.join(filtered_skills)


print("Начинаем фильтрацию soft skills")
df = pd.read_csv(INPUT_FILE, dtype={"_id": str})

if 'soft_skills' not in df.columns:
    raise ValueError("Колонка 'soft_skills' не найдена в CSV файле")

print(f"Пример навыков до обработки:")
print(df[['_id', 'soft_skills']].head(3))

df['soft_skills'] = df['soft_skills'].apply(filter_skills)

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"\nГотово! Отфильтрованные данные сохранены в {OUTPUT_FILE}")
print(f"Пример обработанных навыков:")
print(df[['_id', 'soft_skills']].head(3))
