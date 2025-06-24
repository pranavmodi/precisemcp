#!/usr/bin/env python3
"""
Configuration settings for PreciseMCP Server
"""

import os

# RadFlow API Configuration
RADFLOW_API_URL = os.getenv("RADFLOW_API_URL", "https://app.radflow360.com/chatbotapi/Patient/GetPatientStudyRelatedDetails")
RADFLOW_PARTNER_API_URL = os.getenv("RADFLOW_PARTNER_API_URL", "https://staging-app.radflow360.com/patientportalapi/Partner/GetRefreshToken")
RADFLOW_TODO_STATUS_API_URL = os.getenv("RADFLOW_TODO_STATUS_API_URL", "https://staging-app.radflow360.com/patientportalapi/Patient/GetPatientToDoStatus")
PARTNER_API_KEY = "f0M65v8av8ns3iZ4XFEacXc1dKWqWI6756Nb4nRVymYysN1jtKmSBQUyEfgGeRc3tDyBF5bP61Z8VcT4zm8GvCe8xSiLgS143V6Y3OQ4a062qutS13qgx55T4A9DNhAk"

# Chatbot API Configuration
CHATBOT_API_USER = "Chatbot"
CHATBOT_API_PASSWORD = "lcNvSuG3pXDb0rht6Vwh0rhDpXCCzCzCzWe4L3GjQsGHpXiz0rxZ6V4s9K8W5eLcv"
GET_CASE_UPDATE_DETAILS_URL = "https://staging-app.radflow360.com/chatbotapi/GetCaseUpdateDetailsChatbot"
GET_PATIENT_REPORT_URL = "https://staging-app.radflow360.com/chatbotapi/GetPatientReportChatbot"
INSERT_CASE_UPDATE_LOG_URL = "https://staging-app.radflow360.com/chatbotapi/InsertCaseUpdateLogChatbot"
GET_PATIENT_LIEN_BILL_BALANCE_URL = "https://staging-app.radflow360.com/chatbotapi/GetPatientLienBillBalanceDetails"

# Server Configuration
DEFAULT_PORT = 8001