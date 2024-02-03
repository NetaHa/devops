from fastapi import FastAPI, Depends
from pydantic import BaseModel
import sqlite3
from datetime import timezone, datetime, timedelta
import uvicorn

class Event(BaseModel):
    userid: str
    eventname: str

app = FastAPI()

def get_db_connection():
    return sqlite3.connect('../events.db', check_same_thread=False)

def create_events_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        eventtimestamputc DATETIME,
        userid TEXT,
        eventname TEXT
    )
    ''')
    conn.commit()
    conn.close()

create_events_table()

@app.post("/process_event/")
async def process_event(event: Event, db=Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute('''
    INSERT INTO events (eventtimestamputc, userid, eventname) VALUES (CURRENT_TIMESTAMP, ?, ?)
    ''', (event.userid, event.eventname))
    db.commit()
    db.close()
    return {"message": "Event processed successfully"}

@app.post("/get_reports/")
async def get_reports(lastseconds: int, userid: str, db=Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute('''
    SELECT * FROM events WHERE userid = ? AND eventtimestamputc > DATETIME('now', ?)
    ''', (userid, f'-{lastseconds} seconds'))
    events = cursor.fetchall()
    db.close()

    events_list = [{'eventtimestamputc': event[0], 'userid': event[1], 'eventname': event[2]} for event in events]
    return {"events": events_list}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
