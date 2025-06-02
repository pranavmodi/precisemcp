#!/usr/bin/env python3
"""
Independent MCP Server with Streamable HTTP Transport

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("streamable-mcp-server")

# Configuration - You'll need to set this to your actual API URL
RADFLOW_API_URL = os.getenv("RADFLOW_API_URL", "https://app.radflow360.com/chatbotapi/Patient/GetPatientStudyRelatedDetails")

# Create FastMCP server instance with streamable HTTP support
mcp = FastMCP("streamable-mcp-server", stateless_http=True)

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
                
                logger.info(f"Successfully retrieved patient data for patient_id: {patient_id}")
                
                # Return the patient data as a formatted JSON string
                result = {
                    "success": True,
                    "patient_id": patient_id,
                    "conversation_id": conversation_id,
                    "data": data,
                    "message": f"Successfully retrieved patient information for ID: {patient_id}"
                }
                
                return json.dumps(result, indent=2)
                
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

if __name__ == "__main__":
    print("🚀 Starting RadFlow Streamable MCP Server...")
    print("=" * 60)
    print("Server will be available at:")
    print("  🌐 HTTP endpoint: http://localhost:8000/mcp")
    print("  📡 This server uses Streamable HTTP transport")
    print("  🔄 Stateless operation for better scalability")
    print("  🏥 RadFlow API integration enabled")
    print("=" * 60)
    
    # Run with streamable HTTP transport (default port is 8000)
    mcp.run(transport="streamable-http") 