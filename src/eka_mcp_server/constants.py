INDIAN_BRANDED_DRUG_SEARCH = """
    Search repository of drugs based on drug brand name, generic composition, 
    or form, to get detailed information about the drug.
    Tool can provide information about a single drug, single or compound generics at a time.
    Use this tool whenever any recommendation about medicines has to be given.
    After the use of this tool, always respond with the name of the drug instead of 
    generic name response from the tool unless otherwise specified
"""

INDIAN_TREATMENT_PROTOCOL_SEARCH = """
    Search the publicly available protocols and treatment guidelines for Indian patients.
    Not for general knowledge or symptom-only queries.
    
    Key triggers for tool invocation:
    - Strictly for clinical decision-making — diagnosis, evaluation, or management. 
    - Questions about condition management protocols

    requires output from following tools - protocol_publishers. 
    This tool can only accept input from the list of publishers as described by protocol_publishers  

    Prerequisite before invoking the tool
    1. Intent conformation
    - No assumptions can be made about condition about based on symptoms solely.
    - Ask the doctor if they would like symptomatic treatment or tag/condition driven
    - Always confirm the suspected condition(s) with the doctor before searching protocols or treatments.
    - Explicit conformation could be in patient's history or else the doctor's reference in the chat.
    - While request conformation, provide the user with options of the potential conditions and request them to choose from them.
        <example>
        Example option provision:
        1. DM2
        2. Hypertension
        </example>
    - In case the confirmed condition is not in the list, then do not invoke the tool
    2. Publisher retrieval
    - The publishers supported are dynamic and supported publishers can be fetched only from the tool protocol_publishers  
    - If the publisher list is empty, then do not invoke the tool  
    3. Publisher preference selection
    - Invoke the tool with the user given preference of a publisher or the first available publisher. 
    - In the output explicitly offer the user if they would like to see output from other relevant publishers as listed in protocol_publishers

    Query writing guidelines:
    - Incase the question is too broad, breakdown the query into multiple sub queries asking targeted questions
    - This tool will be invoked multiple times for each sub-query
    - Query needs to be specific and concise, use keywords commonly found in medical protocols published by medical bodies like ADA, ICMR, RSSDI
    Example
    user query - "What are the treatment guidelines for diabetes?"
    sub queries -
    1. "Monitoring parameters for diabetes"
    2. "Treatment strategies for diabetes"
    3. "Drug choices for diabetes"

    Important notes:
    - When asking for conformation of any kind, question cannot exceed 10 words
    - Use exact condition names from the list
    - Keep queries concise and specific
    - Don't use question words in queries
    - If results aren't relevant, discard the results and proceed to answer
"""

PROTOCOL_PUBLISHERS_DESC = """
    Get list of all available publishers of protocols 
"""

SNOMED_LINKER_DESC = """
When the doctor requests for exact SNOMED ID, this tools needs to be invoked, no other trigger to invoke this tool.
First, Extract every distinct disease or medical condition explicitly mentioned in a doctor’s free-text sentence or short note.

STRICT GUIDELINES
Segmentation
- Strip away dates, durations, pronouns, conjunctions, and filler words.
- Retain only the raw disease/condition phrases exactly as they appear.

Deduplication
- If the same disease/condition (or its exact synonym) appears multiple times, list it only once.

Strict Input Matching
- Do NOT infer, translate, re-phrase, or interpret clinically.
- Do NOT map to codes or preferred terms—output only the original phrases.
"""

PHARMACOLOGY_SEARCH_DESC = """
Search through the generic details of a drug from the National Formulary of India 2011. 
The tool has to be invoked with the name of the generic. 

Key triggers for tool invocation:
- Need information about indications, dosage, contraindications, adverse-effects and pregnancy safety of a generic
- Do not invoke the tool for trivial general information

The tool can work with both single and compound generics. 
The tool will respond with both single and compound generics when available
The results are ranked based on relevance of the input query.

For searching compound generic, the input should be like A + B, where A and B are the names of the generics.

Eg: On searching for Rifampicin - both Rifampicin and Rifampicin + Isoniazid are given the results. 
Based on the context of the chat, the assistant will use the tool results and focus on relevant parts as required.

In case combined generics fail then the tool should be called with individual generics multiple times
"""
