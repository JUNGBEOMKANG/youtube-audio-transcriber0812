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
import torch
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio
import json

# --- Environment Setup ---
load_dotenv()

# Google Gemini 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
USE_GEMINI_SUMMARY = os.getenv("USE_GEMINI_SUMMARY", "false").lower() == "true"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"🔑 Google Gemini API 설정 완료! (모델: {GEMINI_MODEL})")
else:
    print("⚠️  Gemini API 키가 설정되지 않았습니다. 기존 T5 모델을 사용합니다.")

# --- App Initialization ---
app = FastAPI(
    title="YouTube Audio Transcriber", 
    version="3.1.0",
    description="고품질 AI를 사용한 YouTube 음성-텍스트 변환 및 요약 서비스 (OpenAI 통합)",
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
print("🔄 안정화된 한국어 요약 모델을 로드하는 중입니다...")
try:
    # 안정적인 T5 모델 사용 (긴 텍스트 처리 가능)
    summarizer = pipeline("summarization", 
                         model="eenzeenee/t5-small-korean-summarization",
                         max_length=1024,  # 최대 길이 제한
                         truncation=True)
    print("✅ T5 한국어 요약 모델 로드 완료!")
except Exception as e:
    summarizer = None
    print(f"❌ 요약 모델 로드 실패: {e}")
    print("   요약 기능 없이 애플리케이션을 시작합니다.")


# In-memory job store
jobs = {}

# --- Google Gemini 요약 함수들 ---
async def gemini_summarize_key_points(text: str):
    """Google Gemini를 사용한 핵심요약"""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        prompt = f"""
당신은 전문 텍스트 요약 전문가입니다. 주어진 유튜브 스크립트를 분석하여 각 문단의 핵심 내용을 정확하고 간결하게 요약해주세요.

지시사항:
1. 주어진 텍스트를 자연스러운 문단으로 나누세요
2. 각 문단의 핵심 내용을 1-2 문장으로 요약하세요
3. 결과를 JSON 배열 형태로 반환하세요
4. 각 항목은 "paragraph_summary" 키를 가져야 합니다

텍스트:
{text}

응답 형식 (JSON만 반환):
[
  {{"paragraph_summary": "첫 번째 문단 요약"}},
  {{"paragraph_summary": "두 번째 문단 요약"}},
  ...
]
"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000,
            )
        )
        
        result_text = response.text.strip()
        # JSON 추출 (코드 블록 제거)
        if result_text.startswith('```json'):
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif result_text.startswith('```'):
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        return json.loads(result_text)
    except Exception as e:
        print(f"Gemini 핵심요약 오류: {e}")
        return None

async def gemini_summarize_curator(text: str):
    """Google Gemini를 사용한 큐레이터 요약"""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        prompt = f"""
당신은 전문 콘텐츠 큐레이터입니다. 주어진 유튜브 영상 스크립트를 분석하여 시청자가 30초 안에 핵심을 파악할 수 있도록 요약해주세요.

지시사항:
1. 제목: 영상 내용을 가장 잘 나타내는 매력적인 한 문장 제목
2. 한 줄 요약: 전체 내용을 한 문장으로 압축한 핵심 요약
3. 핵심 포인트: 가장 중요한 3개의 포인트

텍스트:
{text}

응답을 JSON 형태로만 제공해주세요:
{{
  "title": "매력적인 제목",
  "one_line_summary": "전체 내용의 핵심 요약",
  "key_points": ["포인트 1", "포인트 2", "포인트 3"]
}}
"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=1000,
            )
        )
        
        result_text = response.text.strip()
        # JSON 추출
        if result_text.startswith('```json'):
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif result_text.startswith('```'):
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        return json.loads(result_text)
    except Exception as e:
        print(f"Gemini 큐레이터 요약 오류: {e}")
        return None

