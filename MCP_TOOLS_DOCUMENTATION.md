# PreciseMCP Server - Tools Documentation

This document provides comprehensive documentation for all Model Context Protocol (MCP) tools and resources exposed by the PreciseMCP server.

## Overview

The PreciseMCP server provides a set of tools for interacting with the RadFlow API to manage patient information, study details, case updates, and reports. All tools return JSON responses with consistent error handling.

## Resources

### `hello://greeting`
**Type**: Resource  
**Description**: A simple greeting resource for testing server connectivity.

**Returns**: 
```
"Hello from your RadFlow MCP server! 🚀"
```

---

## Patient Information Tools

### `fetch_patient_info`
**Description**: Fetch comprehensive patient information from the RadFlow API using patient ID.

**Parameters**:
- `patient_id` (string, required): The patient ID to fetch information for

**Returns**: JSON string containing:
```json
{
  "success": boolean,
  "patient_id": "string",
  "data": {
    "success": boolean,
    "message": "string",
    "patients": [
      {
        "patient_id": "string",
        "first_name": "string",
        "last_name": "string",
        "phone": "string",
        "sex": "string",
        "financial_type": "string",
        "language": "string",
        "birth_date": "string",
        "address": "string",
        "doi": "string",
        "dol": "string",
        "radiologist_name": "string"
      }
    ],
    "numbered_list": "string"
  },
  "message": "string"
}
```

**Example Usage**:
```json
{
  "tool": "fetch_patient_info",
  "arguments": {
    "patient_id": "12345"
  }
}
```

---

### `fetch_patient_by_id`
**Description**: Fetch patient information by ID from the RadFlow API (simplified version).

**Parameters**:
- `patient_id` (string, required): The patient's ID

**Returns**: JSON string with patient information and processing status

**Example Usage**:
```json
{
  "tool": "fetch_patient_by_id",
  "arguments": {
    "patient_id": "12345"
  }
}
```

---

### `fetch_patient_by_phone`
**Description**: Fetch patient data using phone number lookup.

**Parameters**:
- `phone` (string, required): Phone number to fetch data for (supports +1 prefix)

**Returns**: JSON string with patient data matching the phone number

**Notes**: 
- Automatically handles +1 prefix removal for consistency
- Returns all patients associated with the phone number

**Example Usage**:
```json
{
  "tool": "fetch_patient_by_phone",
  "arguments": {
    "phone": "+15551234567"
  }
}
```

### `fetch_patient_by_name_and_doi`
**Description**: Fetch patient data using first name, last name, and date of injury.

**Parameters**:
- `firstName` (string, required): Patient's first name
- `lastName` (string, required): Patient's last name  
- `doi` (string, required): Date of injury in YYYY-MM-DD or MM/DD/YYYY format (automatically converted to YYYY-MM-DD 00:00:00)

**Returns**: JSON string containing:
```json
{
  "success": true,
  "data": {
    // Patient data from RadFlow API
  }
}
```

**Example Usage**:
```json
{
  "tool": "fetch_patient_by_name_and_doi",
  "arguments": {
    "firstName": "SERVANDO",
    "lastName": "ZAMORA", 
    "doi": "06/01/2024"
  }
}
```

**Supported DOI Formats**:
- `"2024-06-01"` (YYYY-MM-DD)
- `"06/01/2024"` (MM/DD/YYYY)

Both formats are automatically converted to `"2024-06-01 00:00:00"` for the API.

---

## Study Management Tools

### `fetch_study_details`
**Description**: Fetch detailed study information for a patient by their ID.

**Parameters**:
- `patient_id` (string, required): Patient ID to fetch studies for

**Returns**: JSON string containing:
```json
{
  "success": boolean,
  "message": "string",
  "studies": [
    {
      "appointment_time": "string",
      "pre_arrival_minutes": number,
      "facility": {
        "facility_name": "string",
        "address": "string"
      },
      "study_description": "string",
      "status": "string",
      "modality": "string",
      "referring_physician": "string",
      "insurance": "string",
      "authorization_number": "string"
    }
  ]
}
```

**Example Usage**:
```json
{
  "tool": "fetch_study_details",
  "arguments": {
    "patient_id": "12345"
  }
}
```

---

## Case Management Tools

### `get_case_update_details`
**Description**: Fetch case update details for a specific patient.

**Parameters**:
- `patient_id` (string, required): The ID of the patient

**Returns**: JSON string containing case update details or error message
```json
{
  "success": boolean,
  "data": "object"
}
```

**Authentication**: Uses Chatbot API credentials

**Example Usage**:
```json
{
  "tool": "get_case_update_details",
  "arguments": {
    "patient_id": "12345"
  }
}
```

---

### `insert_case_update_log`
**Description**: Insert a case update log entry for a patient with event-specific validation.

