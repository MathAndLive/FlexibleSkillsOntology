import os
import pickle
import numpy as np
from scipy.sparse import csr_matrix, save_npz
from collections import defaultdict, Counter
import gc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedDataProcessor:
    """
    Optimized data processor for large files (10GB+)
    Uses streaming processing and memory-efficient data structures
    """
    
    def __init__(self, chunk_size=10000):
        self.chunk_size = chunk_size
        self.profession_counter = Counter()
        self.skill_counter = Counter()
        self.profession_skills = defaultdict(Counter)
        
    def process_large_file(self, input_file_path, output_dir):
        """
        Process large data file in chunks to avoid memory issues
        """
        logger.info(f"Starting processing of large file: {input_file_path}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Phase 1: Stream through file to collect unique professions and skills
        logger.info("Phase 1: Collecting unique professions and skills...")
        self._collect_unique_values(input_file_path)
        
        # Phase 2: Create mappings
        logger.info("Phase 2: Creating mappings...")
        profession_to_idx, skill_to_idx = self._create_mappings()
        
        # Phase 3: Build sparse matrix efficiently
        logger.info("Phase 3: Building sparse matrix...")
        matrix = self._build_sparse_matrix(input_file_path, profession_to_idx, skill_to_idx)
        
        # Phase 4: Save results
        logger.info("Phase 4: Saving results...")
        self._save_results(output_dir, matrix, profession_to_idx, skill_to_idx)
        
        logger.info(f"Processing complete! {len(profession_to_idx)} professions, {len(skill_to_idx)} skills")
        return len(profession_to_idx), len(skill_to_idx)
    
    def _collect_unique_values(self, file_path):
        """
        Stream through file to collect unique professions and skills
        """
        line_count = 0
        
        with open(file_path, 'r', encoding='utf-8', buffering=8192*16) as f:
            for line in f:
                line_count += 1
                if line_count % 100000 == 0:
                    logger.info(f"Processed {line_count} lines...")
                    
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('|')
                if len(parts) < 3:
                    continue
                    
                profession = parts[0].strip()
                hard_skills = parts[1].strip()
                soft_skills = parts[2].strip()
                
                if profession:
                    self.profession_counter[profession] += 1
                    
                    # Process hard skills
                    if hard_skills:
                        for skill in hard_skills.split(';'):
                            skill = skill.strip()
                            if skill:
                                self.skill_counter[skill] += 1
                                self.profession_skills[profession][skill] += 1
                    
                    # Process soft skills
                    if soft_skills:
                        for skill in soft_skills.split(';'):
                            skill = skill.strip()
                            if skill:
                                soft_skill_key = f"SOFT_{skill}"
                                self.skill_counter[soft_skill_key] += 1
                                self.profession_skills[profession][soft_skill_key] += 1
                
                # Periodic garbage collection for large files
                if line_count % 500000 == 0:
                    gc.collect()
        
        logger.info(f"Collected {len(self.profession_counter)} unique professions")
        logger.info(f"Collected {len(self.skill_counter)} unique skills")
    
    def _create_mappings(self):
        """
        Create profession and skill mappings
        """
        # Sort for consistent ordering
        professions = sorted(self.profession_counter.keys())
        skills = sorted(self.skill_counter.keys())
        
        profession_to_idx = {prof: idx for idx, prof in enumerate(professions)}
        skill_to_idx = {skill: idx for idx, skill in enumerate(skills)}
        
        return profession_to_idx, skill_to_idx
    
    def _build_sparse_matrix(self, file_path, profession_to_idx, skill_to_idx):
        """
        Build sparse matrix efficiently using COO format first, then convert to CSR
        """
        num_professions = len(profession_to_idx)
        num_skills = len(skill_to_idx)
        
        # Use lists to collect COO data
        row_indices = []
        col_indices = []
        data = []
        
        logger.info(f"Building matrix of size {num_professions} x {num_skills}")
        
        # Use the pre-collected profession_skills data
        for profession, skills_counter in self.profession_skills.items():
            if profession in profession_to_idx:
                prof_idx = profession_to_idx[profession]
                
                for skill, count in skills_counter.items():
                    if skill in skill_to_idx:
                        skill_idx = skill_to_idx[skill]
                        row_indices.append(prof_idx)
                        col_indices.append(skill_idx)
                        data.append(count)
        
        # Create COO matrix and convert to CSR for efficient operations
        from scipy.sparse import coo_matrix
        coo_matrix_obj = coo_matrix((data, (row_indices, col_indices)), 
                                   shape=(num_professions, num_skills), dtype=np.int32)
        
        # Convert to CSR for efficient row operations
        csr_matrix_obj = coo_matrix_obj.tocsr()
        
        # Clear temporary data
        del row_indices, col_indices, data, coo_matrix_obj
        gc.collect()
        
        return csr_matrix_obj
    
    def _save_results(self, output_dir, matrix, profession_to_idx, skill_to_idx):
        """
        Save all results to files
        """
        # Save sparse matrix
        save_npz(os.path.join(output_dir, "profession_skills_matrix.npz"), matrix)
        
        # Save mappings
        with open(os.path.join(output_dir, "profession_to_idx.pkl"), 'wb') as f:
            pickle.dump(profession_to_idx, f)
        
        with open(os.path.join(output_dir, "skill_to_idx.pkl"), 'wb') as f:
            pickle.dump(skill_to_idx, f)
        
        # Create reverse mappings
        idx_to_profession = {v: k for k, v in profession_to_idx.items()}
        idx_to_skill = {v: k for k, v in skill_to_idx.items()}
        
        with open(os.path.join(output_dir, "idx_to_profession.pkl"), 'wb') as f:
            pickle.dump(idx_to_profession, f)
        
        with open(os.path.join(output_dir, "idx_to_skill.pkl"), 'wb') as f:
            pickle.dump(idx_to_skill, f)
        
        logger.info(f"Results saved to {output_dir}")


def process_large_data_file(input_file_path, output_dir):
    """
    Main function to process large data files
    """
    processor = OptimizedDataProcessor(chunk_size=10000)
    return processor.process_large_file(input_file_path, output_dir)


if __name__ == "__main__":
    # Example usage
    input_file = "/home/ubuntu/upload/extracted_skills_with_professions.txt"
    output_dir = "src/data"
    
    try:
        num_professions, num_skills = process_large_data_file(input_file, output_dir)
        print(f"SUCCESS: {num_professions} professions, {num_skills} skills processed")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

