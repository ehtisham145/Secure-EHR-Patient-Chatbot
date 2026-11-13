from presidio_analyzer import AnalyzerEngine,PatternRecognizer,Pattern
# Analyzer Engine is used to scan the text 
from presidio_anonymizer import AnonymizerEngine
# The main work of anonymizer is to take the critial text and reduct the senstive information

class ClinicalPIIRedactor():
    def __init__(self):
        print("Initialize Presidio Zero Trust Middleware ...")
        self.analyzer=AnalyzerEngine()
        self.anonymizer=AnonymizerEngine()

        # Custom SSN(Social Security Number) Pattern Recognizer
        ssn_pattern = Pattern(name="catch_all_ssn", regex=r"\d{3}-\d{2}-\d{4}", score=0.9)
        ssn_recognizer = PatternRecognizer(supported_entity="US_SSN", patterns=[ssn_pattern])
        self.analyzer.registry.add_recognizer(ssn_recognizer)

        hospital_recognizer = PatternRecognizer(
            supported_entity = 'ORGANIZATION',
            deny_list=["Massachusetts General Hospital", "Mayo Clinic", "Cleveland Clinic"],
            deny_list_score=1.0 
        )  

        self.analyzer.registry.add_recognizer(hospital_recognizer)
        self.target_entities = [
            "PERSON", 
            "PHONE_NUMBER", 
            "EMAIL_ADDRESS", 
            "US_SSN", 
            "LOCATION", 
            "ORGANIZATION", 
            "DATE_TIME"
        ]

# Remove the Clinical Text from the database using the target entities
    def redact_clinical_context(self, raw_text: str) -> str:
        if not raw_text:
            return ""
        # The main purpose of analyzer is to find the sensititve information
        analyzer_results = self.analyzer.analyze(
            text=raw_text,
            entities=self.target_entities,
            language='en',
            score_threshold=0.4 
        )
        # The main purpose of anonymizer is to remove the sensitive information
        anonymized_result = self.anonymizer.anonymize(
            text=raw_text,
            analyzer_results=analyzer_results
        )
        
        return anonymized_result.text

if __name__ == "__main__":
    redactor = ClinicalPIIRedactor()
    
    simulated_ehr_note = """
    Patient John Doe (SSN: 234-00-1234) was admitted to Massachusetts General Hospital 
    on March 15th following a severe reaction to Furosemide. 
    Wife Jane Doe can be reached at 415-555-0198 or jane.doe@email.com.
    """
    
    print("\nRAW PHI FROM DATABASE:")
    print(simulated_ehr_note.strip())
    
    print("\nREDACTED OUTPUT (Safe for LLM Prompt):")
    safe_text = redactor.redact_clinical_context(simulated_ehr_note)
    print(safe_text.strip())