async def gemini_summarize_timeline(text: str):
    """Google Gemini를 사용한 타임라인 요약"""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        prompt = f"""
당신은 전문 영상 편집자이자 요약 전문가입니다. 주어진 유튜브 스크립트를 시간 흐름에 따라 구간별로 나누어 타임라인 형태로 정리해주세요.

지시사항:
1. 내용의 흐름에 따라 4-8개의 구간으로 나누세요
2. 각 구간에 대해 다음 정보를 제공하세요:
   - timestamp: "X-Y분" 형태의 시간대
   - subtitle: 해당 구간의 핵심 주제 (간결한 제목)
   - summary: 구간 내용의 상세 요약 (2-3문장)
   - keywords: 핵심 키워드 3-5개
   - oneline_summary: 구어체로 한 문장 정리

텍스트:
{text}

응답을 JSON 배열 형태로만 제공해주세요:
[
  {{
    "timestamp": "0-3분",
    "subtitle": "구간 제목",
    "summary": "구간 내용 요약",
    "keywords": ["키워드1", "키워드2", "키워드3"],
    "oneline_summary": "구어체로 한 줄 정리"
  }},
  ...
]
"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5,
                max_output_tokens=2500,
            )
        )
        
        result_text = response.text.strip()
        # JSON 추출
        if result_text.startswith('```json'):
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif result_text.startswith('```'):
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        return json.loads(result_text)
    except Exception as e:
        print(f"Gemini 타임라인 요약 오류: {e}")
        return None

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
    핵심요약 API - OpenAI 우선, T5 백업
    """
    # Google Gemini API 사용 (우선순위)
    if USE_GEMINI_SUMMARY and GEMINI_API_KEY:
        try:
            result = await gemini_summarize_key_points(payload.text)
            if result:
                return JSONResponse(content=result)
        except Exception as e:
            print(f"Gemini 핵심요약 실패, T5로 백업: {e}")
    
    # T5 모델 백업
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
                # 텍스트 길이 제한 (T5 모델 안정성)
                para_truncated = para[:800] if len(para) > 800 else para
                summary = summarizer(para_truncated, 
                                   max_length=120, 
                                   min_length=25, 
                                   do_sample=False,
                                   truncation=True)
                summary_text = summary[0]['summary_text']
            
            if summary_text and len(summary_text.strip()) > 5:
                summaries.append({"paragraph_summary": summary_text.strip()})
                
        return JSONResponse(content=summaries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 처리 중 오류 발생: {str(e)}")


@app.post("/summarize/curator")
async def summarize_curator(payload: SummarizationRequest):
    """
    큐레이터 요약 API - OpenAI 우선, T5 백업
    """
    # Google Gemini API 사용 (우선순위)
    if USE_GEMINI_SUMMARY and GEMINI_API_KEY:
        try:
            result = await gemini_summarize_curator(payload.text)
            if result:
                return JSONResponse(content=result)
        except Exception as e:
            print(f"Gemini 큐레이터 요약 실패, T5로 백업: {e}")
    
    # T5 모델 백업
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
        # T5 모델 안정성을 위한 텍스트 제한
        text_truncated = payload.text[:1000] if len(payload.text) > 1000 else payload.text
        full_summary = summarizer(text_truncated, 
                                max_length=200, 
                                min_length=50, 
                                do_sample=False,
                                truncation=True)[0]['summary_text']
        
        # 제목 생성
        title_text = payload.text[:500]
        title = summarizer(title_text, 
                          max_length=60, 
                          min_length=15, 
                          do_sample=False,
                          truncation=True)[0]['summary_text']

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


@app.post("/summarize/timeline_summary")
async def summarize_timeline(payload: SummarizationRequest):
    """
    타임라인 요약 API - OpenAI 우선, Rule-based 백업
    """
    # Google Gemini API 사용 (우선순위)
    if USE_GEMINI_SUMMARY and GEMINI_API_KEY:
        try:
            result = await gemini_summarize_timeline(payload.text)
            if result:
                return JSONResponse(content=result)
        except Exception as e:
            print(f"Gemini 타임라인 요약 실패, Rule-based로 백업: {e}")
    
    # Rule-based 백업
    try:
        text = payload.text.strip()
        if not text or len(text) < 20:
            return JSONResponse(content=[])
        
        # 텍스트를 문단으로 분할 (더 긴 문단으로)
        paragraphs = []
        sentences = [s.strip() for s in text.split('.') if s.strip() and len(s.strip()) > 15]
        
        # 문장들을 그룹화하여 단락 생성 (약 3-5 문장씩)
        current_paragraph = []
        for sentence in sentences:
            current_paragraph.append(sentence)
            # 문단 길이가 적당하거나 키워드 변화가 감지되면 새 문단 시작
            if len(current_paragraph) >= 4 or len(' '.join(current_paragraph)) > 300:
                paragraphs.append('. '.join(current_paragraph) + '.')
                current_paragraph = []
        
        # 남은 문장들 추가
        if current_paragraph:
            paragraphs.append('. '.join(current_paragraph) + '.')
        
        timeline_sections = []
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 20:  # 너무 짧은 문단 제외
                continue
                
            # 타임스탬프 생성 (대략적으로)
            timestamp = f"{(i * 3) + 1}-{(i + 1) * 3}분"
            
            # 소타이틀 생성 (첫 번째 문장의 핵심 추출)
            first_sentence = paragraph.split('.')[0].strip()
            if len(first_sentence) > 60:
                words = first_sentence.split()[:8]
                subtitle = ' '.join(words) + '...'
            else:
                subtitle = first_sentence
            
            # 단락 요약 (핵심 문장들 선별)
            sentences_in_paragraph = [s.strip() for s in paragraph.split('.') if s.strip()]
            if len(sentences_in_paragraph) > 1:
                # 가장 긴 2-3개 문장을 핵심으로 선택
                important_sentences = sorted(sentences_in_paragraph[:4], key=len, reverse=True)[:2]
                summary = '. '.join(important_sentences) + '.'
            else:
                summary = paragraph
            
            # 키워드 추출 (간단한 방식으로)
            words = paragraph.lower().split()
            # 일반적인 불용어 제거 후 빈도 높은 단어들을 키워드로
            stop_words = {'을', '를', '이', '가', '은', '는', '의', '에', '에서', '으로', '와', '과', '하고', '그리고', '또한', '하지만', '그런데', '그래서', '따라서', '즉', '것', '수', '때', '곳', '등'}
            meaningful_words = [w for w in words if len(w) > 1 and w not in stop_words]
            word_freq = {}
            for word in meaningful_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 빈도수 기준 상위 3-5개 키워드 선택
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:4]
            keyword_list = [kw[0] for kw in keywords if kw[1] > 1]
            
            # 한마디 정리 (구어체로)
            if len(sentences_in_paragraph) > 0:
                key_sentence = sentences_in_paragraph[0]
                if "합니다" in key_sentence or "습니다" in key_sentence:
                    oneline = key_sentence.replace("합니다", "해요").replace("습니다", "예요")
                else:
                    oneline = key_sentence + "라는 얘기에요"
            else:
                oneline = "핵심 내용이에요"
            
            timeline_sections.append({
                "timestamp": timestamp,
                "subtitle": subtitle,
                "summary": summary,
                "keywords": keyword_list,
                "oneline_summary": oneline
            })
        
        return JSONResponse(content=timeline_sections[:8])  # 최대 8개 섹션으로 제한
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"타임라인 요약 처리 중 오류 발생: {str(e)}")


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
    print("📱 http://localhost:8001 에서 접속 가능")
    uvicorn.run(app, host="0.0.0.0", port=8001)