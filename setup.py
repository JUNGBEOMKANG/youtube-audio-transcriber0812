#!/usr/bin/env python3
"""
YouTube Audio Transcriber 설치 스크립트
"""
import subprocess
import sys
import os
import platform


def run_command(command, description):
    """명령어 실행"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패: {e.stderr}")
        return False


def check_python_version():
    """Python 버전 확인"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} 감지됨")


def install_system_dependencies():
    """시스템 의존성 설치"""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("🍎 macOS 감지됨")
        if not run_command("which brew", "Homebrew 확인"):
            print("❌ Homebrew가 설치되어 있지 않습니다.")
            print("https://brew.sh/ 에서 Homebrew를 먼저 설치해주세요.")
            return False
        
        return run_command("brew install ffmpeg", "FFmpeg 설치 (Homebrew)")
        
    elif system == "linux":
        print("🐧 Linux 감지됨")
        # Ubuntu/Debian
        if run_command("which apt", "APT 패키지 매니저 확인"):
            return run_command("sudo apt update && sudo apt install -y ffmpeg", "FFmpeg 설치 (APT)")
        # CentOS/RHEL
        elif run_command("which yum", "YUM 패키지 매니저 확인"):
            return run_command("sudo yum install -y ffmpeg", "FFmpeg 설치 (YUM)")
        else:
            print("⚠️ 지원되지 않는 Linux 배포판입니다. FFmpeg를 수동으로 설치해주세요.")
            return False
            
    elif system == "windows":
        print("🪟 Windows 감지됨")
        print("⚠️ Windows에서는 FFmpeg를 수동으로 설치해야 합니다.")
        print("1. https://ffmpeg.org/download.html 에서 FFmpeg 다운로드")
        print("2. PATH 환경변수에 ffmpeg.exe 경로 추가")
        input("FFmpeg 설치 완료 후 Enter를 눌러주세요...")
        return True
    
    return False


def create_virtual_environment():
    """가상환경 생성"""
    if os.path.exists("venv"):
        print("✅ 가상환경이 이미 존재합니다.")
        return True
    
    return run_command(f"{sys.executable} -m venv venv", "가상환경 생성")


def install_python_dependencies():
    """Python 의존성 설치"""
    # 가상환경의 pip 경로 결정
    if platform.system().lower() == "windows":
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # pip 업그레이드
    if not run_command(f"{pip_path} install --upgrade pip", "pip 업그레이드"):
        return False
    
    # 의존성 설치
    if not run_command(f"{pip_path} install -r requirements.txt", "Python 패키지 설치"):
        return False
    
    return True


def test_installation():
    """설치 테스트"""
    print("\n🧪 설치 테스트 중...")
    
    # 가상환경의 python 경로
    if platform.system().lower() == "windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    # 테스트 스크립트
    test_code = '''
import yt_dlp
import whisper
import speech_recognition as sr
from pydub import AudioSegment
print("✅ 모든 라이브러리 로드 성공!")
'''
    
    try:
        result = subprocess.run([python_path, "-c", test_code], 
                              capture_output=True, text=True, check=True)
        print("✅ 설치 테스트 성공!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 설치 테스트 실패: {e.stderr}")
        return False


def main():
    print("🎵 YouTube Audio Transcriber 설치")
    print("="*50)
    
    # 스크립트 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📂 작업 디렉토리: {script_dir}")
    
    # Python 버전 확인
    check_python_version()
    
    # 시스템 의존성 설치
    if not install_system_dependencies():
        print("❌ 시스템 의존성 설치 실패")
        sys.exit(1)
    
    # 가상환경 생성
    if not create_virtual_environment():
        print("❌ 가상환경 생성 실패")
        sys.exit(1)
    
    # Python 의존성 설치
    if not install_python_dependencies():
        print("❌ Python 패키지 설치 실패")
        sys.exit(1)
    
    # 설치 테스트
    if not test_installation():
        print("❌ 설치 테스트 실패")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("🎉 설치 완료!")
    print("\n사용법:")
    print("1. CLI 모드:")
    if platform.system().lower() == "windows":
        print("   venv\\Scripts\\python cli.py \"YOUTUBE_URL\"")
    else:
        print("   venv/bin/python cli.py \"YOUTUBE_URL\"")
    
    print("\n2. 웹 인터페이스:")
    if platform.system().lower() == "windows":
        print("   venv\\Scripts\\python app.py")
    else:
        print("   venv/bin/python app.py")
    print("   브라우저에서 http://localhost:8000 접속")


if __name__ == "__main__":
    main()