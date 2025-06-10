#!/usr/bin/env python3
"""
PreciseMCP Server with Streamable HTTP Transport

This server runs independently and can be accessed via HTTP.
"""

import asyncio
import logging
import json
import traceback
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import httpx
import os
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("precise-mcp-server")

# Configuration - You'll need to set this to your actual API URL
RADFLOW_API_URL = os.getenv("RADFLOW_API_URL", "https://app.radflow360.com/chatbotapi/Patient/GetPatientStudyRelatedDetails")

# Create FastMCP server instance with streamable HTTP support
mcp = FastMCP("precise-mcp-server", stateless_http=True)

# Expose the ASGI app
app = mcp.streamable_http_app()

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

@mcp.resource("hello://greeting")
async def get_greeting() -> str:
    """A simple greeting resource."""
    return "Hello from your RadFlow MCP server! 🚀"

@mcp.tool()
async def fetch_patient_info(patient_id: str, conversation_id: str = "default") -> str:
    """
    Fetch patient information from the RadFlow API using patient ID.
    
    Args:
        patient_id: The patient ID to fetch information for
        conversation_id: Optional conversation ID for tracking (defaults to 'default')
    """
    try:
        logger.info(f"Fetching patient data for patient_id: {patient_id}, conversation_id: {conversation_id}")
        
        payload = {
            "patientId": patient_id,
            "phone": "",
            "firstName": "",
            "lastName": "",
            "birthDate": "",
            "doi": "",
            "accessionNumber": "",
            "requiredField": "Details"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"Making API request to {RADFLOW_API_URL} with payload: {json.dumps(payload)}")
        
        async with httpx.AsyncClient(verify=False) as client:
            logger.debug("Created httpx client")
            
            try:
                response = await client.post(
                    RADFLOW_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                logger.debug(f"Received API response with status code: {response.status_code}")
                
                if response.status_code != 200:
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    return json.dumps({
                        "success": False,
                        "error": error_msg
                    })
                
                try:
                    data = response.json()
                    logger.debug("Successfully parsed JSON response")
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse JSON response: {e}"
                    logger.error(f"{error_msg}\nResponse text: {response.text[:500]}")
                    return json.dumps({
                        "success": False,
                        "error": "Invalid JSON response from API"
                    })
                
                logger.info(f"Processing patient data response for ID: {patient_id}")
                result = process_patient_data(data, "")
                
                if result["success"]:
                    logger.info(f"Successfully retrieved patient data: {result['message']}")
                else:
                    logger.error(f"Failed to process patient data: {result.get('error', 'Unknown error')}")
                
                # Return the patient data as a formatted JSON string
                result_with_metadata = {
                    "success": result["success"],
                    "patient_id": patient_id,
                    "conversation_id": conversation_id,
                    "data": result,
                    "message": result.get("message", f"Retrieved patient information for ID: {patient_id}")
                }
                
                return json.dumps(result_with_metadata, indent=2)
                
            except httpx.TimeoutException:
                error_msg = "API request timed out after 30 seconds"
                logger.error(error_msg)
                return json.dumps({
                    "success": False,
                    "error": error_msg
                })
            except httpx.ConnectError as e:
                error_msg = f"Connection error: {str(e)}"
                logger.error(f"Connection error while fetching patient data: {error_msg}")
                return json.dumps({
                    "success": False,
                    "error": error_msg
                })
                
    except Exception as e:
        error_msg = f"Failed to fetch patient data: {str(e)}"
        logger.error(f"Unexpected error in fetch_patient_info: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return json.dumps({
            "success": False,
            "error": error_msg
        })

@mcp.tool()
async def fetch_patient_by_id(patient_id: str) -> str:
    """
    Fetch patient information by ID from the RadFlow API.
    
    Args:
        patient_id: The patient's ID
        
    Returns:
        JSON string with patient information and status
    """
    try:
        logger.info(f"Fetching patient data for ID: {patient_id}")
        
        payload = {
            "patientId": patient_id,
            "phone": "",
            "firstName": "",
            "lastName": "",
            "birthDate": "",
            "doi": "",
            "accessionNumber": "",
            "requiredField": "Details"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                RADFLOW_API_URL,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return json.dumps({
                    "success": False,
                    "error": f"API request failed with status {response.status_code}"
                })
            
            try:
                data = response.json()
                logger.debug("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}\nResponse text: {response.text[:500]}")
                return json.dumps({
                    "success": False,
                    "error": "Invalid JSON response from API"
                })
            
            logger.info(f"Processing patient data response for ID: {patient_id}")
            result = process_patient_data(data, "")
            
            if result["success"]:
                logger.info(f"Successfully retrieved patient data: {result['message']}")
            else:
                logger.error(f"Failed to process patient data: {result.get('error', 'Unknown error')}")
            
            return json.dumps(result, indent=2)
            
    except Exception as e:
        logger.error(f"Unexpected error in fetch_patient_by_id: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return json.dumps({
            "success": False,
            "error": f"Failed to fetch patient data: {str(e)}"
        })

