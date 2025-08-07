import pandas as pd
import numpy as np
import pickle
from scipy.sparse import dok_matrix, save_npz
import os

def create_sample_data():
    """Create sample profession-skills data for testing"""
    
    # Sample data
    sample_data = [
        ("Software Developer", "Python;JavaScript;React;Node.js;Git;SQL;Docker", "Communication;Problem Solving;Teamwork;Time Management"),
        ("Data Scientist", "Python;R;Machine Learning;Statistics;SQL;Pandas;NumPy;Scikit-learn", "Analytical Thinking;Communication;Curiosity;Attention to Detail"),
        ("Web Designer", "HTML;CSS;JavaScript;Photoshop;Figma;Adobe Illustrator;UI/UX Design", "Creativity;Communication;Attention to Detail;Problem Solving"),
        ("Project Manager", "Agile;Scrum;JIRA;Microsoft Project;Risk Management;Budget Management", "Leadership;Communication;Organization;Problem Solving;Time Management"),
        ("DevOps Engineer", "Docker;Kubernetes;AWS;Jenkins;Terraform;Linux;Git;CI/CD", "Problem Solving;Communication;Automation;System Thinking"),
        ("Frontend Developer", "JavaScript;React;Vue.js;HTML;CSS;TypeScript;Webpack;Git", "Problem Solving;Attention to Detail;Communication;Creativity"),
        ("Backend Developer", "Python;Java;Node.js;SQL;MongoDB;REST API;Microservices;Docker", "Problem Solving;Logical Thinking;Communication;System Design"),
        ("Mobile Developer", "Swift;Kotlin;React Native;Flutter;iOS;Android;Git;REST API", "Problem Solving;Attention to Detail;Communication;User Experience"),
        ("QA Engineer", "Selenium;TestNG;JIRA;Manual Testing;Automation Testing;Bug Tracking", "Attention to Detail;Communication;Analytical Thinking;Problem Solving"),
        ("UI/UX Designer", "Figma;Sketch;Adobe XD;Photoshop;User Research;Wireframing;Prototyping", "Creativity;Empathy;Communication;Problem Solving;User-Centered Design"),
        ("Database Administrator", "SQL;MySQL;PostgreSQL;Oracle;Database Design;Performance Tuning;Backup", "Problem Solving;Attention to Detail;System Thinking;Communication"),
        ("System Administrator", "Linux;Windows Server;Networking;Security;Monitoring;Scripting;Virtualization", "Problem Solving;System Thinking;Communication;Troubleshooting"),
        ("Marketing Manager", "Digital Marketing;SEO;Google Analytics;Social Media;Content Marketing;Email Marketing", "Creativity;Communication;Strategic Thinking;Analytical Skills"),
        ("Sales Representative", "CRM;Lead Generation;Negotiation;Customer Service;Sales Process;Product Knowledge", "Communication;Persuasion;Relationship Building;Goal Oriented"),
        ("Business Analyst", "Requirements Analysis;SQL;Excel;Process Modeling;Documentation;Stakeholder Management", "Analytical Thinking;Communication;Problem Solving;Attention to Detail")
    ]
    
    # Create profession and skill mappings
    unique_professions = set()
    unique_skills = set()
    
    for profession, hard_skills, soft_skills in sample_data:
        unique_professions.add(profession)
        
        # Process hard skills
        for skill in hard_skills.split(';'):
            if skill.strip():
                unique_skills.add(skill.strip())
        
        # Process soft skills with prefix
        for skill in soft_skills.split(';'):
            if skill.strip():
                unique_skills.add("SOFT_" + skill.strip())
    
    # Create index mappings
    profession_to_idx = {prof: idx for idx, prof in enumerate(sorted(unique_professions))}
    skill_to_idx = {skill: idx for idx, skill in enumerate(sorted(unique_skills))}
    
    # Create reverse mappings
    idx_to_profession = {v: k for k, v in profession_to_idx.items()}
    idx_to_skill = {v: k for k, v in skill_to_idx.items()}
    
    # Create matrix
    matrix = dok_matrix((len(unique_professions), len(unique_skills)), dtype=np.int32)
    
    # Fill matrix with sample data
    for profession, hard_skills, soft_skills in sample_data:
        p_idx = profession_to_idx[profession]
        
        # Add hard skills
        for skill in hard_skills.split(';'):
            skill = skill.strip()
            if skill and skill in skill_to_idx:
                s_idx = skill_to_idx[skill]
                # Add random frequency between 5-50
                matrix[p_idx, s_idx] = np.random.randint(5, 51)
        
        # Add soft skills
        for skill in soft_skills.split(';'):
            skill = skill.strip()
            if skill:
                skill_key = "SOFT_" + skill
                if skill_key in skill_to_idx:
                    s_idx = skill_to_idx[skill_key]
                    # Add random frequency between 10-80
                    matrix[p_idx, s_idx] = np.random.randint(10, 81)
    
    # Save data
    output_dir = "src/data"
    
    # Save matrix
    csr_matrix = matrix.tocsr()
    save_npz(os.path.join(output_dir, "profession_skills_matrix.npz"), csr_matrix)
    
    # Save dictionaries
    with open(os.path.join(output_dir, "profession_to_idx.pkl"), 'wb') as f:
        pickle.dump(profession_to_idx, f)
    
    with open(os.path.join(output_dir, "skill_to_idx.pkl"), 'wb') as f:
        pickle.dump(skill_to_idx, f)
    
    with open(os.path.join(output_dir, "idx_to_profession.pkl"), 'wb') as f:
        pickle.dump(idx_to_profession, f)
    
    with open(os.path.join(output_dir, "idx_to_skill.pkl"), 'wb') as f:
        pickle.dump(idx_to_skill, f)
    
    print(f"Sample data created successfully!")
    print(f"Professions: {len(unique_professions)}")
    print(f"Skills: {len(unique_skills)}")
    print(f"Matrix shape: {csr_matrix.shape}")

if __name__ == "__main__":
    create_sample_data()

