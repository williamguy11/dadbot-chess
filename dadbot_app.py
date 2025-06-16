import streamlit as st
import chess
import chess.engine
import openai
import os

# === Load OpenAI key from Streamlit Secrets ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === Stockfish Path on Streamlit Cloud (use preinstalled binary) ===
STOCKFISH_PATH = "/usr/games/stockfish"

# === Initialize Session State ===
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "comment" not in st.session_state:
    st.session_state.comment = ""
if "engine" not in st.session_state:
    st.session_state.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

# === GPT Commentary Function ===
def get_commentary(move_uci, board_fen):
    prompt = f"""You are DadBot — a witty, encouraging chess coach and proud father.
A move was just played: {move_uci}
Board (FEN): {board_fen}
Respond in 1–2 sentences. Be funny, clever, or supportive."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

# === UI ===
st.title("♟️ DadBot: Your Father's Day Chess Buddy")
st.markdown("Happy Father’s Day! Play chess against Stockfish and enjoy DadBot’s commentary along the way.")

st.code(str(st.session_state.board))  # show board as text

# Select move
legal_moves = [move.uci() for move in st.session_state.board.legal_moves]
selected_move = st.selectbox("Your move:", options=legal_moves)

if st.button("Make Move"):
    try:
        move = chess.Move.from_uci(selected_move)
        st.session_state.board.push(move)
        user_comment = get_commentary(selected_move, st.session_state.board.fen())

        # Stockfish replies
        result = st.session_state.engine.play(st.session_state.board, chess.engine.Limit(time=0.5))
        st.session_state.board.push(result.move)
        bot_comment = get_commentary(result.move.uci(), st.session_state.board.fen())

        st.session_state.comment = f"🧠 DadBot says:\n{user_comment}\n\n♟️ DadBot plays: `{result.move}`\n🧠 {bot_comment}"
    except Exception as e:
        st.error(f"Invalid move: {e}")

st.markdown(st.session_state.comment)

if st.button("🔄 Restart Game"):
    st.session_state.board = chess.Board()
    st.session_state.comment = ""