@mcp.tool()
async def fetch_study_details(patient_id: str) -> str:
    """
    Fetch study details for a patient by their ID.
    
    Args:
        patient_id: Patient ID to fetch studies for
        
    Returns:
        JSON string with study details and status
    """
    try:
        logger.info(f"Fetching study details for patient ID: {patient_id}")
        
        payload = {
            "patientId": patient_id,
            "phone": "",
            "firstName": "",
            "lastName": "",
            "birthDate": "",
            "doi": "",
            "accessionNumber": "",
            "requiredField": "Study Details"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                RADFLOW_API_URL,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            response.raise_for_status()
            
            try:
                data = response.json()

                # Check response status
                if data.get("responseStatus") != "Success":
                    error_msg = data.get("exception") or "Failed to fetch study details"
                    return json.dumps({
                        "success": False,
                        "error": error_msg
                    })

                # Extract studies from nested result
                result = data.get("result", {})
                
                raw_studies = []
                if isinstance(result.get("result"), str):
                    try:
                        raw_studies = json.loads(result["result"])
                    except json.JSONDecodeError:
                        return json.dumps({
                            "success": False,
                            "error": "Failed to parse study data"
                        })
                elif isinstance(result.get("result"), list):
                    raw_studies = result["result"]
                
                if not raw_studies:
                    return json.dumps({
                        "success": False,
                        "error": "No studies found"
                    })
                
                # Transform studies to match our schema
                transformed_studies = []
                for study in raw_studies:
                    # Get the latest status from AppointmentStatuses if available
                    latest_status = "Unknown"
                    scheduled_time = ""
                    if study.get("AppointmentStatuses"):
                        for status in study["AppointmentStatuses"]:
                            if status.get("Status"):
                                latest_status = status["Status"]
                            if status.get("ScheduledFor") and status["ScheduledFor"] != "Not Yet Scheduled":
                                scheduled_time = status["ScheduledFor"]
                    
                    # Get facility info from FacilityUsed if available
                    facility_name = ""
                    facility_address = ""
                    if study.get("FacilityUsed") and len(study["FacilityUsed"]) > 0:
                        facility = study["FacilityUsed"][0]  # Take first facility
                        facility_name = facility.get("FacilityName", "")
                        facility_address = facility.get("Address", "")

                    transformed_study = {
                        "appointment_time": scheduled_time,
                        "pre_arrival_minutes": 30,  # Default value
                        "facility": {
                            "facility_name": facility_name,
                            "address": facility_address
                        },
                        "study_description": study.get("StudyDescription", ""),
                        "status": latest_status,
                        "modality": study.get("Modality", ""),
                        "referring_physician": study.get("SchedulerName", "").strip(),
                        "insurance": "",  # Not provided in API
                        "authorization_number": study.get("AccessionNumber", "")
                    }
                    transformed_studies.append(transformed_study)
                
                result_data = {
                    "success": True,
                    "message": f"Successfully retrieved {len(transformed_studies)} studies for patient {patient_id}",
                    "studies": transformed_studies
                }
                
                return json.dumps(result_data, indent=2)
            
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to process study details: {str(e)}"
                })
            
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "success": False,
            "error": f"HTTP error {e.response.status_code}: {str(e)}"
        })
    except httpx.RequestError as e:
        return json.dumps({
            "success": False,
            "error": f"Request failed: {str(e)}"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to fetch study details: {str(e)}"
        })

@mcp.tool()
async def fetch_patient_by_phone(phone: str) -> str:
    """
    Fetch patient data from the API using phone number.
    
    Args:
        phone: Phone number to fetch data for
        
    Returns:
        JSON string with patient data
    """
    try:
        logger.info(f"Fetching patient data for phone: {phone}")
        
        # Remove +1 prefix if present for consistency
        storage_phone = phone.replace("+1", "")
        logger.debug(f"Standardized phone number to: {storage_phone}")
        
        payload = {
            "patientId": "",
            "phone": storage_phone,
            "firstName": "",
            "lastName": "",
            "birthDate": "",
            "doi": "",
            "accessionNumber": "",
            "requiredField": "Details"
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"Making API request to {RADFLOW_API_URL} with payload: {json.dumps(payload)}")
        
        async with httpx.AsyncClient(verify=False) as client:
            logger.debug("Created httpx client")
            
            try:
                response = await client.post(
                    RADFLOW_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                logger.debug(f"Received API response with status code: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    return json.dumps({
                        "success": False,
                        "error": f"API request failed with status {response.status_code}"
                    })
                
                try:
                    data = response.json()
                    logger.debug("Successfully parsed JSON response")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}\nResponse text: {response.text[:500]}")
                    return json.dumps({
                        "success": False,
                        "error": "Invalid JSON response from API"
                    })
                
                logger.info(f"Processing patient data response for phone: {storage_phone}")
                result = process_patient_data(data, storage_phone)
                
                if result["success"]:
                    logger.info(f"Successfully retrieved patient data: {result['message']}")
                else:
                    logger.error(f"Failed to process patient data: {result.get('error', 'Unknown error')}")
                
                return json.dumps(result, indent=2)
                
            except httpx.TimeoutException:
                logger.error(f"API request timed out after 30 seconds")
                return json.dumps({
                    "success": False,
                    "error": "API request timed out after 30 seconds"
                })
            except httpx.ConnectError as e:
                error_msg = f"Connection error: {str(e)}"
                logger.error(f"Connection error while fetching patient data: {error_msg}")
                return json.dumps({
                    "success": False,
                    "error": error_msg
                })
                
    except Exception as e:
        error_msg = f"Failed to fetch patient data: {str(e)}"
        logger.error(f"Unexpected error in fetch_patient_by_phone: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return json.dumps({
            "success": False,
            "error": error_msg
        })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("🚀 Starting PreciseMCP Server...")
    print("=" * 60)
    print("Server will be available at:")
    print(f"  🌐 HTTP endpoint: http://localhost:{port}")
    print("  📡 This server uses Streamable HTTP transport")
    print("  🔄 Stateless operation for better scalability")
    print("  🏥 RadFlow API integration enabled")
    print("  👤 Patient lookup by ID, phone number")
    print("  📋 Study details retrieval")
    print("=" * 60)
    
    # Run with uvicorn for better control over port
    uvicorn.run(app, host="0.0.0.0", port=port) 