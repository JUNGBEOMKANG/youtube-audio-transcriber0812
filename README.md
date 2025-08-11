# YouTube Audio Transcriber 0812 - 글래스모피즘 버전

YouTube URL에서 오디오를 추출하고 텍스트로 변환하는 프로그램 (글래스모피즘 디자인 적용)

## ✨ 새로운 기능 (0812 버전)
- 🎨 **글래스모피즘 UI 디자인** - #8BBDFF-#61DBF0 그라디언트 배경
- 📝 **AI 요약 기능** - 핵심요약 및 큐레이터 탭
- 🌙 **다크 글래스 컴포넌트** - 향상된 가독성
- ⚡ **호버 효과 및 애니메이션** - 물방울 애니메이션, 엠비언트 라이팅
- 📱 **개선된 모바일 반응형 디자인**

## 🎯 주요 기능
- ✅ YouTube URL → 오디오 다운로드 (mp3/wav)
- ✅ 오디오 파일 → 텍스트 변환 (한국어/영어 지원)
- ✅ CLI 및 웹 인터페이스 지원
- ✅ Whisper AI 및 Google Speech Recognition 지원
- ✅ 실시간 진행 상황 표시
- ✅ **NEW**: AI 기반 텍스트 요약 (핵심요약/큐레이터)
- ✅ **NEW**: 모던 글래스모피즘 UI

## 🛠️ 기술 스택
- **Python 3.8+**
- **yt-dlp**: YouTube 다운로드
- **OpenAI Whisper**: 고품질 음성 인식 (오프라인)
- **Google Speech Recognition**: 온라인 음성 인식
- **FastAPI**: 웹 인터페이스
- **FFmpeg**: 오디오 처리
- **Transformers**: AI 텍스트 요약 (Korean T5 모델)

## ⚡ 빠른 시작

### 자동 설치 (권장)
```bash
# 저장소 클론 또는 파일 다운로드 후
cd youtube-audio-transcriber0812

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

### 🌐 웹 인터페이스 (추천)
```bash
# 웹 서버 시작
python app.py

# 브라우저에서 접속
# http://localhost:8000
```

**웹 인터페이스 특징:**
- 🎨 글래스모피즘 디자인으로 현대적인 UI/UX
- 📊 실시간 진행 상황 표시
- 🔧 직관적인 설정 옵션
- 📝 3가지 결과 탭: 전체 스크립트 / 핵심요약 / 큐레이터
- 💾 결과 텍스트 다운로드
- 📱 완전 반응형 디자인

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

# 전체 옵션 보기
python cli.py --help
```

## 🧪 테스트

```bash
# 설치 및 기본 기능 테스트
python test_example.py

# 요약 기능 테스트
python test_summarization.py

# 접근성 테스트
python test_accessibility.py
```

## 📁 프로젝트 구조

```
youtube-audio-transcriber0812/
├── audio_extractor.py      # YouTube 오디오 추출
├── speech_transcriber.py   # 음성-텍스트 변환
├── cli.py                 # CLI 인터페이스
├── app.py                 # 웹 인터페이스 (FastAPI + 요약 기능)
├── static/
│   ├── css/
│   │   └── dashboard.css  # 글래스모피즘 스타일
│   └── js/
│       └── dashboard-components.js  # 모듈화된 JS 컴포넌트
├── templates/
│   └── dashboard.html     # 메인 웹 페이지
├── setup.py              # 자동 설치 스크립트
├── test_*.py             # 각종 테스트 스크립트
├── requirements.txt      # Python 의존성
└── README.md            # 문서
```

## 🎨 글래스모피즘 디자인 특징

- **배경**: #8BBDFF → #61DBF0 그라디언트
- **글래스 효과**: backdrop-filter: blur() 사용
- **엠비언트 라이팅**: 헤더 호버시 조명 효과
- **물방울 애니메이션**: 활성 탭의 스케일 애니메이션
- **다크 글래스**: 텍스트 가독성을 위한 어두운 반투명 배경
- **고곡률 버튼**: 50px 라운드 코너의 현대적 버튼
- **반응형**: 모든 화면 크기에서 완벽한 표시

## 🤖 AI 요약 기능

### 핵심요약 탭
- 각 문단별 핵심 내용을 1-2 문장으로 요약
- 번호가 매겨진 리스트 형태로 제공
- 긴 텍스트의 빠른 파악에 최적화

### 큐레이터 탭
- **제목**: 영상 내용을 가장 잘 나타내는 한 문장
- **한 줄 요약**: 전체 내용의 핵심 압축
- **핵심 포인트**: 3가지 주요 내용 정리
- 30초 안에 영상 핵심을 파악할 수 있도록 설계

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

2. **요약 모델 로딩 실패**
   - 인터넷 연결 확인 (첫 실행시 모델 다운로드)
   - 충분한 디스크 공간 확보 (~500MB)

3. **메모리 부족**
   - 더 작은 Whisper 모델 사용 (tiny, base)
   - 긴 영상의 경우 분할 처리 고려

### 로그 확인
- CLI: 터미널 출력 확인
- 웹: 브라우저 개발자 도구 콘솔 확인
- 서버: Python 실행 터미널에서 실시간 로그 확인

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
- 요약 기능은 한국어 텍스트에 최적화되어 있습니다

## 🔮 향후 계획

- [ ] 더 많은 언어의 요약 모델 지원
- [ ] 타임스탬프 포함 자막 생성
- [ ] 배치 처리 지원 (여러 URL 동시 처리)
- [ ] PWA (Progressive Web App) 지원
- [ ] Docker 컨테이너 지원
- [ ] 클라우드 배포 가이드