**Parameters**:
- `patient_id` (string, required): The ID of the patient
- `user_name` (string, required): The name of the user performing the action
- `event_id` (integer, required): The ID of the event
- `notes` (string, optional): Notes for the log
- `liability_expected_date` (string, optional): Expected date for liability clearance (MM/DD/YYYY)
- `expected_payment_date` (string, optional): Expected date for payment (MM/DD/YYYY)
- `payment_date_sent` (string, optional): Date when payment was sent (MM/DD/YYYY)
- `check_number` (string, optional): The check number
- `check_amount` (float, optional): The amount of the check
- `send_payment_of_estimated_date` (string, optional): Estimated date for sending payment (MM/DD/YYYY)

**Event-Specific Requirements**:
- **Event ID 2**: Requires `liability_expected_date`
- **Event ID 5**: Requires `expected_payment_date`
- **Event ID 6**: Requires `payment_date_sent`, `check_number`, and `check_amount`
- **Event ID 7**: Requires `notes`
- **Event ID 20**: Requires `send_payment_of_estimated_date`

**Returns**: JSON string with operation result
```json
{
  "success": boolean,
  "data": "object"
}
```

**Example Usage**:
```json
{
  "tool": "insert_case_update_log",
  "arguments": {
    "patient_id": "12345",
    "user_name": "Dr. Smith",
    "event_id": 7,
    "notes": "Patient case review completed"
  }
}
```

---

## Reporting Tools

### `get_patient_report`
**Description**: Fetch the comprehensive report for a specific patient.

**Parameters**:
- `patient_id` (string, required): The ID of the patient

**Returns**: JSON string containing patient report data
```json
{
  "success": boolean,
  "data": "object"
}
```

**Authentication**: Uses Chatbot API credentials

**Example Usage**:
```json
{
  "tool": "get_patient_report",
  "arguments": {
    "patient_id": "12345"
  }
}
```

---

### `get_patient_lien_bill_balance`
**Description**: Get patient lien bill balance details from the RadFlow API.

**Parameters**:
- `patient_id` (string, required): The ID of the patient to fetch lien bill balance details for

**Returns**: JSON string containing lien bill balance details or error message
```json
{
  "success": boolean,
  "data": "object"
}
```

**Authentication**: Uses Chatbot API credentials (Basic Auth)

**Example Usage**:
```json
{
  "tool": "get_patient_lien_bill_balance",
  "arguments": {
    "patient_id": "PRE00001"
  }
}
```

---

## Patient Status and Tasks

### `get_patient_todo_status`
**Description**: Get the to-do status for a patient from the RadFlow API.

**Parameters**:
- `patient_id` (string, required): The ID of the patient
- `document_type_id` (integer, optional): The type ID of the document (default: 21)
- `logged_partner_id` (integer, optional): The ID of the logged-in partner (default: 1)
- `patient_preferred_language` (string, optional): The patient's preferred language (default: "english")

**Returns**: JSON string with to-do status information
```json
{
  "success": boolean,
  "status": "object"
}
```

**Authentication**: Uses JWT token with automatic refresh

**Example Usage**:
```json
{
  "tool": "get_patient_todo_status",
  "arguments": {
    "patient_id": "12345",
    "document_type_id": 21,
    "patient_preferred_language": "english"
  }
}
```

---

## Error Handling

All tools follow a consistent error handling pattern:

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Detailed error message"
}
```

### Common Error Types
- **API Request Failures**: HTTP status codes other than 200
- **Network Issues**: Connection timeouts, connection errors
- **Data Processing Errors**: JSON parsing failures, invalid response format
- **Authentication Errors**: JWT token issues, invalid credentials
- **Validation Errors**: Missing required parameters for specific event IDs

---

## Authentication

The server uses two authentication methods:

1. **JWT Authentication**: For RadFlow Partner API (automatically managed with token caching)
2. **Basic Authentication**: For Chatbot API endpoints using username/password

All authentication is handled internally by the server.

---

## Rate Limiting & Timeouts

- **Request Timeout**: 30 seconds for all API calls
- **SSL Verification**: Disabled for all requests (verify=False)
- **Connection Pooling**: Managed automatically by httpx.AsyncClient

---

## Usage Notes

1. **Patient ID Format**: Patient IDs should be provided as strings
2. **Date Formats**: 
   - **DOI (Date of Injury)**: Supports both YYYY-MM-DD and MM/DD/YYYY formats (automatically converted)
   - **Other dates**: Use MM/DD/YYYY format for case update dates
3. **Phone Numbers**: Support international format with +1 prefix (automatically normalized)
4. **Event IDs**: Specific validation rules apply based on the event type
5. **Language Support**: Patient preferred language defaults to "english"

---

## Server Information

- **Server Type**: FastMCP with Streamable HTTP transport
- **Operation Mode**: Stateless for better scalability
- **Default Port**: 8000 (configurable via PORT environment variable)
- **Health Check**: Use the `hello://greeting` resource to verify server status 