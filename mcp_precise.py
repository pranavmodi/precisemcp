#!/usr/bin/env python3
"""
PreciseMCP Server with Streamable HTTP Transport

This server runs independently and can be accessed via HTTP.
"""

import asyncio
import logging
import json
import traceback
import time
import jwt
from typing import Dict, Any, Optional
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
RADFLOW_PARTNER_API_URL = os.getenv("RADFLOW_PARTNER_API_URL", "https://staging-app.radflow360.com/patientportalapi/Partner/GetRefreshToken")
RADFLOW_TODO_STATUS_API_URL = os.getenv("RADFLOW_TODO_STATUS_API_URL", "https://staging-app.radflow360.com/patientportalapi/Patient/GetPatientToDoStatus")
PARTNER_API_KEY = "f0M65v8av8ns3iZ4XFEacXc1dKWqWI6756Nb4nRVymYysN1jtKmSBQUyEfgGeRc3tDyBF5bP61Z8VcT4zm8GvCe8xSiLgS143V6Y3OQ4a062qutS13qgx55T4A9DNhAk"
# Chatbot API configuration
CHATBOT_API_USER = "Chatbot"
CHATBOT_API_PASSWORD = "lcNvSuG3pXDb0rht6Vwh0rhDpXCCzCzCzWe4L3GjQsGHpXiz0rxZ6V4s9K8W5eLcv"
GET_CASE_UPDATE_DETAILS_URL = "https://staging-app.radflow360.com/chatbotapi/GetCaseUpdateDetailsChatbot"
GET_PATIENT_REPORT_URL = "https://staging-app.radflow360.com/chatbotapi/GetPatientReportChatbot"
INSERT_CASE_UPDATE_LOG_URL = "https://staging-app.radflow360.com/chatbotapi/InsertCaseUpdateLogChatbot"

# In-memory cache for the JWT
JWT_CACHE = {"token": None, "expires_at": 0}

# Create FastMCP server instance with streamable HTTP support
mcp = FastMCP("precise-mcp-server", stateless_http=True)

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
async def fetch_patient_info(patient_id: str) -> str:
    """
    Fetch patient information from the RadFlow API using patient ID.
    
    Args:
        patient_id: The patient ID to fetch information for
    """
    try:
        logger.info(f"Fetching patient data for patient_id: {patient_id}")
        
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

@mcp.tool()
async def get_case_update_details(patient_id: str) -> str:
    """
    Fetches case update details for a given patient.

    Args:
        patient_id: The ID of the patient.

    Returns:
        A JSON string containing the case update details or an error message.
    """
    logger.info(f"Fetching case update details for patient ID: {patient_id}")
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {"patientID": patient_id}
        auth = (CHATBOT_API_USER, CHATBOT_API_PASSWORD)

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                GET_CASE_UPDATE_DETAILS_URL,
                json=payload,
                headers=headers,
                auth=auth,
                timeout=30.0
            )
            response.raise_for_status()
            return json.dumps({"success": True, "data": response.json()})

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
        return json.dumps({"success": False, "error": error_msg})

@mcp.tool()
async def get_patient_report(patient_id: str) -> str:
    """
    Fetches the report for a given patient.

    Args:
        patient_id: The ID of the patient.

    Returns:
        A JSON string containing the patient report or an error message.
    """
    logger.info(f"Fetching patient report for patient ID: {patient_id}")
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {"patientID": patient_id}
        auth = (CHATBOT_API_USER, CHATBOT_API_PASSWORD)

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                GET_PATIENT_REPORT_URL,
                json=payload,
                headers=headers,
                auth=auth,
                timeout=30.0
            )
            response.raise_for_status()
            return json.dumps({"success": True, "data": response.json()})

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
        return json.dumps({"success": False, "error": error_msg})

