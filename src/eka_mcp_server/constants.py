MEDICATION_UNDERSTANDING_DESC = """
    Search repository of drugs based on drug brand name, generic composition, 
    or form, to get detailed information about the drug.
    Tool can provide information about a single drug, single or compound generics at a time.
    Use this tool whenever any recommendation about medicines has to be given.
    After the use of this tool, always respond with the name of the drug instead of 
    generic name response from the tool unless otherwise specified
"""

MEDICATION_INTERACTION_DESC = """
   Check for interactions between multiple drugs.
   Tool can check interactions between 2 or more drugs.
   The tools returns the interaction category X, A, B, C, D and the interacting drug pairs
"""

SEARCH_PROTOCOLS_DESC = """
    Search the publicly available protocols and treatment guidelines for Indian patients.
    When the query is about any of these tags/conditions:
    {}

    requires output from following tools - protocol_publishers 

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
    - Publisher preference should be asked before protocol search if it's not specified in the query, do not assume any publisher
    - The publishers supported are dynamic and supported publishers can be fetched only from the tool protocol_publishers  
    - If the publisher list is empty, then do not invoke the tool
    3. Publisher preference selection
    - Once possible publishers are available, confirm which preferred publisher from the retrieved list should be queried

    Key triggers for tool invocation:
    - Questions about condition management protocols
    - Screening recommendations
    - Treatment guidelines
    - Monitoring parameters
    - Drug choices

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
    - If results aren't relevant, rely on inherent medical knowledge
"""

PROTOCOL_PUBLISHERS_DESC = """
    Get all available publishers of protocols for the supported tags/conditions. 
    Accepts only {} these tags/conditions
"""
