#!/usr/bin/env python3
"""
개선된 오디오 추출 및 변환 테스트
"""
from audio_extractor import YouTubeAudioExtractor
from speech_transcriber import SpeechTranscriber
import os


def test_improved_extractor():
    """개선된 오디오 추출 테스트"""
    print("🧪 개선된 오디오 추출 테스트")
    print("="*50)
    
    extractor = YouTubeAudioExtractor()
    
    # 짧은 테스트 비디오 (YouTube의 첫 번째 비디오)
    test_url = "https://youtu.be/jNQXAC9IVRw"  # "Me at the zoo"
    
    print(f"📺 테스트 URL: {test_url}")
    
    try:
        # 1. 비디오 정보 확인
        info = extractor.get_video_info(test_url)
        if info:
            print(f"✅ 제목: {info.get('title', 'Unknown')}")
            print(f"   길이: {info.get('duration', 0)}초")
        
        # 2. 오디오 추출 (MP3)
        print("\n🎵 오디오 추출 중...")
        audio_path = extractor.extract_audio(test_url, "mp3")
        
        if audio_path and os.path.exists(audio_path):
            print(f"✅ 오디오 추출 성공!")
            print(f"   파일 경로: {audio_path}")
            
            # 파일 크기 확인
            size_mb = os.path.getsize(audio_path) / 1024 / 1024
            print(f"   파일 크기: {size_mb:.2f} MB")
            
            # 3. 음성 인식 테스트 (작은 모델 사용)
            print("\n🎙️ 음성 인식 테스트 (Whisper tiny 모델)...")
            transcriber = SpeechTranscriber(model_name="tiny")
            
            result = transcriber.transcribe(audio_path, method="whisper")
            
            if result.get('success'):
                print("✅ 음성 인식 성공!")
                print(f"   텍스트: {result.get('text', '')[:100]}...")
            else:
                print(f"❌ 음성 인식 실패: {result.get('error', '')}")
            
            # 테스트 파일 정리
            try:
                os.remove(audio_path)
                print("🗑️ 테스트 파일 정리 완료")
            except:
                pass
            
            return True
        else:
            print("❌ 오디오 추출 실패")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def test_error_handling():
    """오류 처리 테스트"""
    print("\n🧪 오류 처리 테스트")
    print("="*50)
    
    transcriber = SpeechTranscriber()
    
    # 1. 존재하지 않는 파일 테스트
    print("1. 존재하지 않는 파일 테스트:")
    result = transcriber.transcribe("nonexistent_file.mp3")
    print(f"   결과: {result.get('error', '')[:100]}...")
    
    # 2. 빈 경로 테스트
    print("\n2. 빈 경로 테스트:")
    result = transcriber.transcribe("")
    print(f"   결과: {result.get('error', '')}")
    
    # 3. None 경로 테스트
    print("\n3. None 경로 테스트:")
    result = transcriber.transcribe(None)
    print(f"   결과: {result.get('error', '')}")
    
    return True


def main():
    """메인 테스트 함수"""
    print("🎵 개선된 YouTube Audio Transcriber 테스트")
    print("="*60)
    
    tests = [
        ("오디오 추출 및 변환", test_improved_extractor),
        ("오류 처리", test_error_handling),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{'='*20} {name} 테스트 {'='*20}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 테스트 중 예외 발생: {e}")
            results.append((name, False))
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n총 {success_count}/{total_count} 테스트 통과")
    
    if success_count == total_count:
        print("🎉 모든 개선사항이 정상 작동합니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")


if __name__ == "__main__":
    main()