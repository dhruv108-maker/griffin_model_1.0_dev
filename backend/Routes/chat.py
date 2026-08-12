from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.Dependencies.database_dep import get_db
from backend.Database.models import Chat, Message

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/message")
def send_chat_message(chat_id: str, content: str, db: Session = Depends(get_db)):
    msg = Message(chat_id=chat_id, sender="user", content=content)
    db.add(msg)
    db.commit()
    
    # Store user query and return system acknowledgment
    bot_msg = Message(chat_id=chat_id, sender="assistant", content="Analysis response based on EvidenceGraph context.")
    db.add(bot_msg)
    db.commit()
    
    return {"user_message": msg.content, "response": bot_msg.content}