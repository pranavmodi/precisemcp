#!/usr/bin/env python3
"""
Test script to verify different MCP transport methods work correctly.
"""

import asyncio
import subprocess
import time
import sys
from pathlib import Path

async def test_sse_transport():
    """Test SSE transport by starting server and client."""
    print("🧪 Testing SSE Transport...")
    print("=" * 40)
    
    # Start the SSE server
    server_process = subprocess.Popen([
        sys.executable, "server.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server is running
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print(f"❌ SSE Server failed to start:")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            return False
        
        print("✅ SSE Server started successfully")
        
        # Run the SSE client
        client_process = subprocess.run([
            sys.executable, "client_http.py"
        ], capture_output=True, text=True, timeout=15)
        
        if client_process.returncode == 0:
            print("✅ SSE Client connected and ran successfully")
            print("Sample output:")
            print(client_process.stdout[:200] + "...")
            return True
        else:
            print(f"❌ SSE Client failed:")
            print(f"stdout: {client_process.stdout}")
            print(f"stderr: {client_process.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ SSE Client timed out")
        return False
    except Exception as e:
        print(f"❌ SSE Test failed: {e}")
        return False
    finally:
        # Clean up server process
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

async def test_streamable_transport():
    """Test Streamable HTTP transport by starting server and client."""
    print("\n🧪 Testing Streamable HTTP Transport...")
    print("=" * 40)
    
    # Start the Streamable HTTP server
    server_process = subprocess.Popen([
        sys.executable, "server_streamable.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server is running
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print(f"❌ Streamable Server failed to start:")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            return False
        
        print("✅ Streamable HTTP Server started successfully")
        
        # Run the Streamable HTTP client
        client_process = subprocess.run([
            sys.executable, "client_streamable.py"
        ], capture_output=True, text=True, timeout=15)
        
        if client_process.returncode == 0:
            print("✅ Streamable HTTP Client connected and ran successfully")
            print("Sample output:")
            print(client_process.stdout[:200] + "...")
            return True
        else:
            print(f"❌ Streamable HTTP Client failed:")
            print(f"stdout: {client_process.stdout}")
            print(f"stderr: {client_process.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Streamable HTTP Client timed out")
        return False
    except Exception as e:
        print(f"❌ Streamable HTTP Test failed: {e}")
        return False
    finally:
        # Clean up server process
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

async def test_stdio_transport():
    """Test stdio transport with the original client."""
    print("\n🧪 Testing stdio Transport...")
    print("=" * 40)
    
    try:
        # Run the stdio client (which spawns its own server)
        client_process = subprocess.run([
            sys.executable, "client.py"
        ], capture_output=True, text=True, timeout=15)
        
        if client_process.returncode == 0:
            print("✅ stdio Client connected and ran successfully")
            print("Sample output:")
            print(client_process.stdout[:200] + "...")
            return True
        else:
            print(f"❌ stdio Client failed:")
            print(f"stdout: {client_process.stdout}")
            print(f"stderr: {client_process.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ stdio Client timed out")
        return False
    except Exception as e:
        print(f"❌ stdio Test failed: {e}")
        return False

async def main():
    """Run all transport tests."""
    print("🚀 MCP Transport Testing Suite")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        "server.py",
        "server_streamable.py", 
        "client.py",
        "client_http.py",
        "client_streamable.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file missing: {file}")
            return
    
    print("✅ All required files present")
    print()
    
    # Test results
    results = {}
    
    # Test stdio transport
    results['stdio'] = await test_stdio_transport()
    
    # Test SSE transport
    results['sse'] = await test_sse_transport()
    
    # Test Streamable HTTP transport  
    results['streamable'] = await test_streamable_transport()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    for transport, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{transport.upper():12} transport: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All transport methods working correctly!")
    else:
        print("⚠️  Some transport methods need attention")

if __name__ == "__main__":
    asyncio.run(main()) 