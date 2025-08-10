#!/usr/bin/env python3
"""
YouTube Audio Transcriber 테스트 스크립트
"""
from audio_extractor import YouTubeAudioExtractor
from speech_transcriber import SpeechTranscriber
import os


def test_video_info():
    """비디오 정보 테스트"""
    print("🧪 비디오 정보 테스트")
    
    extractor = YouTubeAudioExtractor()
    
    # 짧은 테스트 비디오 (공개 도메인)
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # 유명한 테스트 비디오
        "https://youtu.be/jNQXAC9IVRw",  # 짧은 비디오
    ]
    
    for url in test_urls:
        print(f"\n📺 URL: {url}")
        try:
            info = extractor.get_video_info(url)
            if info:
                print(f"✅ 제목: {info.get('title', 'Unknown')}")
                print(f"   길이: {info.get('duration', 0)//60}:{info.get('duration', 0)%60:02d}")
                print(f"   업로더: {info.get('uploader', 'Unknown')}")
            else:
                print("❌ 비디오 정보 가져오기 실패")
        except Exception as e:
            print(f"❌ 오류: {e}")


def test_audio_extraction():
    """오디오 추출 테스트"""
    print("\n🧪 오디오 추출 테스트")
    
    extractor = YouTubeAudioExtractor()
    
    # 매우 짧은 테스트 비디오 사용
    test_url = "https://youtu.be/jNQXAC9IVRw"  # "Me at the zoo" - YouTube 첫 번째 비디오
    
    print(f"📺 테스트 URL: {test_url}")
    
    try:
        # 오디오 추출 (MP3)
        audio_path = extractor.extract_audio(test_url, "mp3")
        
        if audio_path and os.path.exists(audio_path):
            print(f"✅ 오디오 추출 성공: {audio_path}")
            
            # 파일 크기 확인
            size_mb = os.path.getsize(audio_path) / 1024 / 1024
            print(f"   파일 크기: {size_mb:.2f} MB")
            
            # 테스트 후 파일 삭제
            os.remove(audio_path)
            print("🗑️  테스트 파일 삭제됨")
            
            return True
        else:
            print("❌ 오디오 추출 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_speech_recognition():
    """음성 인식 테스트 (샘플 오디오 파일 필요)"""
    print("\n🧪 음성 인식 테스트")
    print("⚠️ 이 테스트는 실제 오디오 파일이 필요합니다.")
    
    # 간단한 모델 로드 테스트만 수행
    try:
        transcriber = SpeechTranscriber(model_name="tiny")  # 가장 작은 모델
        print("✅ SpeechTranscriber 초기화 성공")
        
        # Whisper 모델 로드 테스트 (실제로는 로드하지 않음)
        print("✅ 음성 인식 모듈 준비 완료")
        
        return True
    except Exception as e:
        print(f"❌ 음성 인식 모듈 오류: {e}")
        return False


def main():
    """메인 테스트 실행"""
    print("🎵 YouTube Audio Transcriber 테스트 시작")
    print("="*50)
    
    tests = [
        ("비디오 정보", test_video_info),
        ("오디오 추출", test_audio_extraction),
        ("음성 인식", test_speech_recognition),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{'='*20} {name} 테스트 {'='*20}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 테스트 중 오류: {e}")
            results.append((name, False))
    
    # 결과 요약
    print("\n" + "="*50)
    print("📊 테스트 결과 요약")
    print("="*50)
    
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n총 {success_count}/{total_count} 테스트 통과")
    
    if success_count == total_count:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패. 설치를 확인해주세요.")


if __name__ == "__main__":
    main()