"""아이디어 회로 — original cloud fairy, guided idea development, and reflective tarot."""
import base64
import html
import json
import os
import random
import re
from datetime import datetime
from pathlib import Path

import streamlit as st
from google import genai

BASE = Path(__file__).resolve().parent
st.set_page_config(page_title="아이디어 회로 | Idea Circuit", page_icon="☁️", layout="wide")

MODES = {
    "logic": {"ko": "논리회로", "en": "Logic Circuit", "emoji": "🔍", "ko_desc": "아이디어는 있지만 설득력이 부족해요 · 필요성과 근거를 탄탄하게", "en_desc": "I have an idea, but need stronger reasons and evidence"},
    "creative": {"ko": "발상회로", "en": "Ideation Circuit", "emoji": "✨", "ko_desc": "아직 아이디어가 막연해요 · 새로운 가능성을 발견하기", "en_desc": "My idea is still vague; help me discover possibilities"},
    "fusion": {"ko": "구체화 회로", "en": "Development Circuit", "emoji": "🧩", "ko_desc": "방향과 근거는 있지만 실행 방법이 막막해요", "en_desc": "I know the direction but need an actionable plan"},
}
CARDS = [
    ("00_fool.png", "The Fool", "바보", "새로운 시작과 열린 가능성"),
    ("01_magician.png", "The Magician", "마법사", "자원과 실행의 힘"),
    ("02_high_priestess.png", "The High Priestess", "여사제", "직관과 내면의 질문"),
    ("03_empress.png", "The Empress", "여황제", "성장과 돌봄"),
    ("04_emperor.png", "The Emperor", "황제", "구조와 책임"),
    ("05_hierophant.png", "The Hierophant", "교황", "배움과 관습"),
    ("06_lovers.png", "The Lovers", "연인", "가치와 선택"),
    ("07_chariot.png", "The Chariot", "전차", "방향과 추진력"),
    ("08_strength.png", "Strength", "힘", "용기와 인내"),
    ("09_hermit.png", "The Hermit", "은둔자", "성찰과 탐색"),
    ("10_wheel_of_fortune.png", "Wheel of Fortune", "운명의 수레바퀴", "변화와 기회"),
    ("11_justice.png", "Justice", "정의", "균형과 근거"),
    ("12_hanged_man.png", "The Hanged Man", "매달린 사람", "관점의 전환"),
    ("13_death.png", "Death", "죽음", "끝과 새로운 시작"),
    ("14_temperance.png", "Temperance", "절제", "조화와 통합"),
    ("15_devil.png", "The Devil", "악마", "고정관념과 집착"),
    ("16_tower.png", "The Tower", "탑", "기존 가정의 재검토"),
    ("17_star.png", "The Star", "별", "희망과 영감"),
    ("18_moon.png", "The Moon", "달", "불확실성과 상상"),
    ("19_sun.png", "The Sun", "태양", "명료함과 활력"),
    ("20_judgement.png", "Judgement", "심판", "되돌아봄과 새 판단"),
    ("21_world.png", "The World", "세계", "완성과 연결"),
]

IDEATION_LENSES = [
    ("관점 바꾸기", "Shift perspective"), ("반대로 생각하기", "Reverse assumptions"),
    ("이질적 연결", "Unexpected connections"), ("제약 없애기", "Remove constraints"),
    ("상황 바꾸기", "Change the setting"), ("문제 재정의", "Reframe the problem"),
]

CSS = """
<style>
.stApp {background: linear-gradient(155deg,#f4f8ff 0%,#f9f5ff 52%,#fdf8f3 100%);}
.block-container {max-width:1080px;padding-top:2rem;}
.hero {text-align:center;padding:22px 14px 12px;}
.hero h1 {font-size:3.25rem;color:#38456f;margin:5px 0 0;letter-spacing:-.04em;}
.hero-eyebrow {font-size:.82rem;letter-spacing:.14em;color:#7987ad;font-weight:700;}
.hero .hero-tagline {font-size:1.48rem;font-weight:750;color:#425987;margin:12px 0 6px;}
.hero .hero-subtitle {font-size:1.02rem;color:#727b9a;margin:4px 0 10px;}
.hero p {color:#727b9a;font-size:1.08rem;margin:8px 0;}
.cloud-label {background:white;border:1px solid #e2e7fa;border-radius:25px;padding:14px 20px;box-shadow:0 10px 30px #9ca8d526;text-align:center;margin:8px 0 18px;color:#505d86;}
.step-line {display:flex;justify-content:center;align-items:center;gap:10px;margin:12px auto;flex-wrap:wrap;}
.step-cloud {padding:9px 15px;border-radius:30px;background:#fff;box-shadow:0 5px 16px #a8b6d73a;color:#53618c;font-size:.87rem;}
.step-arrow {color:#a6add1;}
section[data-testid="stSidebar"] {background:#f4f3fd;}
div.stButton > button {border-radius:18px;min-height:3rem;border:1px solid #d8dff5;background:white;color:#45517d;white-space:normal;height:auto;padding:12px 14px;}
div.stButton > button:hover {border-color:#a58bda;color:#6853a6;background:#f9f5ff;}
div.stButton > button[kind="primary"] {background:#7465c8;color:white;border-color:#7465c8;}
@keyframes cloudHop {0%{transform:translateY(0) scale(1)}35%{transform:translateY(-18px) scale(1.035)}70%{transform:translateY(-4px)}100%{transform:translateY(0)}}
.fairy-hop img {animation:cloudHop 1.1s ease-in-out;}
.journal {background:#fffaf0;border:1px solid #e9dbc2;border-radius:22px;padding:24px;color:#574d45;}
.journal h2 {color:#63513f;margin-top:0;}
.journal .thought {padding:10px 0;border-bottom:1px solid #e7dccd;}
.journal .note {font-size:.9rem;color:#806c5c;}
.mode-selected {border:2px solid #a894ed!important;background:#f3efff!important;}
.cloud-kicker {font-size:.84rem;color:#7d72aa;font-weight:700;margin-bottom:5px;}
.idea-journey {background:#fff;border:1px solid #e2e7fa;border-radius:18px;padding:14px 18px;margin-bottom:16px;}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def tr(ko, en):
    return ko if st.session_state.lang == "한국어" else en

def esc(s):
    return html.escape(str(s))

def img_uri(path):
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()

def ask_ai(task, fallback):