@mcp.tool()
async def insert_case_update_log(
    patient_id: str,
    user_name: str,
    event_id: int,
    notes: Optional[str] = None,
    liability_expected_date: Optional[str] = None,
    expected_payment_date: Optional[str] = None,
    payment_date_sent: Optional[str] = None,
    check_number: Optional[str] = None,
    check_amount: Optional[float] = None,
    send_payment_of_estimated_date: Optional[str] = None,
) -> str:
    """
    Inserts a case update log for a patient.

    Args:
        patient_id: The ID of the patient.
        user_name: The name of the user performing the action.
        event_id: The ID of the event.
        notes: Notes for the log.
        liability_expected_date: Expected date for liability clearance (MM/DD/YYYY).
        expected_payment_date: Expected date for payment (MM/DD/YYYY).
        payment_date_sent: Date when payment was sent (MM/DD/YYYY).
        check_number: The check number.
        check_amount: The amount of the check.
        send_payment_of_estimated_date: Estimated date for sending payment (MM/DD/YYYY).

    Returns:
        A JSON string with the result of the operation.
    """
    logger.info(f"Inserting case update log for patient ID: {patient_id}, Event ID: {event_id}")
    try:
        # Validation based on event_id
        if event_id == 2 and not liability_expected_date:
            return json.dumps({"success": False, "error": "liability_expected_date is required for event_id 2"})
        if event_id == 5 and not expected_payment_date:
            return json.dumps({"success": False, "error": "expected_payment_date is required for event_id 5"})
        if event_id == 6 and not (payment_date_sent and check_number and check_amount is not None):
            return json.dumps({"success": False, "error": "payment_date_sent, check_number, and check_amount are required for event_id 6"})
        if event_id == 7 and not notes:
            return json.dumps({"success": False, "error": "notes is required for event_id 7"})
        if event_id == 20 and not send_payment_of_estimated_date:
            return json.dumps({"success": False, "error": "send_payment_of_estimated_date is required for event_id 20"})

        payload = {
            "patientId": patient_id,
            "userName": user_name,
            "eventId": event_id,
            "eventStatus": event_id,
            "notes": notes,
            "liabilityExpectedDate": liability_expected_date,
            "expectedPaymentDate": expected_payment_date,
            "paymentDateSent": payment_date_sent,
            "checkNumber": check_number,
            "checkAmount": check_amount,
            "sendPaymentOfEstimatedDate": send_payment_of_estimated_date,
        }
        # Remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        auth = (CHATBOT_API_USER, CHATBOT_API_PASSWORD)

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                INSERT_CASE_UPDATE_LOG_URL,
                json=payload,
                headers=headers,
                auth=auth,
                timeout=30.0
            )
            response.raise_for_status()
            return json.dumps({"success": True, "data": response.json()})

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return json.dumps({"success": False, "error": error_msg})
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
        return json.dumps({"success": False, "error": error_msg})

async def _get_and_cache_jwt_token() -> str:
    """
    Get a JWT token, using a cache to avoid repeated requests.
    If the cached token is expired or not present, it fetches a new one.

    Returns:
        The JWT token string.

    Raises:
        Exception: If fetching or parsing the token fails.
    """
    # Check if the cached token is still valid (with a 60-second buffer)
    if JWT_CACHE["token"] and JWT_CACHE["expires_at"] > time.time() + 60:
        logger.info("Using cached JWT token.")
        return JWT_CACHE["token"]

    logger.info("Fetching new JWT token.")
    url = f"{RADFLOW_PARTNER_API_URL}?partnerApiKey={PARTNER_API_KEY}"
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(url, headers=headers, timeout=30.0)
            response.raise_for_status()  # Will raise an exception for 4xx/5xx status
            
            data = response.json()
            token_data = data.get("result") # The token data is in the 'result' field

            if not token_data:
                raise ValueError("API response missing 'result' object")

            jwt_token = token_data.get("jwtToken")

            if not jwt_token:
                raise ValueError("JWT token is missing or invalid in API response")

            # Decode the token to get the expiration time from its payload
            decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
            expires_at = decoded_token.get("exp")

            if not expires_at:
                raise ValueError("Expiration time ('exp') not found in JWT payload")

            # Update cache
            JWT_CACHE["token"] = jwt_token
            JWT_CACHE["expires_at"] = expires_at
            logger.info("Successfully fetched and cached new JWT token.")
            
            return jwt_token

        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, ValueError, jwt.PyJWTError) as e:
            logger.error(f"Failed to get or cache JWT token: {e}")
            raise Exception(f"Could not retrieve authentication token: {e}")

@mcp.tool()
async def get_patient_todo_status(
    patient_id: str,
    document_type_id: int = 21,
    logged_partner_id: int = 1,
    patient_preferred_language: str = "english"
) -> str:
    """
    Get the to-do status for a patient from the RadFlow API.

    Args:
        patient_id: The ID of the patient.
        document_type_id: The type ID of the document.
        logged_partner_id: The ID of the logged-in partner.
        patient_preferred_language: The patient's preferred language.

    Returns:
        JSON string with the to-do status or an error.
    """
    try:
        logger.info(f"Fetching to-do status for patient ID: {patient_id}")

        # Get the JWT token using the caching mechanism
        jwt_token = await _get_and_cache_jwt_token()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "patientId": patient_id,
            "documentTypeId": document_type_id,
            "loggedPartnerId": logged_partner_id,
            "jwtToken": jwt_token,
            "patientPreferredLanguage": patient_preferred_language
        }

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                RADFLOW_TODO_STATUS_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Successfully retrieved patient to-do status.")
                    return json.dumps({"success": True, "status": data}, indent=2)
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON response from to-do status endpoint.")
                    return json.dumps({"success": False, "error": "Invalid JSON response from API"})
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return json.dumps({"success": False, "error": error_msg})

    except Exception as e:
        error_msg = f"An unexpected error occurred while getting patient to-do status: {str(e)}"
        logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
        return json.dumps({"success": False, "error": error_msg})

# Expose the ASGI app *after* all tools and resources are defined
app = mcp.streamable_http_app()

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