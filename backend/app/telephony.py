"""Twilio PSTN webhook adapter (speech gather -> local Ollama -> TwiML).
Twilio handles carrier/audio transport; all conversational LLM inference stays local.
"""
from fastapi import APIRouter,Request,HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from uuid import UUID
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse, Gather
from .config import settings
from .db import SessionLocal
from .models import Tenant,CallSession,CallMessage
from .rag import embed_query,ollama_chat,build_context
from .models import KnowledgeChunk
from sqlalchemy import desc

router=APIRouter(prefix="/voice",tags=["telephony"])

def xml(response:VoiceResponse):
    return Response(str(response),media_type="application/xml")

async def validate_twilio(request:Request):
    if not settings.twilio_auth_token:
        if settings.twilio_validate_signature:
            raise HTTPException(503,"Twilio signature validation configured but token missing")
        return
    signature=request.headers.get("X-Twilio-Signature","")
    url=str(request.url)
    form=dict(await request.form())
    validator=RequestValidator(settings.twilio_auth_token)
    if not validator.validate(url,form,signature):
        raise HTTPException(403,"Invalid Twilio signature")

@router.post("/twilio/{tenant_id}")
async def inbound(tenant_id:UUID,request:Request):
    await validate_twilio(request)
    form=await request.form()
    caller=str(form.get("From",""))[:40]
    response=VoiceResponse()
    async with SessionLocal() as db:
        tenant=await db.get(Tenant,tenant_id)
        if not tenant: raise HTTPException(404,"Tenant not found")
        call=CallSession(tenant_id=tenant_id,caller_number=caller,status="active")
        db.add(call); await db.commit(); await db.refresh(call)
    response.say(f"Thank you for calling {tenant.name}. How may I help you?",voice=settings.twilio_voice,language=settings.twilio_language)
    gather=Gather(input="speech",action=f"{settings.public_base_url}/voice/twilio/{tenant_id}/turn/{call.id}",method="POST",
                  speech_timeout="auto",timeout=7,language=settings.twilio_language)
    response.append(gather); response.say("I did not hear anything. Please call again.",voice=settings.twilio_voice,language=settings.twilio_language)
    response.hangup()
    return xml(response)

@router.post("/twilio/{tenant_id}/turn/{call_id}")
async def turn(tenant_id:UUID,call_id:UUID,request:Request):
    await validate_twilio(request)
    form=await request.form(); utterance=str(form.get("SpeechResult","")).strip()
    response=VoiceResponse()
    if not utterance:
        response.say("Sorry, I could not understand that.",voice=settings.twilio_voice,language=settings.twilio_language)
    else:
        async with SessionLocal() as db:
            call=await db.scalar(select(CallSession).where(CallSession.id==call_id,CallSession.tenant_id==tenant_id))
            if not call: raise HTTPException(404,"Call not found")
            vector=embed_query(utterance)
            chunks=(await db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.tenant_id==tenant_id,KnowledgeChunk.embedding.is_not(None)).order_by(KnowledgeChunk.embedding.cosine_distance(vector)).limit(4))).all()
            context=build_context([c.content for c in chunks])
            history=(await db.scalars(select(CallMessage).where(CallMessage.tenant_id==tenant_id,CallMessage.session_id==call_id).order_by(desc(CallMessage.created_at)).limit(10))).all()
            msgs=[{"role":"system","content":"You are a concise, courteous phone receptionist. Answer only from business context. If information is missing, offer a staff callback. Keep spoken answers under 2 sentences. Context:\n"+context}]
            msgs += [{"role":m.role,"content":m.content} for m in reversed(history)]
            msgs.append({"role":"user","content":utterance})
            answer=await ollama_chat(msgs)
            db.add_all([CallMessage(tenant_id=tenant_id,session_id=call_id,role="user",content=utterance),CallMessage(tenant_id=tenant_id,session_id=call_id,role="assistant",content=answer)])
            await db.commit()
        response.say(answer,voice=settings.twilio_voice,language=settings.twilio_language)
    gather=Gather(input="speech",action=f"{settings.public_base_url}/voice/twilio/{tenant_id}/turn/{call_id}",method="POST",speech_timeout="auto",timeout=7,language=settings.twilio_language)
    response.append(gather); response.say("Thank you for calling. Goodbye.",voice=settings.twilio_voice,language=settings.twilio_language); response.hangup()
    return xml(response)

@router.post("/twilio/{tenant_id}/status")
async def status(tenant_id:UUID,request:Request):
    await validate_twilio(request)
    form=await request.form(); sid=str(form.get("CallSid","")); state=str(form.get("CallStatus",""))
    # Provider status callback is accepted for observability; correlate by caller and timestamp in future.
    return Response("ok",media_type="text/plain")
