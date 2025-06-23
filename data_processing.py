#!/usr/bin/env python3
"""
Data processing utilities for PreciseMCP Server
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger("precise-mcp-server")

def process_patient_data(data: Dict[str, Any], phone: str) -> Dict[str, Any]:
    """
    Process patient data from API response.
    
    Args:
        data (Dict[str, Any]): Raw API response data
        phone (str): Phone number for indexing
        
    Returns:
        Dict[str, Any]: Success status and message
    """
    try:
        # Check if the API response was successful
        if data.get("responseStatus") != "Success":
            logger.error("API response status indicates failure")
            return {
                "success": False,
                "error": data.get("exception") or "API response indicates failure"
            }

        result = data.get("result", {})
        patient_data_list = []
        
        # Handle the nested JSON string in result.result
        if isinstance(result.get("result"), str):
            try:
                patient_data_list = json.loads(result["result"])
            except json.JSONDecodeError:
                logger.error("Failed to parse nested JSON string in result.result")
                return {
                    "success": False,
                    "error": "Failed to parse patient data"
                }
        elif isinstance(result.get("result"), list):
            patient_data_list = result["result"]
            
        # Get total patients from response
        total_patients = result.get("totalPatients", len(patient_data_list))
            
        if not patient_data_list:
            return {
                "success": False,
                "error": "No patients found"
            }
            
        # Create numbered list of patients
        numbered_list = []
        transformed_patients = []
        
        for i, patient in enumerate(patient_data_list, 1):
            # Transform patient data to match our schema
            transformed_patient = {
                "patient_id": patient.get("PatientId", ""),
                "first_name": patient.get("FirstName", ""),
                "last_name": patient.get("LastName", ""),
                "phone": patient.get("Phone", phone),  # Use provided phone if not in data
                "sex": patient.get("Sex", "").strip(),  # Remove trailing spaces
                "financial_type": patient.get("FinancialTypeName", ""),
                "language": patient.get("LANGUAGE", ""),
                "birth_date": patient.get("BirthDate", ""),
                "address": patient.get("ADDRESS", ""),
                "doi": patient.get("Doi", ""),
                "dol": patient.get("DOL", ""),
                "radiologist_name": patient.get("RadiologistName", "")
            }
            transformed_patients.append(transformed_patient)
            
            # Create numbered list entry
            name = f"{transformed_patient['first_name']} {transformed_patient['last_name']}".strip()
            patient_id = transformed_patient["patient_id"]
            numbered_list.append(f"<button>{i}. {name} (ID: {patient_id})</button>")
        
        return {
            "success": True,
            "message": f"Successfully processed {total_patients} patients",
            "patients": transformed_patients,
            "numbered_list": "\n".join(numbered_list)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to process patient data: {str(e)}"
        } 