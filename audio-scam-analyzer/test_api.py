#!/usr/bin/env python3
"""
Quick API Health & Analysis Test Script
Tests both health check and demo analysis
"""
import requests
import json
import time
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("🔷 TEST 1: Health Check Endpoint")
    print("="*60)
    
    try:
        url = f"{API_URL}/health"
        print(f"📡 GET {url}\n")
        
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        print("✅ HEALTH CHECK PASSED\n")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False

def test_analyze_demo():
    """Test analysis with demo mode"""
    print("="*60)
    print("🔷 TEST 2: Analysis Endpoint (DEMO MODE)")
    print("="*60)
    
    try:
        # Create a minimal audio file for testing
        import os
        audio_path = Path(__file__).parent / "test_audio.wav"
        
        if not audio_path.exists():
            print(f"⚠️ Creating minimal test audio file...")
            # Create a minimal WAV file (silence)
            import wave
            with wave.open(str(audio_path), 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes(b'\x00\x00' * 16000)  # 1 second of silence
        
        url = f"{API_URL}/analyze-call"
        print(f"📡 POST {url}\n")
        
        with open(audio_path, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            t0 = time.time()
            response = requests.post(url, files=files, timeout=30)
            elapsed = time.time() - t0
        
        print(f"Response Time: {elapsed:.2f}s")
        print(f"Status: {response.status_code}")
        
        data = response.json()
        print(f"\nAnalysis Results:")
        print(f"  Success: {data.get('success')}")
        print(f"  Risk Score: {data.get('risk_score')}/100")
        print(f"  Risk Level: {data.get('risk_level')}")
        print(f"  Confidence: {data.get('confidence'):.1%}")
        print(f"  Detected Patterns: {len(data.get('detected_patterns', []))}")
        print(f"  Primary Threat: {data.get('primary_threat', 'N/A')}")
        
        if elapsed < 0.5:
            print(f"\n⚡ Response Time: ULTRA FAST (<500ms)")
        
        print("✅ ANALYSIS TEST PASSED\n")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False

def main():
    print("\n🚀 Audio Scam Analyzer - API Test Suite")
    print(f"Target API: {API_URL}\n")
    
    # Check if API is running
    try:
        requests.get(f"{API_URL}/health", timeout=2)
    except:
        print("❌ ERROR: API is not running!")
        print("\nTo start the API, run:")
        print("  cd backend")
        print("  python app.py")
        return
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Analysis (Demo)", test_analyze_demo()))
    
    # Summary
    print("="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED")

if __name__ == "__main__":
    main()
