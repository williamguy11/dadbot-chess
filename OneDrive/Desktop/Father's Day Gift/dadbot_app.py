import streamlit as st
import chess
import chess.engine
import openai
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Stockfish executable path
STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), "stockfish")

# Initialize session state
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "comment" not in st.session_state:
    st.session_state.comment = ""
if "engine" not in st.session_state:
    st.session_state.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

# GPT commentary
def get_commentary(move_uci, board_fen):
    prompt = f"""You are DadBot — a witty, chess-loving dad who gives playful, encouraging, or sarcastic advice.
A move was played: {move_uci}
Board state (FEN): {board_fen}
Respond in 1–2 sentences. Make it fun, clever, or heartwarming."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

# UI
st.title("♟️ Play Chess with DadBot")
st.write("Happy Father's Day! Play against Stockfish with GPT commentary.")

# Show current board as ASCII
st.code(str(st.session_state.board))

# Player move
legal_moves = [move.uci() for move in st.session_state.board.legal_moves]
selected_move = st.selectbox("Your Move:", options=legal_moves)

if st.button("Make Move"):
    move = chess.Move.from_uci(selected_move)
    st.session_state.board.push(move)
    user_comment = get_commentary(selected_move, st.session_state.board.fen())

    # DadBot (Stockfish) replies
    result = st.session_state.engine.play(st.session_state.board, chess.engine.Limit(time=0.5))
    st.session_state.board.push(result.move)
    bot_comment = get_commentary(result.move.uci(), st.session_state.board.fen())

    st.session_state.comment = f"🧠 DadBot says:\n{user_comment}\n\n♟️ DadBot plays: {result.move}\n🧠 {bot_comment}"

# Show commentary
st.markdown(st.session_state.comment)

# Restart button
if st.button("🔄 Restart Game"):
    st.session_state.board = chess.Board()
    st.session_state.comment = ""
