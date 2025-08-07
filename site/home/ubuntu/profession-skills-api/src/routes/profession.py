from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import pickle
import numpy as np
from scipy.sparse import load_npz
import os
from difflib import get_close_matches

profession_bp = Blueprint('profession', __name__)

# Global variables to store loaded data
matrix = None
profession_to_idx = None
skill_to_idx = None
idx_to_profession = None
idx_to_skill = None

def clear_cache():
    """Clear cached data to force reload"""
    global profession_to_idx, skill_to_idx, matrix, idx_to_profession, idx_to_skill
    profession_to_idx = None
    skill_to_idx = None
    matrix = None
    idx_to_profession = None
    idx_to_skill = None

def load_data():
    """Load the profession-skills matrix and dictionaries"""
    global matrix, profession_to_idx, skill_to_idx, idx_to_profession, idx_to_skill
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    try:
        # Load matrix
        matrix = load_npz(os.path.join(data_dir, "profession_skills_matrix.npz"))
        
        # Load dictionaries
        with open(os.path.join(data_dir, "profession_to_idx.pkl"), 'rb') as f:
            profession_to_idx = pickle.load(f)
            
        with open(os.path.join(data_dir, "skill_to_idx.pkl"), 'rb') as f:
            skill_to_idx = pickle.load(f)
            
        with open(os.path.join(data_dir, "idx_to_profession.pkl"), 'rb') as f:
            idx_to_profession = pickle.load(f)
            
        with open(os.path.join(data_dir, "idx_to_skill.pkl"), 'rb') as f:
            idx_to_skill = pickle.load(f)
            
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

@profession_bp.route('/professions', methods=['GET'])
@cross_origin()
def get_professions():
    """Get list of all professions"""
    if profession_to_idx is None:
        if not load_data():
            return jsonify({"error": "Data not available"}), 500
    
    professions = list(profession_to_idx.keys())
    professions.sort()
    return jsonify({"professions": professions})

@profession_bp.route('/search', methods=['GET'])
@cross_origin()
def search_professions():
    """Search professions by query"""
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return jsonify({"matches": []})
    
    if profession_to_idx is None:
        if not load_data():
            return jsonify({"error": "Data not available"}), 500
    
    # Get all profession names
    professions = list(profession_to_idx.keys())
    
    # Find close matches (case insensitive)
    matches = []
    for profession in professions:
        if query in profession.lower():
            matches.append(profession)
    
    # If no exact matches, use fuzzy matching
    if not matches:
        matches = get_close_matches(query, professions, n=10, cutoff=0.3)
    
    # Limit to top 10 matches
    matches = matches[:10]
    
    return jsonify({"matches": matches})

@profession_bp.route('/skills/<profession>', methods=['GET'])
@cross_origin()
def get_skills_for_profession(profession):
    """Get skills for a specific profession"""
    if profession_to_idx is None:
        if not load_data():
            return jsonify({"error": "Data not available"}), 500
    
    # Check if profession exists
    if profession not in profession_to_idx:
        return jsonify({"error": "Profession not found"}), 404
    
    # Get profession index
    prof_idx = profession_to_idx[profession]
    
    # Get skills for this profession (row from matrix)
    skills_row = matrix[prof_idx].toarray().flatten()
    
    # Calculate total job postings for this profession
    # This is the maximum frequency among all skills for this profession
    total_job_postings = int(skills_row.max()) if skills_row.size > 0 else 0
    
    # Create list of skills with their frequencies
    skills_data = []
    for skill_idx, frequency in enumerate(skills_row):
        if frequency > 0:  # Only include skills that appear
            skill_name = idx_to_skill[skill_idx]
            
            # Determine if it's a soft skill
            is_soft_skill = skill_name.startswith("SOFT_")
            display_name = skill_name[5:] if is_soft_skill else skill_name
            
            skills_data.append({
                "name": display_name,
                "frequency": int(frequency),
                "total_postings": total_job_postings,
                "type": "soft" if is_soft_skill else "hard"
            })
    
    # Sort by frequency (descending)
    skills_data.sort(key=lambda x: x["frequency"], reverse=True)
    
    return jsonify({
        "profession": profession,
        "skills": skills_data,
        "total_skills": len(skills_data),
        "total_job_postings": total_job_postings
    })

@profession_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """Get general statistics about the data"""
    if profession_to_idx is None:
        if not load_data():
            return jsonify({"error": "Data not available"}), 500
    
    total_professions = len(profession_to_idx)
    total_skills = len(skill_to_idx)
    
    # Count soft vs hard skills
    soft_skills = sum(1 for skill in skill_to_idx.keys() if skill.startswith("SOFT_"))
    hard_skills = total_skills - soft_skills
    
    return jsonify({
        "total_professions": total_professions,
        "total_skills": total_skills,
        "hard_skills": hard_skills,
        "soft_skills": soft_skills
    })

