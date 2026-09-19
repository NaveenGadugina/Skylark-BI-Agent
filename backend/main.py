from websockets import Response

from fastapi import FastAPI, HTTPException, Responsefrom monday_client import get_board_items
from data_cleaner import clean_items
import os
from query_router import route_question
from analytics import (
    DEAL_COLUMNS,
    WORK_ORDER_COLUMNS,
    rename_columns,
    deal_summary,
    work_order_summary,
    cross_board_summary,
    deal_pipeline_by_date
)
app = FastAPI(title="Skylark BI Agent")
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_agent import ask_ai

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://skylark-bi-agent-1-hc9a.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"], 
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "running",
        "project": "Skylark BI Agent"
    }


@app.get("/data/deals")
def get_deals():
    board = get_board_items(os.getenv("DEALS_BOARD_ID"))
    return clean_items(board)


@app.get("/data/work-orders")
def get_work_orders():
    board = get_board_items(os.getenv("WORK_ORDERS_BOARD_ID"))
    return clean_items(board)

@app.get("/analytics/deals")
def get_deal_analytics():
    board = get_board_items(os.getenv("DEALS_BOARD_ID"))

    records = clean_items(board)

    records = [
        rename_columns(record, DEAL_COLUMNS)
        for record in records
    ]

    return deal_summary(records)


@app.get("/analytics/work-orders")
def get_work_order_analytics():
    board = get_board_items(os.getenv("WORK_ORDERS_BOARD_ID"))

    records = clean_items(board)

    records = [
        rename_columns(record, WORK_ORDER_COLUMNS)
        for record in records
    ]

    return work_order_summary(records)


class ChatRequest(BaseModel):
    question: str

@app.options("/chat")
def chat_options():
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "https://skylark-bi-agent-1-hc9a.onrender.com",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        route = route_question(request.question)
        
        question_lower = request.question.lower()

        date_pipeline = None

        if route == "deals" and any(word in question_lower for word in [
            "this quarter",
            "this month",
            "this year"
        ]):
            from datetime import date

            today = date.today()

            if "this month" in question_lower:
                start_date = today.replace(day=1)
                end_date = today

            elif "this quarter" in question_lower:
                quarter_start_month = ((today.month - 1) // 3) * 3 + 1
                start_date = today.replace(
                    month=quarter_start_month,
                    day=1
                )
                end_date = today

            else:
                start_date = today.replace(month=1, day=1)
                end_date = today

            deals_board = get_board_items(os.getenv("DEALS_BOARD_ID"))
            deals = clean_items(deals_board)
            deals = [
                rename_columns(record, DEAL_COLUMNS)
                for record in deals
            ]

            date_pipeline = deal_pipeline_by_date(
                deals,
                start_date,
                end_date
            )

        business_data = {}

        if route in ["deals", "both"]:
            deals_board = get_board_items(os.getenv("DEALS_BOARD_ID"))
            deals = clean_items(deals_board)
            deals = [rename_columns(record, DEAL_COLUMNS) for record in deals]

            business_data["deals"] = deal_summary(deals)

        if route in ["work_orders", "both"]:
            work_orders_board = get_board_items(
                os.getenv("WORK_ORDERS_BOARD_ID")
            )
            work_orders = clean_items(work_orders_board)
            work_orders = [
                rename_columns(record, WORK_ORDER_COLUMNS)
                for record in work_orders
            ]

            business_data["work_orders"] = work_order_summary(work_orders)
        if route == "both":
            business_data["cross_board"] = cross_board_summary(
                deals,
                work_orders
            )
        

        if date_pipeline is not None:
           
            business_data["date_pipeline"] = date_pipeline

        try:
            answer = ask_ai(request.question, business_data)
        except Exception as e:
            print("AI error:", str(e))
            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable. Please try again."
            )

        return {
            "question": request.question,
            "route": route,
            "answer": answer
        }
    except Exception as e:
        print("Chat error:", str(e))
        raise HTTPException(
            status_code=500,
            detail="Unable to process the request. Please try again."
        )