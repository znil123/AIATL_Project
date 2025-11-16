import os
from crewai import Agent, Task, Crew, Process, LLM
from ai_crew.agents.crew import Aiatl1Crew
from dotenv import load_dotenv
from datetime import datetime
import sys

# Add the project root to the Python path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.helpers import get_mongo_client

def run(symptoms, name, race, gender, username=None):
    load_dotenv()
    """
    Run the crew with user input and store results in MongoDB.
    """
    
    crew_instance = Aiatl1Crew()
    
    inputs = {
        'symptoms': symptoms,  
        'name': name,
        'race': race,
        'gender': gender,
    }

    # Run the crew and capture outputs
    result = crew_instance.crew().kickoff(inputs=inputs)
    
    # Store results in MongoDB instead of files
    try:
        client = get_mongo_client()
        if not client:
            print("Error: Failed to connect to MongoDB")
            return
        
        db = client["myDatabase"]
        analysis_collection = db["analysis_results"]
        
        # Prepare the analysis document
        final_report = str(result) if result else "Analysis completed but no results were generated."
        
        analysis_doc = {
            "username": username,  # Patient username
            "symptoms": symptoms,
            "final_report": final_report,
            "patient_name": name,
            "race": race,
            "gender": gender,
            "created_at": datetime.utcnow(),
            # Placeholder for individual analyses (can be expanded later)
            "cardiologist_analysis": "Individual analysis will be available in future versions.",
            "pulmonologist_analysis": "Individual analysis will be available in future versions.",
            "neurologist_analysis": "Individual analysis will be available in future versions."
        }
        
        # Insert the analysis result
        analysis_collection.insert_one(analysis_doc)
        print(f"Analysis complete! Results saved to MongoDB for user: {username}")
                
    except Exception as e:
        print(f"Error storing analysis in MongoDB: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
# if __name__ == "__main__":
#    run()