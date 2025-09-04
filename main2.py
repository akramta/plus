from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from google import genai
from google.genai import types
import os

app = FastAPI()
templates = Jinja2Templates(directory=os.path.dirname(__file__))

client = genai.Client(api_key="AIzaSyCLuANVl6WdljIO8IPEdxPDW6xtsgWV_Ms")
chat_history = []

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask(question: str = Form(...)):
    from google.genai.types import UserContent, ModelContent, Part

    # إضافة سؤال المستخدم للـ history
    chat_history.append(UserContent(parts=[Part(text=question)]))

    # System instruction لتخصيص التخصص: الطاقة الكهربائية فقط
    system_instruction = """أنت مساعد متخصص في مجال الطاقة الكهربائية ⚡
- أجب فقط على الأسئلة المتعلقة بالطاقة الكهربائية
- أي سؤال خارج هذا المجال: أجب بـ "عذراً! 😊 نحن طلاب متخصصين في مجال الطاقة الكهربائية فقط هل لديك اي سؤال نحن هنا لمساعدتك في اي وقت شكرا ⚡"
- رتب الإجابات بشكل واضح ومفهوم"""

    # إنشاء جلسة محادثة مع history
    chat = client.chats.create(
        model="gemini-2.5-flash",
        history=chat_history,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(
                thinking_budget=200
            )
        )
    )

    # الرد كامل
    resp = chat.send_message(question)

    # إضافة رد البوت للـ history
    chat_history.append(ModelContent(parts=[Part(text=resp.text)]))

    # نعيد الرد كامل، وسيتولى JS عمل streaming حرف حرف
    return JSONResponse({"answer": resp.text})
