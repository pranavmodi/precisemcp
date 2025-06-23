# PreciseMCP Tools - Quick Reference

## Tool Summary Table

| Tool Name | Category | Parameters | Purpose | Authentication |
|-----------|----------|------------|---------|----------------|
| `hello://greeting` | Resource | None | Server health check | None |
| `fetch_patient_info` | Patient Info | `patient_id` | Get comprehensive patient data | RadFlow API |
| `fetch_patient_by_id` | Patient Info | `patient_id` | Get patient data (simplified) | RadFlow API |
| `fetch_patient_by_phone` | Patient Info | `phone` | Find patients by phone number | RadFlow API |
| `fetch_study_details` | Studies | `patient_id` | Get patient study information | RadFlow API |
| `get_case_update_details` | Case Management | `patient_id` | Get case update details | Chatbot API |
| `insert_case_update_log` | Case Management | `patient_id`, `user_name`, `event_id`, + optional fields | Insert case update log | Chatbot API |
| `get_patient_report` | Reporting | `patient_id` | Get patient report | Chatbot API |
| `get_patient_todo_status` | Tasks | `patient_id` + optional params | Get patient to-do status | JWT Auth |

## Quick Parameter Reference

### Required Parameters
- **patient_id**: All tools except `fetch_patient_by_phone` and `hello://greeting`
- **phone**: Only `fetch_patient_by_phone`
- **user_name**: Only `insert_case_update_log`
- **event_id**: Only `insert_case_update_log`

### Event ID Requirements (insert_case_update_log)
| Event ID | Required Additional Parameters |
|----------|-------------------------------|
| 2 | `liability_expected_date` |
| 5 | `expected_payment_date` |
| 6 | `payment_date_sent`, `check_number`, `check_amount` |
| 7 | `notes` |
| 20 | `send_payment_of_estimated_date` |

## Common Response Patterns

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description"
}
```

## Quick Examples

### Get Patient by ID
```json
{
  "tool": "fetch_patient_by_id",
  "arguments": { "patient_id": "12345" }
}
```

### Find Patient by Phone
```json
{
  "tool": "fetch_patient_by_phone", 
  "arguments": { "phone": "+15551234567" }
}
```

### Add Case Note
```json
{
  "tool": "insert_case_update_log",
  "arguments": {
    "patient_id": "12345",
    "user_name": "Dr. Smith",
    "event_id": 7,
    "notes": "Patient follow-up completed"
  }
}
```

### Check Server Health
```json
{
  "resource": "hello://greeting"
}
```

---

For detailed documentation, see [MCP_TOOLS_DOCUMENTATION.md](MCP_TOOLS_DOCUMENTATION.md) 