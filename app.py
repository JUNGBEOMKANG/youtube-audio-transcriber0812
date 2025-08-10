"""
YouTube Audio Transcriber 웹 애플리케이션
"""
from fastapi import FastAPI, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import asyncio
from pathlib import Path
from audio_extractor import YouTubeAudioExtractor
from speech_transcriber import SpeechTranscriber
import json
import uuid
from datetime import datetime

app = FastAPI(title="YouTube Audio Transcriber", version="1.0.0")

# 전역 객체
extractor = YouTubeAudioExtractor()
transcriber = SpeechTranscriber()

# 작업 상태 저장
jobs = {}


@app.get("/", response_class=HTMLResponse)
async def home():
    """메인 페이지"""
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Audio Transcriber</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .loading { animation: spin 1s linear infinite; }
            @keyframes spin { to { transform: rotate(360deg); } }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
                <h1 class="text-3xl font-bold text-center mb-8 text-gray-800">
                    🎵 YouTube Audio Transcriber
                </h1>
                
                <form id="transcribeForm" class="space-y-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            YouTube URL
                        </label>
                        <input 
                            type="url" 
                            id="url" 
                            name="url" 
                            required
                            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="https://youtube.com/watch?v=..."
                        >
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                오디오 포맷
                            </label>
                            <select id="format" name="format" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                                <option value="mp3">MP3</option>
                                <option value="wav">WAV</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                음성 인식
                            </label>
                            <select id="method" name="method" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                                <option value="whisper">Whisper (로컬)</option>
                                <option value="google">Google (온라인)</option>
                                <option value="both">둘 다</option>
                            </select>
                        </div>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Whisper 모델
                        </label>
                        <select id="model" name="model" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                            <option value="tiny">Tiny (빠름, 낮은 품질)</option>
                            <option value="base" selected>Base (균형)</option>
                            <option value="small">Small (느림, 높은 품질)</option>
                            <option value="medium">Medium (매우 느림)</option>
                            <option value="large">Large (가장 느림, 최고 품질)</option>
                        </select>
                    </div>
                    
                    <button 
                        type="submit" 
                        id="submitBtn"
                        class="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                        변환 시작
                    </button>
                </form>
                
                <div id="status" class="mt-6 hidden">
                    <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
                        <div class="flex items-center">
                            <div class="loading w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full mr-3"></div>
                            <span id="statusText">처리 중...</span>
                        </div>
                    </div>
                </div>
                
                <div id="result" class="mt-6 hidden">
                    <h3 class="text-lg font-semibold mb-4">📝 변환 결과</h3>
                    <div id="resultContent" class="bg-gray-50 border rounded-md p-4"></div>
                    <button 
                        id="downloadBtn" 
                        class="mt-4 bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600"
                    >
                        텍스트 다운로드
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            let currentJobId = null;
            
            document.getElementById('transcribeForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const submitBtn = document.getElementById('submitBtn');
                const statusDiv = document.getElementById('status');
                const resultDiv = document.getElementById('result');
                
                // UI 상태 변경
                submitBtn.disabled = true;
                submitBtn.textContent = '처리 중...';
                statusDiv.classList.remove('hidden');
                resultDiv.classList.add('hidden');
                
                try {
                    // 작업 시작
                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        currentJobId = data.job_id;
                        checkStatus();
                    } else {
                        throw new Error(data.detail);
                    }
                    
                } catch (error) {
                    alert('오류: ' + error.message);
                    resetUI();
                }
            });
            
            async function checkStatus() {
                if (!currentJobId) return;
                
                try {
                    const response = await fetch(`/status/${currentJobId}`);
                    const data = await response.json();
                    
                    document.getElementById('statusText').textContent = data.status;
                    
                    if (data.completed) {
                        if (data.success) {
                            showResult(data.result);
                        } else {
                            alert('변환 실패: ' + data.error);
                        }
                        resetUI();
                    } else {
                        setTimeout(checkStatus, 2000);
                    }
                    
                } catch (error) {
                    alert('상태 확인 오류: ' + error.message);
                    resetUI();
                }
            }
            
            function showResult(result) {
                const resultDiv = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                
                let html = '';
                
                if (result.method === 'both') {
                    html += '<h4 class="font-semibold mb-2">🤖 Whisper 결과:</h4>';
                    html += '<p class="mb-4 whitespace-pre-wrap">' + (result.whisper.text || '변환 실패') + '</p>';
                    html += '<h4 class="font-semibold mb-2">🌐 Google 결과:</h4>';
                    html += '<p class="whitespace-pre-wrap">' + (result.google.text || '변환 실패') + '</p>';
                } else {
                    html += '<p class="whitespace-pre-wrap">' + (result.text || '변환 실패') + '</p>';
                    if (result.language) {
                        html += '<p class="mt-2 text-sm text-gray-600">언어: ' + result.language + '</p>';
                    }
                }
                
                resultContent.innerHTML = html;
                resultDiv.classList.remove('hidden');
                
                // 다운로드 버튼 이벤트
                document.getElementById('downloadBtn').onclick = () => downloadResult(result);
            }
            
            function downloadResult(result) {
                let text = '';
                
                if (result.method === 'both') {
                    text += 'Whisper 결과:\\n';
                    text += (result.whisper.text || '변환 실패') + '\\n\\n';
                    text += 'Google 결과:\\n';
                    text += (result.google.text || '변환 실패');
                } else {
                    text = result.text || '변환 실패';
                }
                
                const blob = new Blob([text], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'transcript.txt';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
            
            function resetUI() {
                const submitBtn = document.getElementById('submitBtn');
                const statusDiv = document.getElementById('status');
                
                submitBtn.disabled = false;
                submitBtn.textContent = '변환 시작';
                statusDiv.classList.add('hidden');
                currentJobId = null;
            }
        </script>
    </body>
    </html>
    """


@app.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    format: str = Form("mp3"),
    method: str = Form("whisper"), 
    model: str = Form("base")
):
    """음성 변환 작업 시작"""
    
    # YouTube URL 검증
    if 'youtube.com' not in url and 'youtu.be' not in url:
        raise HTTPException(status_code=400, detail="유효한 YouTube URL을 입력해주세요")
    
    # 작업 ID 생성
    job_id = str(uuid.uuid4())
    
    # 작업 상태 초기화
    jobs[job_id] = {
        'status': '비디오 정보 확인 중...',
        'completed': False,
        'success': False,
        'result': None,
        'error': None,
        'created_at': datetime.now()
    }
    
    # 백그라운드 작업 시작
    background_tasks.add_task(process_transcription, job_id, url, format, method, model)
    
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """작업 상태 확인"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    return jobs[job_id]


async def process_transcription(job_id: str, url: str, format: str, method: str, model: str):
    """백그라운드 음성 변환 처리"""
    try:
        # 비디오 정보 확인
        jobs[job_id]['status'] = '비디오 정보 확인 중...'
        video_info = extractor.get_video_info(url)
        
        if not video_info:
            jobs[job_id].update({
                'completed': True,
                'success': False,
                'error': '비디오 정보를 가져올 수 없습니다'
            })
            return
        
        # 오디오 추출
        jobs[job_id]['status'] = f'오디오 추출 중... ({format})'
        audio_path = extractor.extract_audio(url, format)
        
        if not audio_path:
            jobs[job_id].update({
                'completed': True,
                'success': False,
                'error': '오디오 추출에 실패했습니다'
            })
            return
        
        # 음성 인식
        jobs[job_id]['status'] = f'음성 인식 중... ({method})'
        transcriber_instance = SpeechTranscriber(model_name=model)
        result = transcriber_instance.transcribe(audio_path, method=method)
        
        # 오디오 파일 정리
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        if result.get('success', False):
            jobs[job_id].update({
                'status': '변환 완료!',
                'completed': True,
                'success': True,
                'result': result
            })
        else:
            jobs[job_id].update({
                'completed': True,
                'success': False,
                'error': result.get('error', '알 수 없는 오류')
            })
            
    except Exception as e:
        jobs[job_id].update({
            'completed': True,
            'success': False,
            'error': str(e)
        })


if __name__ == "__main__":
    print("🚀 YouTube Audio Transcriber 웹 서버 시작")
    print("📱 http://localhost:8000 에서 접속 가능")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)