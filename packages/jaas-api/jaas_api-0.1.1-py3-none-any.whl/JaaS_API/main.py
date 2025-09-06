#==========================================================================================
#
#  JaaS API SDK - version 0.1.1 - September 5, 2025
#
#==========================================================================================

import requests
import json
from typing import Dict, List, Optional

class JaaSEvaluationClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.jaas-ai.com"  
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def evaluate(
        self,
        question: str,
        answer: str,
        evaluation_criteria: List[str],
        eval_type: str = "S",
        ground_truth_answer: Optional[str] = None,
        context: Optional[str] = None,
        cohort: Optional[str] = None
    ) -> Dict:
        """
        Submit an evaluation request
        
        Args:
            question: The input question
            answer: The AI-generated answer to evaluate
            evaluation_criteria: List of criteria to evaluate against
            eval_type: Evaluation type ("S", "C", "D", "V")
            ground_truth_answer: Reference answer 
            context: Additional context
            cohort: Cohort name for grouping 
            
        Returns:
            Dict containing evaluation results
        """
        payload = {
            "question": question,
            "answer": answer,  
            "evaluation_criteria": evaluation_criteria,
            "type": eval_type
        }
        
        if ground_truth_answer:
            payload["ground_truth_answer"] = ground_truth_answer 
        if context:
            payload["context"] = context
        if cohort:
            payload["cohort"] = cohort
            
        try:
            response = requests.post(
                f"{self.base_url}/v1/evaluate",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: Unable to connect to {self.base_url}")
            print(f"Error details: {e}")
            raise
        except requests.exceptions.Timeout:
            print(f"Request timed out while connecting to {self.base_url}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise