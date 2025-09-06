from WarrantyClaimAISystem import WarrantyClaimAgent
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
agent = WarrantyClaimAgent(model_provider="groq",model_name="deepseek-r1-distill-llama-70b",api_key=api_key,policy_dir="/home/egg/Downloads/Warranty-Claim-AI/src/policy_dir",vector_db_dir="/home/egg/Downloads/Warranty-Claim-AI/src/vector_db")
form_data = """sample_form_data = {
    "customer_name": "Alicia Warren",
    "customer_id": "CUST-481516",
    "contact_email": "alicia.w@email.com",
    "product_model": "QuantumBook Pro X1 (2024)",
    "serial_number": "QB-PROX1-2024-987654",
    "purchase_date": "2024-11-20", # This is within the 1-year warranty
    "issue_description": "The laptop screen has started showing random green horizontal lines and flickering. The issue is most prominent when the screen background is dark. No physical damage or drops have occurred."
}"""
image_files = "/home/egg/Downloads/Warranty-Claim-AI/src/images"
historical_claims ="""{
        "claim_id": "CLAIM-2024-03-1138",
        "product_model": "QuantumBook Pro X1 (2024)",
        "issue": "AC power adapter stopped working",
        "decision": "Approved",
        "resolution": "Replacement adapter shipped",
        "date_filed": "2025-03-15"
    }"""
r1,r2 = agent.process_claim(form_data=form_data,image_files=image_files,historical_claims=historical_claims)
print(r2)
with open("result.txt","w") as f:
    f.write(str(r1))
    f.write("\n")
    f.write(str(r2))
    f.close()