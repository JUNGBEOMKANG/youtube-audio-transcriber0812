"""
YouTube 오디오 추출 모듈
"""
import os
import yt_dlp
from pathlib import Path
from typing import Optional


class YouTubeAudioExtractor:
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_audio(self, url: str, format: str = "mp3") -> Optional[str]:
        """
        YouTube URL에서 오디오 추출
        
        Args:
            url: YouTube URL
            format: 출력 포맷 (mp3, wav)
            
        Returns:
            추출된 오디오 파일 경로
        """
        downloaded_file_path = None
        
        def progress_hook(d):
            nonlocal downloaded_file_path
            if d['status'] == 'finished':
                downloaded_file_path = d['filename']
        
        try:
            # 비디오 제목 가져오기
            info = self._get_video_info_safe(url)
            if not info:
                return None
                
            title = info.get('title', 'Unknown')
            # 안전한 파일명 생성
            safe_title = self._sanitize_filename(title)
            
            # yt-dlp 옵션 설정
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_dir / f'{safe_title}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format,
                    'preferredquality': '192',
                }],
                'noplaylist': True,
                'progress_hooks': [progress_hook],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
                # 후크에서 파일 경로를 받았으면 반환
                if downloaded_file_path and os.path.exists(downloaded_file_path):
                    return downloaded_file_path
                
                # 후크가 실패한 경우 폴더에서 찾기
                return self._find_latest_audio_file(format, safe_title)
                
        except Exception as e:
            print(f"오디오 추출 실패: {e}")
            # 오류가 발생해도 파일이 다운로드되었을 수 있으므로 확인
            try:
                return self._find_latest_audio_file(format)
            except:
                return None
    
    def _get_video_info_safe(self, url: str) -> dict:
        """안전하게 비디오 정보 가져오기"""
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"비디오 정보 가져오기 실패: {e}")
            return {}
    
    def _sanitize_filename(self, filename: str) -> str:
        """파일명에서 특수문자 제거"""
        import re
        # 한글, 영문, 숫자, 공백, 하이픈, 언더스코어만 허용
        safe_name = re.sub(r'[^\w\s\-가-힣]', '', filename)
        # 연속된 공백을 하나로 줄이고 양끝 공백 제거
        safe_name = re.sub(r'\s+', ' ', safe_name).strip()
        # 길이 제한 (200자)
        if len(safe_name) > 200:
            safe_name = safe_name[:200]
        return safe_name or "audio"
    
    def _find_latest_audio_file(self, preferred_format: str, title_hint: str = None) -> Optional[str]:
        """다운로드 폴더에서 최신 오디오 파일 찾기"""
        try:
            audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac']
            audio_files = []
            
            for file_path in self.output_dir.iterdir():
                if file_path.suffix.lower() in audio_extensions:
                    # 제목 힌트가 있으면 우선 매칭
                    if title_hint and title_hint.lower() in file_path.stem.lower():
                        return str(file_path)
                    audio_files.append((file_path.stat().st_mtime, file_path))
            
            if audio_files:
                # 가장 최근 파일 반환
                latest_file = max(audio_files, key=lambda x: x[0])[1]
                return str(latest_file)
            
            return None
        except Exception as e:
            print(f"오디오 파일 검색 실패: {e}")
            return None
    
    def get_video_info(self, url: str) -> dict:
        """비디오 정보 가져오기"""
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0)
                }
        except Exception as e:
            print(f"비디오 정보 가져오기 실패: {e}")
            return {}