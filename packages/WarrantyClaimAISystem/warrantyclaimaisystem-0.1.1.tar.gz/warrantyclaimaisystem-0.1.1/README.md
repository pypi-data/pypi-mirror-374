# Warranty Claim AI System

The Warranty Claim AI System is a powerful Python-based toolkit designed to automate and streamline the warranty claim process. By leveraging generative AI, this system intelligently analyzes claim data, validates it against policies, checks for fraud, and provides a comprehensive report, automating the manual work of claim adjudicators.

## Features

- **Automated Claim Processing:** End-to-end automation of the warranty claim lifecycle, from intake to final decision.
- **Intelligent Data Extraction:** Utilizes OCR to extract and structure data from claim forms and uploaded images of documents or products.
- **AI-Powered Validation:** Employs LLMs to validate the completeness and legitimacy of claim information.
- **Fraud Detection:** Analyzes claim data and historical patterns to identify potential fraud.
- **RAG-Based Policy Checking:** A Retrieval-Augmented Generation (RAG) system checks the claim against your specific warranty policies.
- **Comprehensive Reporting:** Generates a detailed report for each claim, including the final decision, reasoning, and any necessary next steps.
- **Multi-Provider LLM Support:** Easily switch between different LLM providers like OpenAI, Google, and Groq.

## How It Works

The system processes warranty claims through a series of steps orchestrated by a processing graph:

1.  **Claim Intake:** The system takes in customer-submitted form data and images. OCR is used to extract text from images, and an LLM structures all the initial data.
2.  **Validation:** The structured data is validated for completeness, quality, and legitimacy.
3.  **Fraud Detection:** The claim is analyzed for any signs of fraud by comparing it with historical data and looking for suspicious patterns.
4.  **Policy Check:** The system uses a RAG model to search a vector store of your warranty policies to determine if the claim is covered.
5.  **Adjudication:** Based on all the previous steps, a final decision is made: approve, deny, or flag for manual review. A detailed report is generated.

## Installation

To use the Warranty Claim AI System, you first need to clone the repository and install the required dependencies.

```bash
git clone https://github.com/your-username/Warranty-Claim-AI.git
cd Warranty-Claim-AI
pip install -r requirements.txt
```

## Usage

Here is a basic example of how to process a warranty claim:

```python
import os
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
```
## Result
### Final Decision and Comprehensive Report on Warranty Claim

#### **Warranty Claim Summary**
- **Customer Name:** Alicia Warren
- **Customer ID:** CUST-481516
- **Product Model:** QuantumBook Pro X1 (2024)
- **Serial Number:** QB-PROX1-2024-987654
- **Purchase Date:** November 20, 2024
- **Warranty Period:** November 20, 2024, to November 20, 2025
- **Issue Reported:** Screen flickering with green horizontal lines, especially on dark backgrounds.
- **Claim Submission Date:** October 30, 2024

---

### **Decision**
- **Approved Amount:** $850.00 (Cost of repair or replacement)
- **Confidence:** 95%
- **Decision Factors:**
  - The claim is within the active warranty period.
  - The issue aligns with covered defects under the warranty policy (Sections 3.2 and 3.4).
  - No evidence of physical damage or misuse.
  - Low fraud risk assessment.

---

### **Reasoning**
1. **Warranty Coverage:**
   - The product is within the 1-year warranty period.
   - The issue described (green horizontal lines and flickering) is consistent with hardware defects covered under the warranty (Section 3.2 and 3.4).

2. **Fraud Risk Assessment:**
   - **Fraud Score:** Low (2/10)
   - **Fraud Indicators:**
     - Missing purchase amount and place.
     - Missing claim amount requested.
     - Limited details on issue onset and troubleshooting.
   - **Conclusion:** No significant fraud indicators identified.

3. **Technical Feasibility:**
   - The issue is plausible and consistent with known display hardware defects.
   - The symptoms described (green lines and flickering) are common indicators of a faulty display panel.

4. **Policy Compliance:**
   - The claim adheres to the warranty policy, with no exclusions applying (e.g., no physical damage, no misuse).
   - The customer has provided sufficient information to process the claim.

---

### **Next Actions**
1. **Process the Claim:**
   - Approve the claim for repair or replacement of the laptop.
   - The approved amount is $850.00, covering the cost of repair or replacement.

2. **Customer Communication:**
   - Inform Alicia Warren of the approval and outline the next steps.
   - Provide instructions for arranging the repair or replacement.

3. **Documentation:**
   - Update the claim status to "Approved" in the system.
   - Record the approved amount and the reason for approval.

4. **Quality Assurance:**
   - Conduct a follow-up to ensure the repair or replacement is completed satisfactorily.
   - Monitor customer feedback to ensure resolution.

---

### **Customer Message**
"Dear Alicia Warren,

Thank you for submitting your warranty claim. After a thorough review, we are pleased to inform you that your claim has been approved. The issue with your QuantumBook Pro X1 (2024) screen flickering and displaying green horizontal lines is covered under your warranty.

We will arrange for your laptop to be repaired or replaced at no additional cost to you. You will receive further instructions shortly regarding the next steps in the process.

If you have any questions or need assistance, please do not hesitate to contact us.

Thank you for choosing our products.

Best regards,
[Your Name]  
Warranty Claims Team"

---

### **Review Required**
- **Manual Review Required:** No
- **Reason:** The claim is valid, within the warranty period, and aligns with the warranty policy. No fraud indicators or policy ambiguities were identified.

---

This comprehensive report outlines the decision-making process, ensuring transparency and fairness in the adjudication of the warranty claim.
## Configuration

1.  **API Keys:** The system requires API keys for the LLM provider you choose to use. Create a `.env` file in the root of the project and add your API keys:

    ```
    GROQ_API_KEY="your_groq_api_key"
    OPENAI_API_KEY="your_openai_api_key"
    GOOGLE_API_KEY="your_google_api_key"
    ```

2.  **Warranty Policies:** Place your warranty policy documents (in `.txt` or `.md` format) in the `src/policy_dir` directory. The RAG system will automatically create a vector store from these documents.

## Project Structure

```
/Warranty-Claim-AI
├───.env                # API keys and environment variables
├───README.md           # This file
├───requirements.txt    # Project dependencies
├───result.txt          # Output file for the claim report
└───src/
    ├───images/         # Directory for claim images
    ├───policy_dir/     # Directory for your warranty policy files
    │   └───policy.txt
    ├───vector_db/      # Directory for the policy vector store
    └───warranty_claim_system/
        ├───Agent.py        # Main agent orchestrating the claim processing
        ├───model.py        # Wrapper for different LLM providers
        ├───ocr.py          # OCR processing for images
        ├───rag_system.py   # RAG system for policy checking
        └───test.py         # Example script for running the system
```
