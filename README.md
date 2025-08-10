# YouTube Audio Transcriber (YouTube-to-text)

YouTube URL에서 오디오를 추출하고 텍스트로 변환하는 프로그램

## 🎯 주요 기능
- ✅ YouTube URL → 오디오 다운로드 (mp3/wav)
- ✅ 오디오 파일 → 텍스트 변환 (한국어/영어 지원)
- ✅ CLI 및 웹 인터페이스 지원
- ✅ Whisper AI 및 Google Speech Recognition 지원
- ✅ 실시간 진행 상황 표시

## 🛠️ 기술 스택
- **Python 3.8+**
- **yt-dlp**: YouTube 다운로드
- **OpenAI Whisper**: 고품질 음성 인식 (오프라인)
- **Google Speech Recognition**: 온라인 음성 인식
- **FastAPI**: 웹 인터페이스
- **FFmpeg**: 오디오 처리

## ⚡ 빠른 시작

### 자동 설치 (권장)
```bash
# 저장소 클론 또는 파일 다운로드 후
cd youtube-audio-transcriber

# 자동 설치 실행
python setup.py
```

### 수동 설치
```bash
# 1. Python 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Python 패키지 설치
pip install -r requirements.txt

# 4. FFmpeg 설치
# macOS: brew install ffmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# Windows: https://ffmpeg.org/download.html 에서 수동 설치
```

## 📖 사용법

### 🖥️ CLI 모드
```bash
# 기본 사용법
python cli.py "https://youtube.com/watch?v=VIDEO_ID"

# 다양한 옵션
python cli.py "https://youtube.com/watch?v=VIDEO_ID" \
    --format wav \
    --method whisper \
    --model base \
    --output transcript.txt \
    --keep-audio

# 비디오 정보만 확인
python cli.py "https://youtube.com/watch?v=VIDEO_ID" --info-only

# 전체 옵션 보기
python cli.py --help
```

#### CLI 옵션
- `-f, --format`: 오디오 포맷 (mp3, wav)
- `-m, --method`: 음성 인식 방법 (whisper, google, both)
- `--model`: Whisper 모델 크기 (tiny, base, small, medium, large)
- `-o, --output`: 결과 텍스트 파일 경로
- `--keep-audio`: 오디오 파일 유지
- `--info-only`: 비디오 정보만 출력

### 🌐 웹 인터페이스
```bash
# 웹 서버 시작
python app.py

# 브라우저에서 접속
# http://localhost:8000
```

웹 인터페이스 특징:
- 실시간 진행 상황 표시
- 다양한 옵션 설정
- 결과 텍스트 다운로드
- 반응형 디자인

## 🧪 테스트

```bash
# 설치 및 기본 기능 테스트
python test_example.py
```

## 📁 프로젝트 구조

```
youtube-audio-transcriber/
├── audio_extractor.py      # YouTube 오디오 추출
├── speech_transcriber.py   # 음성-텍스트 변환
├── cli.py                 # CLI 인터페이스
├── app.py                 # 웹 인터페이스 (FastAPI)
├── setup.py              # 자동 설치 스크립트
├── test_example.py       # 테스트 스크립트
├── requirements.txt      # Python 의존성
├── README.md            # 문서
└── .gitignore          # Git 무시 파일
```

## ⚙️ 음성 인식 방법 비교

| 방법 | 장점 | 단점 | 권장 사용 |
|------|------|------|----------|
| **Whisper** | 높은 정확도, 오프라인, 다국어 지원 | 처음 로딩 시간, GPU 권장 | 일반적인 용도 |
| **Google** | 빠른 처리, 실시간 지원 | 인터넷 필요, API 제한 | 짧은 오디오 |
| **Both** | 결과 비교 가능 | 처리 시간 2배 | 정확도 검증 필요시 |

## 🎛️ Whisper 모델 선택

| 모델 | 크기 | 처리 속도 | 정확도 | 권장 사용 |
|------|------|----------|---------|----------|
| tiny | ~39MB | 매우 빠름 | 보통 | 빠른 처리 필요시 |
| base | ~142MB | 빠름 | 좋음 | **기본 권장** |
| small | ~483MB | 보통 | 더 좋음 | 품질 중시 |
| medium | ~1.5GB | 느림 | 매우 좋음 | 높은 품질 필요 |
| large | ~2.9GB | 매우 느림 | 최고 | 최고 품질 필요 |

## 🔧 문제 해결

### 일반적인 오류

1. **FFmpeg 관련 오류**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # Windows: https://ffmpeg.org/download.html
   ```

2. **권한 오류 (Linux/macOS)**
   ```bash
   chmod +x cli.py setup.py test_example.py
   ```

3. **메모리 부족**
   - 더 작은 Whisper 모델 사용 (tiny, base)
   - Google Speech Recognition 사용

4. **네트워크 오류**
   - 안정한 인터넷 연결 확인
   - VPN 사용시 비활성화 시도

### 로그 확인
- CLI: 터미널 출력 확인
- 웹: 브라우저 개발자 도구 콘솔 확인

## 🤝 기여

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Create Pull Request

## 📄 라이선스

MIT License

## ⚠️ 주의사항

- YouTube 이용약관을 준수하여 사용하세요
- 저작권이 있는 콘텐츠는 개인적인 용도로만 사용하세요
- 대용량 비디오는 처리 시간이 오래 걸릴 수 있습니다

## 🔮 향후 계획

- [ ] 배치 처리 지원 (여러 URL 동시 처리)
- [ ] 더 많은 언어 지원
- [ ] 타임스탬프 포함 자막 생성
- [ ] Docker 컨테이너 지원
- [ ] 클라우드 배포 가이드
