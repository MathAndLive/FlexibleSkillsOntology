import pandas as pd

results_paths = [r"..\3_merge_with_profession\results\merged_skills.csv",
                 r"..\3_merge_with_profession\results\merged_skills(1).csv"]
soft_paths = [r"..\2_getSkills\results\soft.txt",
              r"..\2_getSkills\results\soft(1).txt"]
hard_paths = [r"..\2_getSkills\results\hard.txt",
              r"..\2_getSkills\results\hard(1).txt"]

result_out = "results/merged_skills_final.csv"
soft_out = "results/soft_skills_final.txt"
hard_out = "results/hard_skills_final.txt"


def merge_files(file_paths, output_path):
    merged_data = []
    for path in file_paths:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if data:
                merged_data.append(data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(merged_data))
        print(f"Сведено в {output_path}")


def merge_csv_files(file_paths, output_path):
    merged_df = pd.DataFrame()
    for path in file_paths:
        df = pd.read_csv(path, dtype={"_id": str}, encoding="utf-8-sig")
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    merged_df.drop_duplicates(subset="_id", inplace=True)
    merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Сведено {len(merged_df)} строк в {output_path}")


merge_csv_files(results_paths, result_out)
merge_files(soft_paths, soft_out)
merge_files(hard_paths, hard_out)
