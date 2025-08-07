import pandas as pd
import numpy as np
import pickle
from scipy.sparse import dok_matrix, save_npz
import os

def process_user_data(file_path, output_dir, chunk_size=50000):
    """Process user's profession-skills data file"""
    os.makedirs(output_dir, exist_ok=True)

    # 1. First pass: collect unique values
    unique_professions = set()
    unique_skills = set()

    print("🔍 First pass: collecting unique professions and skills...")
    reader = pd.read_csv(file_path, sep='|', header=None,
                         names=['profession', 'hard_skills', 'soft_skills'],
                         chunksize=chunk_size, low_memory=False)

    for chunk in reader:
        # Collect unique professions with normalization
        professions = chunk['profession'].dropna().str.strip().unique()
        unique_professions.update(professions)

        # Process hard skills with normalization
        if 'hard_skills' in chunk:
            hard_skills = chunk['hard_skills'].dropna()
            hard_skills = hard_skills.str.split(';').explode()
            hard_skills = hard_skills.str.strip()  # Normalization
            hard_skills = hard_skills[hard_skills != '']
            unique_skills.update(hard_skills)

        # Process soft skills with normalization and prefix
        if 'soft_skills' in chunk:
            soft_skills = chunk['soft_skills'].dropna()
            soft_skills = soft_skills.str.split(';').explode()
            soft_skills = soft_skills.str.strip()  # Normalization
            soft_skills = soft_skills[soft_skills != '']
            unique_skills.update("SOFT_" + soft_skills)

    # 2. Create index dictionaries
    profession_to_idx = {prof: idx for idx, prof in enumerate(sorted(unique_professions))}
    skill_to_idx = {skill: idx for idx, skill in enumerate(sorted(unique_skills))}

    # 3. Second pass: build matrix
    matrix = dok_matrix((len(unique_professions), len(unique_skills)), dtype=np.int32)

    print("\n🔧 Second pass: building matrix...")
    reader = pd.read_csv(file_path, sep='|', header=None,
                         names=['profession', 'hard_skills', 'soft_skills'],
                         chunksize=chunk_size, low_memory=False)

    skipped_skills = set()  # Track skipped skills
    for chunk in reader:
        for _, row in chunk.iterrows():
            if pd.isna(row['profession']):
                continue

            # Normalize profession
            profession = str(row['profession']).strip()
            if not profession or profession not in profession_to_idx:
                continue

            p_idx = profession_to_idx[profession]

            # Process hard skills with checking
            if pd.notna(row['hard_skills']):
                for skill in str(row['hard_skills']).split(';'):
                    if skill := skill.strip():
                        if skill in skill_to_idx:
                            s_idx = skill_to_idx[skill]
                            matrix[p_idx, s_idx] += 1
                        else:
                            skipped_skills.add(skill)

            # Process soft skills with checking
            if pd.notna(row['soft_skills']):
                for skill in str(row['soft_skills']).split(';'):
                    if skill := skill.strip():
                        skill_key = "SOFT_" + skill
                        if skill_key in skill_to_idx:
                            s_idx = skill_to_idx[skill_key]
                            matrix[p_idx, s_idx] += 1
                        else:
                            skipped_skills.add(skill_key)

    # Report skipped skills
    if skipped_skills:
        print(f"\n⚠️ Skipped {len(skipped_skills)} skills missing from dictionary")
        print("Examples of skipped skills:", list(skipped_skills)[:5])

    # 4. Save results
    print("\n💾 Saving results...")
    # Matrix in CSR format
    csr_matrix = matrix.tocsr()
    save_npz(os.path.join(output_dir, "profession_skills_matrix.npz"), csr_matrix)

    # Index dictionaries
    with open(os.path.join(output_dir, "profession_to_idx.pkl"), 'wb') as f:
        pickle.dump(profession_to_idx, f)

    with open(os.path.join(output_dir, "skill_to_idx.pkl"), 'wb') as f:
        pickle.dump(skill_to_idx, f)

    # Reverse indices
    idx_to_profession = {v: k for k, v in profession_to_idx.items()}
    idx_to_skill = {v: k for k, v in skill_to_idx.items()}

    with open(os.path.join(output_dir, "idx_to_profession.pkl"), 'wb') as f:
        pickle.dump(idx_to_profession, f)

    with open(os.path.join(output_dir, "idx_to_skill.pkl"), 'wb') as f:
        pickle.dump(idx_to_skill, f)

    print(f"✅ Done! Matrix size {csr_matrix.shape[0]} professions × {csr_matrix.shape[1]} skills")
    print(f"📁 Results saved in: {output_dir}")

if __name__ == "__main__":
    # Process the user's uploaded file
    input_file = "/home/ubuntu/upload/extracted_skills_with_professions.txt"
    output_dir = "/home/ubuntu/profession-skills-api/src/data"
    
    # Check if the uploaded file contains actual data or just the code
    with open(input_file, 'r') as f:
        content = f.read()
    
    if content.startswith('import pandas'):
        print("❌ The uploaded file contains Python code, not data.")
        print("Please upload the actual profession-skills data file (extracted_skills_with_professions.txt)")
        print("The file should contain data in format: profession|hard_skills|soft_skills")
    else:
        print("Processing user data file...")
        process_user_data(input_file, output_dir)

