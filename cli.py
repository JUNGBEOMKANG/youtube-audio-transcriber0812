#!/usr/bin/env python3
"""
YouTube Audio Transcriber CLI
"""
import argparse
import sys
import os
from pathlib import Path
import json
from audio_extractor import YouTubeAudioExtractor
from speech_transcriber import SpeechTranscriber


def main():
    parser = argparse.ArgumentParser(description='YouTube 오디오를 텍스트로 변환')
    parser.add_argument('url', help='YouTube URL')
    parser.add_argument('-f', '--format', default='mp3', choices=['mp3', 'wav'], 
                       help='오디오 포맷 (기본: mp3)')
    parser.add_argument('-m', '--method', default='whisper', 
                       choices=['whisper', 'google', 'both'],
                       help='음성 인식 방법 (기본: whisper)')
    parser.add_argument('-o', '--output', help='결과 텍스트 파일 경로')
    parser.add_argument('--model', default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper 모델 크기 (기본: base)')
    parser.add_argument('--keep-audio', action='store_true',
                       help='오디오 파일 유지 (기본: 삭제)')
    parser.add_argument('--info-only', action='store_true',
                       help='비디오 정보만 출력')
    
    args = parser.parse_args()
    
    # YouTube URL 검증
    if 'youtube.com' not in args.url and 'youtu.be' not in args.url:
        print("❌ 유효한 YouTube URL을 입력해주세요.")
        sys.exit(1)
    
    print("🔍 YouTube 비디오 정보 확인 중...")
    
    # 오디오 추출기 초기화
    extractor = YouTubeAudioExtractor()
    
    # 비디오 정보 가져오기
    video_info = extractor.get_video_info(args.url)
    if not video_info:
        print("❌ 비디오 정보를 가져올 수 없습니다.")
        sys.exit(1)
    
    print(f"📺 제목: {video_info.get('title', 'Unknown')}")
    print(f"👤 업로더: {video_info.get('uploader', 'Unknown')}")
    print(f"⏱️  길이: {video_info.get('duration', 0)//60}분 {video_info.get('duration', 0)%60}초")
    print(f"👀 조회수: {video_info.get('view_count', 0):,}")
    
    if args.info_only:
        return
    
    print(f"\n🎵 오디오 추출 중 ({args.format})...")
    
    # 오디오 추출
    audio_path = extractor.extract_audio(args.url, args.format)
    if not audio_path:
        print("❌ 오디오 추출에 실패했습니다.")
        sys.exit(1)
    
    print(f"✅ 오디오 추출 완료: {audio_path}")
    
    # 음성 인식
    print(f"\n🎙️  음성 인식 시작 ({args.method})...")
    transcriber = SpeechTranscriber(model_name=args.model)
    
    result = transcriber.transcribe(audio_path, method=args.method)
    
    if not result.get('success', False):
        print(f"❌ 음성 인식 실패: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    # 결과 출력
    print("\n" + "="*50)
    print("📝 변환 결과")
    print("="*50)
    
    if args.method == 'both':
        print("\n🤖 Whisper 결과:")
        print(result['whisper'].get('text', '변환 실패'))
        print(f"언어: {result['whisper'].get('language', 'Unknown')}")
        
        print("\n🌐 Google 결과:")
        print(result['google'].get('text', '변환 실패'))
    else:
        print(f"\n{result.get('text', '변환 실패')}")
        if 'language' in result:
            print(f"\n언어: {result['language']}")
    
    # 결과 파일 저장
    if args.output:
        output_path = args.output
    else:
        # 기본 출력 파일명 생성
        safe_title = "".join(c for c in video_info.get('title', 'transcript') 
                           if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_path = f"{safe_title}_transcript.txt"
    
    # 텍스트 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"YouTube 비디오: {video_info.get('title', 'Unknown')}\n")
        f.write(f"URL: {args.url}\n")
        f.write(f"변환 방법: {args.method}\n")
        f.write("="*50 + "\n\n")
        
        if args.method == 'both':
            f.write("Whisper 결과:\n")
            f.write(result['whisper'].get('text', '변환 실패') + "\n\n")
            f.write("Google 결과:\n")
            f.write(result['google'].get('text', '변환 실패') + "\n")
        else:
            f.write(result.get('text', '변환 실패'))
    
    print(f"\n💾 결과 저장됨: {output_path}")
    
    # 오디오 파일 정리
    if not args.keep_audio and os.path.exists(audio_path):
        os.remove(audio_path)
        print(f"🗑️  오디오 파일 삭제됨: {audio_path}")
    
    print("\n✨ 변환 완료!")


if __name__ == '__main__':
    main()