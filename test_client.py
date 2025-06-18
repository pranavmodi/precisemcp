import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# The base URL of your MCP server
SERVER_URL = "http://localhost:8001/mcp"

async def main():
    """Main function to run the test client."""
    print("🚀 Starting MCP Test Client...")
    
    # Use a test phone number to find a patient
    test_phone_number = "8189700937" # Replace with a valid test number if needed
    
    try:
        async with streamablehttp_client(SERVER_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected to MCP Server!")

                # 1. Fetch patient information using a phone number to get a patient ID
                print(f"\n📞 Calling 'fetch_patient_by_phone' with phone: {test_phone_number}")
                
                try:
                    result = await session.call_tool("fetch_patient_by_phone", {"phone": test_phone_number})
                    patient_info_result = json.loads(result.content[0].text)
                    
                    if not patient_info_result.get("success"):
                        print("❌ Test failed: Could not retrieve patient information.")
                        print(f"   Error: {patient_info_result.get('error')}")
                        return

                    patients = patient_info_result.get("patients")
                    if not patients:
                        print("❌ Test failed: No patients found for the provided phone number.")
                        return
                        
                    patient_id = patients[0].get("patient_id")
                    if not patient_id:
                        print("❌ Test failed: Patient data does not contain a 'patient_id'.")
                        return

                    print(f"✅ Success! Found Patient ID: {patient_id}")

                    # 2. Call the get_patient_todo_status tool with the retrieved patient ID
                    print(f"\n📋 Calling 'get_patient_todo_status' for patient ID: {patient_id}")
                    
                    todo_result = await session.call_tool("get_patient_todo_status", {"patient_id": patient_id})
                    
                    # Defensive check for content
                    if not todo_result.content or not todo_result.content[0].text:
                        print("❌ Test failed: Server returned an empty response.")
                        return

                    raw_response = todo_result.content[0].text
                    
                    try:
                        todo_status_result = json.loads(raw_response)
                    except json.JSONDecodeError:
                        # Handle cases where the server returns a non-JSON error string
                        print("❌ Test failed: Server returned a non-JSON response.")
                        print(f"   Server message: {raw_response}")
                        return

                    if todo_status_result.get("success"):
                        print("✅ Test successful: 'get_patient_todo_status' returned a successful response.")
                        print("   Response:")
                        print(json.dumps(todo_status_result.get("status"), indent=2))
                    else:
                        print("❌ Test failed: 'get_patient_todo_status' returned an error.")
                        print(f"   Error: {todo_status_result.get('error')}")
                
                except Exception as e:
                    print(f"❌ An error occurred during tool call: {e}")

    except Exception as e:
        print(f"❌ Failed to connect to MCP server at {SERVER_URL}: {e}")

if __name__ == "__main__":
    asyncio.run(main())