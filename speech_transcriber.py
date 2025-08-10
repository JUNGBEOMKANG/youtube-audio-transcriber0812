"""
음성 텍스트 변환 모듈
"""
import whisper
import speech_recognition as sr
from pathlib import Path
from typing import Optional, Dict
from pydub import AudioSegment
import tempfile
import os


class SpeechTranscriber:
    def __init__(self, model_name: str = "base"):
        """
        Args:
            model_name: Whisper 모델명 (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.whisper_model = None
        self.recognizer = sr.Recognizer()
        
    def load_whisper_model(self):
        """Whisper 모델 로드 (지연 로딩)"""
        if self.whisper_model is None:
            print(f"Whisper {self.model_name} 모델 로드 중...")
            self.whisper_model = whisper.load_model(self.model_name)
    
    def transcribe_with_whisper(self, audio_path: str) -> Dict[str, any]:
        """
        Whisper를 사용한 음성 인식
        
        Args:
            audio_path: 오디오 파일 경로
            
        Returns:
            변환 결과 딕셔너리
        """
        try:
            self.load_whisper_model()
            
            result = self.whisper_model.transcribe(
                audio_path,
                language='ko',  # 한국어 우선, None으로 설정하면 자동 감지
                task='transcribe'
            )
            
            return {
                'text': result['text'].strip(),
                'language': result['language'],
                'segments': result['segments'],
                'success': True,
                'method': 'whisper'
            }
            
        except Exception as e:
            return {
                'text': '',
                'error': str(e),
                'success': False,
                'method': 'whisper'
            }
    
    def transcribe_with_google(self, audio_path: str) -> Dict[str, any]:
        """
        Google Speech Recognition을 사용한 음성 인식
        
        Args:
            audio_path: 오디오 파일 경로
            
        Returns:
            변환 결과 딕셔너리
        """
        try:
            # 오디오 파일을 WAV로 변환 (Google API용)
            audio = AudioSegment.from_file(audio_path)
            
            # 임시 WAV 파일 생성
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                audio.export(tmp_file.name, format='wav')
                wav_path = tmp_file.name
            
            try:
                # Google Speech Recognition
                with sr.AudioFile(wav_path) as source:
                    audio_data = self.recognizer.record(source)
                
                # 한국어 우선, 실패시 영어
                try:
                    text = self.recognizer.recognize_google(audio_data, language='ko-KR')
                except sr.UnknownValueError:
                    text = self.recognizer.recognize_google(audio_data, language='en-US')
                
                return {
                    'text': text,
                    'language': 'ko-KR',
                    'success': True,
                    'method': 'google'
                }
                
            finally:
                # 임시 파일 삭제
                os.unlink(wav_path)
                
        except sr.UnknownValueError:
            return {
                'text': '',
                'error': '음성을 인식할 수 없습니다',
                'success': False,
                'method': 'google'
            }
        except sr.RequestError as e:
            return {
                'text': '',
                'error': f'Google API 오류: {e}',
                'success': False,
                'method': 'google'
            }
        except Exception as e:
            return {
                'text': '',
                'error': str(e),
                'success': False,
                'method': 'google'
            }
    
    def transcribe(self, audio_path: str, method: str = 'whisper') -> Dict[str, any]:
        """
        음성을 텍스트로 변환
        
        Args:
            audio_path: 오디오 파일 경로
            method: 변환 방법 ('whisper', 'google', 'both')
            
        Returns:
            변환 결과
        """
        # 파일 존재 확인 및 상세 정보 제공
        if not audio_path:
            return {
                'text': '',
                'error': '오디오 파일 경로가 제공되지 않았습니다.',
                'success': False
            }
            
        if not os.path.exists(audio_path):
            # 파일이 없는 경우 디렉토리 내용 확인
            directory = os.path.dirname(audio_path)
            if os.path.exists(directory):
                files = [f for f in os.listdir(directory) if f.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg'))]
                file_list = ', '.join(files[:5])  # 처음 5개만 표시
                more_files = f" (그 외 {len(files)-5}개 더)" if len(files) > 5 else ""
                
                return {
                    'text': '',
                    'error': f'파일을 찾을 수 없습니다: {audio_path}\n' + 
                            f'디렉토리 {directory}의 오디오 파일들: {file_list}{more_files}',
                    'success': False
                }
            else:
                return {
                    'text': '',
                    'error': f'파일을 찾을 수 없습니다: {audio_path}\n디렉토리도 존재하지 않습니다: {directory}',
                    'success': False
                }
        
        # 파일 크기 확인
        try:
            file_size = os.path.getsize(audio_path)
            if file_size == 0:
                return {
                    'text': '',
                    'error': f'오디오 파일이 비어있습니다: {audio_path}',
                    'success': False
                }
            print(f"📁 오디오 파일 크기: {file_size / 1024 / 1024:.2f} MB")
        except OSError as e:
            return {
                'text': '',
                'error': f'파일 접근 오류: {audio_path} - {e}',
                'success': False
            }
        
        if method == 'whisper':
            return self.transcribe_with_whisper(audio_path)
        elif method == 'google':
            return self.transcribe_with_google(audio_path)
        elif method == 'both':
            # 두 방법 모두 시도
            whisper_result = self.transcribe_with_whisper(audio_path)
            google_result = self.transcribe_with_google(audio_path)
            
            return {
                'whisper': whisper_result,
                'google': google_result,
                'success': True,
                'method': 'both'
            }
        else:
            return {
                'text': '',
                'error': f'지원하지 않는 방법: {method}',
                'success': False
            }