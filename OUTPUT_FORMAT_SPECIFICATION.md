# MCP Patient Lookup Output Format Specification

## 📋 **For the Other Coding Agent**

This document specifies the **exact output format** you can expect from all patient lookup MCP tools.

## 🎯 **Standardized Response Format**

All patient lookup tools (`fetch_patient_info`, `fetch_patient_by_id`, `fetch_patient_by_phone`, `fetch_patient_by_name_and_doi`) now return the **same standardized format**:

### ✅ **Success Response**
```json
{
  "success": true,
  "message": "Successfully processed 1 patients", 
  "patients": [
    {
      "patient_id": "PRE1006707",           // 🎯 This is what you need!
      "first_name": "SERVANDO",
      "last_name": "ZAMORA", 
      "phone": "3109519475",
      "sex": "M",
      "financial_type": "PERSONAL INJURY",
      "language": "english", 
      "birth_date": "1970-10-20",
      "address": "2032 E HATCHWAY ST COMPTON CA 90222",
      "doi": "2024-06-01",
      "dol": "2024-06-01", 
      "radiologist_name": "STAN KREMSKY"
    }
  ],
  "numbered_list": "<button>1. SERVANDO ZAMORA (ID: PRE1006707)</button>"
}
```

### ❌ **Error Response**
```json
{
  "success": false,
  "error": "No patients found"
}
```

## 🚀 **How to Extract Patient ID**

### **Python Code Example**
```python
import json

# Parse MCP response 
response = json.loads(mcp_response_string)

# Extract patient ID
if response.get("success") and response.get("patients"):
    patient_id = response["patients"][0]["patient_id"]
    print(f"Found patient ID: {patient_id}")
else:
    error = response.get("error", "Unknown error")
    print(f"Error: {error}")
```

### **JavaScript Code Example**
```javascript
// Parse MCP response
const response = JSON.parse(mcpResponseString);

// Extract patient ID
if (response.success && response.patients && response.patients.length > 0) {
    const patientId = response.patients[0].patient_id;
    console.log(`Found patient ID: ${patientId}`);
} else {
    const error = response.error || "Unknown error";
    console.log(`Error: ${error}`);
}
```

## 📊 **Field Definitions**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `patient_id` | string | **Primary identifier** for the patient | "PRE1006707" |
| `first_name` | string | Patient's first name (uppercase) | "SERVANDO" |
| `last_name` | string | Patient's last name (uppercase) | "ZAMORA" |
| `phone` | string | Patient's phone number | "3109519475" |
| `sex` | string | Patient's gender | "M" or "F" |
| `financial_type` | string | Insurance/payment type | "PERSONAL INJURY" |
| `language` | string | Patient's preferred language | "english" |
| `birth_date` | string | Date of birth (YYYY-MM-DD) | "1970-10-20" |
| `address` | string | Patient's address | "2032 E HATCHWAY ST..." |
| `doi` | string | Date of injury (YYYY-MM-DD) | "2024-06-01" |
| `dol` | string | Date of loss (YYYY-MM-DD) | "2024-06-01" |
| `radiologist_name` | string | Assigned radiologist | "STAN KREMSKY" |

## 🔄 **Multiple Patients**

If multiple patients are found, the `patients` array will contain multiple objects:

```json
{
  "success": true,
  "message": "Successfully processed 2 patients",
  "patients": [
    { "patient_id": "PRE1006707", "first_name": "SERVANDO", ... },
    { "patient_id": "PRE1006708", "first_name": "MARIA", ... }
  ],
  "numbered_list": "<button>1. SERVANDO ZAMORA (ID: PRE1006707)</button>\n<button>2. MARIA GONZALEZ (ID: PRE1006708)</button>"
}
```

## ✅ **Validation Checklist**

Before processing the response, always check:

1. ✅ `response.success === true`
2. ✅ `response.patients` exists and is an array
3. ✅ `response.patients.length > 0`
4. ✅ `response.patients[0].patient_id` exists and is not empty

## 🚨 **Common Error Cases**

| Error Message | Meaning | Action |
|---------------|---------|--------|
| "No patients found" | No matching patients in database | Try different search criteria |
| "API response indicates failure" | RadFlow API returned error | Check API connectivity |
| "Failed to parse patient data" | Data format issue | Report to development team |
| "Connection error" | Network issue | Retry or check network |

## 🎯 **Summary for Quick Integration**

**What you need**: `response.patients[0].patient_id`

**Always check**: `response.success === true` first

**This format is now consistent across ALL patient lookup tools!** 🚀 