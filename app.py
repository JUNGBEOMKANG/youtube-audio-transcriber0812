"""
YouTube Audio Transcriber 웹 애플리케이션
"""
from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from audio_extractor import YouTubeAudioExtractor
from speech_transcriber import SpeechTranscriber
import uuid
from datetime import datetime
from transformers import pipeline
from pydantic import BaseModel

# --- App Initialization ---
app = FastAPI(
    title="YouTube Audio Transcriber", 
    version="3.0.0",
    description="고품질 AI를 사용한 YouTube 음성-텍스트 변환 및 요약 서비스",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# --- Static Files and Templates ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Global Objects ---
extractor = YouTubeAudioExtractor()
transcriber = SpeechTranscriber()

# Load summarization model at startup
print("🔄 요약 모델을 로드하는 중입니다. 잠시 기다려주세요...")
try:
    summarizer = pipeline("summarization", model="eenzeenee/t5-small-korean-summarization")
    print("✅ 요약 모델 로드 완료!")
except Exception as e:
    summarizer = None
    print(f"❌ 요약 모델 로드 실패: {e}")
    print("   요약 기능 없이 애플리케이션을 시작합니다.")


# In-memory job store
jobs = {}

# --- Pydantic Models ---
class SummarizationRequest(BaseModel):
    text: str

# --- HTML Routes ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지 - 개선된 접근성과 모듈화된 컴포넌트"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

# --- API Routes ---
@app.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    format: str = Form("mp3"),
    method: str = Form("whisper"), 
    model: str = Form("base")
):
    """음성 변환 작업 시작"""
    if 'youtube.com' not in url and 'youtu.be' not in url:
        raise HTTPException(status_code=400, detail="유효한 YouTube URL을 입력해주세요")
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        'status': '비디오 정보 확인 중...', 
        'completed': False,
        'success': False,
        'result': None,
        'error': None,
        'created_at': datetime.now()
    }
    
    background_tasks.add_task(process_transcription, job_id, url, format, method, model)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """작업 상태 확인"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    return jobs[job_id]

@app.post("/summarize/key_summary")
async def summarize_key_points(payload: SummarizationRequest):
    """
    당신은 텍스트 요약 전문가입니다. 주어진 유튜브 스크립트의 각 문단을 정확하고
    간결하게 요약하는 임무를 받았습니다.
    
    요청:
    1. "변환결과"에 있는 각 문단(줄바꿈으로 구분)을 분석하세요.
    2. 각 문단의 핵심 내용을 담아 한국어로 1~2 문장으로 요약하세요.
    3. 전체 결과를 JSON 배열 형태로 반환해 주세요.
    """
    if not summarizer:
        # Use simple rule-based summarization if model is not available
        try:
            # Split by double newlines first, then by single newlines if no double newlines
            paragraphs = payload.text.split('\n\n')
            if len(paragraphs) == 1:
                paragraphs = [p.strip() for p in payload.text.split('\n') if p.strip() and len(p.strip()) > 10]
            else:
                paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            summaries = []
            for para in paragraphs:
                if len(para.strip()) < 30:  # 너무 짧은 문단은 그냥 사용
                    summary_text = para.strip()
                else:
                    # Simple extractive summarization: take first and most important sentences
                    sentences = [s.strip() for s in para.split('.') if s.strip()]
                    if len(sentences) <= 2:
                        summary_text = para.strip()
                    else:
                        # Take first sentence and longest sentence (likely contains key info)
                        first_sentence = sentences[0] + '.'
                        longest_sentence = max(sentences[1:], key=len, default='') + ('.' if sentences[1:] else '')
                        summary_text = first_sentence + (f' {longest_sentence}' if longest_sentence and longest_sentence != '.' else '')
                
                if summary_text and len(summary_text.strip()) > 5:
                    summaries.append({"paragraph_summary": summary_text.strip()})
            
            return JSONResponse(content=summaries)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"요약 처리 중 오류 발생: {str(e)}")

    try:
        # Split by double newlines first, then by single newlines if needed
        paragraphs = payload.text.split('\n\n')
        if len(paragraphs) == 1:
            paragraphs = [p.strip() for p in payload.text.split('\n') if p.strip() and len(p.strip()) > 10]
        else:
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
        summaries = []
        for para in paragraphs:
            if len(para) < 50:  # 너무 짧은 문단은 그냥 사용
                summary_text = para
            else:
                summary = summarizer(para, max_length=100, min_length=20, do_sample=False)
                summary_text = summary[0]['summary_text']
            
            if summary_text and len(summary_text.strip()) > 5:
                summaries.append({"paragraph_summary": summary_text.strip()})
                
        return JSONResponse(content=summaries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 처리 중 오류 발생: {str(e)}")


@app.post("/summarize/curator")
async def summarize_curator(payload: SummarizationRequest):
    """
    당신은 전문 콘텐츠 큐레이터입니다. 아래 텍스트를 분석하여 시청자가 영상의
    핵심 내용을 30초 안에 파악할 수 있도록, 다음 형식에 맞춰 최종 요약본을 생성해
    주세요.
    
    요청 형식:
    - 제목: 영상 내용을 가장 잘 나타내는 한 문장 제목
    - 한 줄 요약: 전체 내용을 한 문장으로 압축한 요약
    - 핵심 포인트:
      - (핵심 내용 1)
      - (핵심 내용 2)
      - (핵심 내용 3)
    """
    if not summarizer:
        # Use simple rule-based approach if model is not available
        try:
            text = payload.text.strip()
            sentences = [s.strip() for s in text.split('.') if s.strip() and len(s.strip()) > 10]
            
            # Generate title from first meaningful sentence or first few words
            if sentences:
                title_candidate = sentences[0]
                if len(title_candidate) > 100:
                    # Take first part if too long
                    words = title_candidate.split()[:10]
                    title = ' '.join(words) + ('...' if len(words) == 10 else '')
                else:
                    title = title_candidate
            else:
                title = "YouTube 영상 요약"
            
            # Generate one line summary from longest sentences
            if len(sentences) >= 2:
                summary_candidates = sorted(sentences[:5], key=len, reverse=True)[:2]
                one_line_summary = '. '.join(summary_candidates) + '.'
            else:
                one_line_summary = sentences[0] if sentences else "영상 내용 요약"
            
            # Extract key points from longest/most informative sentences
            if len(sentences) >= 3:
                key_point_candidates = sorted(sentences, key=len, reverse=True)[:3]
                key_points = [point + ('.' if not point.endswith('.') else '') for point in key_point_candidates]
            else:
                key_points = [s + ('.' if not s.endswith('.') else '') for s in sentences[:3]]
                
            # Ensure we have at least something
            if not key_points:
                key_points = ["영상의 주요 내용을 다룹니다."]

            curated_summary = {
                "title": title,
                "one_line_summary": one_line_summary,
                "key_points": key_points
            }
            return JSONResponse(content=curated_summary)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"큐레이션 처리 중 오류 발생: {str(e)}")

    try:
        # 전체 텍스트 요약
        full_summary = summarizer(payload.text, max_length=256, min_length=50, do_sample=False)[0]['summary_text']
        
        # 제목 생성 (첫 문장을 활용)
        title_text = payload.text[:500]  # Use first 500 chars for title generation
        title = summarizer(title_text, max_length=60, min_length=15, do_sample=False)[0]['summary_text']

        # 핵심 포인트 추출 - 개선된 방법
        sentences = [s.strip() for s in payload.text.split('.') if s.strip() and len(s.strip()) > 20]
        
        # Get meaningful sentences for key points
        if len(sentences) >= 3:
            # Sort by length and take diverse content
            key_point_candidates = sorted(sentences, key=len, reverse=True)[:6]
            # Select 3 most diverse points
            key_points = []
            for candidate in key_point_candidates:
                if len(key_points) >= 3:
                    break
                # Avoid very similar points
                is_similar = False
                for existing in key_points:
                    if len(set(candidate.split()) & set(existing.split())) > len(candidate.split()) * 0.5:
                        is_similar = True
                        break
                if not is_similar:
                    key_points.append(candidate + ('.' if not candidate.endswith('.') else ''))
        else:
            key_points = [s + ('.' if not s.endswith('.') else '') for s in sentences[:3]]
            
        # Ensure we have at least something
        if not key_points:
            key_points = ["영상의 주요 내용을 다룹니다."]

        curated_summary = {
            "title": title,
            "one_line_summary": full_summary,
            "key_points": key_points
        }
        return JSONResponse(content=curated_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"큐레이션 처리 중 오류 발생: {str(e)}")


# --- Background Task ---
async def process_transcription(job_id: str, url: str, format: str, method: str, model: str):
    """백그라운드 음성 변환 처리"""
    try:
        jobs[job_id]['status'] = '비디오 정보 확인 중...'
        video_info = extractor.get_video_info(url)
        if not video_info:
            raise Exception('비디오 정보를 가져올 수 없습니다')

        jobs[job_id]['status'] = f'오디오 추출 중... ({format})'
        audio_path = extractor.extract_audio(url, format)
        if not audio_path:
            raise Exception('오디오 추출에 실패했습니다')

        jobs[job_id]['status'] = f'음성 인식 중... ({method})'
        transcriber_instance = SpeechTranscriber(model_name=model)
        result = transcriber_instance.transcribe(audio_path, method=method)
        
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
            raise Exception(result.get('error', '알 수 없는 오류'))
            
    except Exception as e:
        jobs[job_id].update({
            'completed': True,
            'success': False,
            'error': str(e)
        })

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 YouTube Audio Transcriber 웹 서버 시작")
    print("📱 http://localhost:8000 에서 접속 가능")
    uvicorn.run(app, host="0.0.0.0", port=8000)