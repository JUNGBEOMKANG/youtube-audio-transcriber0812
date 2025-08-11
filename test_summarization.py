#!/usr/bin/env python3
"""
Test script for the enhanced summarization functionality
"""
import requests
import json
import time

def test_summarization_endpoints():
    """Test the summarization endpoints"""
    base_url = "http://localhost:8000"
    
    # Sample text for testing
    test_text = """
    안녕하세요! 오늘은 Python 프로그래밍에 대해서 이야기해보겠습니다.
    
    Python은 정말 강력하고 사용하기 쉬운 프로그래밍 언어입니다. 많은 개발자들이 사용하고 있죠.
    
    첫 번째로, Python의 문법은 매우 직관적입니다. 들여쓰기를 사용해서 코드 블록을 구분하기 때문에 읽기 쉬운 코드를 작성할 수 있습니다.
    
    두 번째로, Python에는 다양한 라이브러리가 있습니다. NumPy, Pandas, Django 등 여러 분야에서 사용할 수 있는 라이브러리들이 풍부하게 제공됩니다.
    
    마지막으로, Python은 머신러닝과 데이터 분석 분야에서 특히 인기가 높습니다. TensorFlow, PyTorch 같은 딥러닝 프레임워크도 Python으로 개발되었죠.
    
    그래서 Python을 배우시는 것을 강력히 추천드립니다!
    """
    
    print("🧪 Summarization Endpoints Test")
    print("=" * 50)
    
    # Test Key Summary endpoint
    print("\n📝 Testing Key Summary Endpoint...")
    try:
        response = requests.post(
            f"{base_url}/summarize/key_summary",
            json={"text": test_text},
            timeout=30
        )
        
        if response.status_code == 200:
            key_summary = response.json()
            print("✅ Key Summary - Success!")
            print(f"Generated {len(key_summary)} paragraph summaries:")
            for i, item in enumerate(key_summary, 1):
                print(f"  {i}. {item['paragraph_summary']}")
        else:
            print(f"❌ Key Summary - Failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Key Summary - Server not running! Please start the server first.")
        return False
    except Exception as e:
        print(f"❌ Key Summary - Error: {e}")
    
    # Test Curator endpoint
    print("\n🎯 Testing Curator Endpoint...")
    try:
        response = requests.post(
            f"{base_url}/summarize/curator",
            json={"text": test_text},
            timeout=30
        )
        
        if response.status_code == 200:
            curator_summary = response.json()
            print("✅ Curator Summary - Success!")
            print(f"Title: {curator_summary.get('title', 'N/A')}")
            print(f"One-line Summary: {curator_summary.get('one_line_summary', 'N/A')}")
            print("Key Points:")
            for i, point in enumerate(curator_summary.get('key_points', []), 1):
                print(f"  {i}. {point}")
        else:
            print(f"❌ Curator Summary - Failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Curator Summary - Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    return True

if __name__ == "__main__":
    print("Starting summarization test...")
    print("Make sure the server is running with: python app.py")
    time.sleep(2)
    test_summarization_endpoints()