import pandas as pd

results = []

with open(r"..\2_getSkills\results\results.txt", "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line or "|" not in line:
            continue

        parts = line.split("|")
        if len(parts) != 3:
            continue

        _id = parts[0].strip()
        hard_skills = parts[1].strip()
        soft_skills = parts[2].strip()

        results.append({
            "_id": _id,
            "hard_skills": hard_skills,
            "soft_skills": soft_skills
        })

skills_df = pd.DataFrame(results)

vacancies_df = pd.read_csv(r"..\1_filtration\results\filtered_vacancies.csv.gz", dtype={"_id": str},
                           encoding="utf-8-sig")

vacancies_df["_id"] = vacancies_df["_id"].astype(str)

merged_df = pd.merge(vacancies_df[["_id", "best_profession"]], skills_df, on="_id", how="inner")

merged_df.to_csv(r"results/merged_skills.csv", index=False, encoding="utf-8-sig")

print(f"Сведено {len(merged_df)} строк")
