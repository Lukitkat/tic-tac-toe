import streamlit as st
import random
import time

VERSION = "1.0.0"

def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != "":
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != "":
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != "":
        return board[0][2]
    if all(cell != "" for row in board for cell in row):
        return "draw"
    return None

def reset_game(state=None):
    if state is None:
        state = st.session_state
    state.board = [["" for _ in range(3)] for _ in range(3)]
    state.current_player = "X"
    state.game_over = False
    state.winner = None
    state.board_key += 1

def bot_move(board=None):
    if board is None:
        board = st.session_state.board
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    if empty_cells:
        return random.choice(empty_cells)
    return None

def handle_click(row, col):
    if st.session_state.game_over or st.session_state.board[row][col] != "":
        return
    st.session_state.board[row][col] = st.session_state.current_player
    st.session_state.winner = check_winner(st.session_state.board)

    if st.session_state.winner == "draw":
        st.session_state.scores["draw"] += 1
        st.session_state.game_over = True
    elif st.session_state.winner:
        st.session_state.scores[st.session_state.winner] += 1
        st.session_state.game_over = True
    else:
        st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"

if __name__ == "__main__":
    st.set_page_config(page_title="Jogo da Velha", layout="centered")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎮 Jogo da Velha")
    with col2:
        st.markdown(f"<small>Versão {VERSION}</small>", unsafe_allow_html=True)

    if "board" not in st.session_state:
        st.session_state.board = [["" for _ in range(3)] for _ in range(3)]
    if "current_player" not in st.session_state:
        st.session_state.current_player = "X"
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "winner" not in st.session_state:
        st.session_state.winner = None
    if "scores" not in st.session_state:
        st.session_state.scores = {"X": 0, "O": 0, "draw": 0}
    if "game_mode" not in st.session_state:
        st.session_state.game_mode = "human"
    if "board_key" not in st.session_state:
        st.session_state.board_key = 0

    st.subheader("Modo de Jogo")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 vs 👤", use_container_width=True):
            st.session_state.game_mode = "human"
            reset_game()
    with col2:
        if st.button("👤 vs 🤖", use_container_width=True):
            st.session_state.game_mode = "bot"
            reset_game()

    st.divider()

    st.subheader("📊 Placar")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Jogador X", st.session_state.scores["X"])
    with col2:
        st.metric("Jogador O", st.session_state.scores["O"])
    with col3:
        st.metric("Empates", st.session_state.scores["draw"])

    st.divider()

    st.subheader("Tabuleiro")

    # Container para o tabuleiro
    board_container = st.container()

    with board_container:
        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                current_value = st.session_state.board[row][col]
                label = current_value if current_value else " "

                if cols[col].button(label, key=f"cell_{row}_{col}_{st.session_state.board_key}", use_container_width=True):
                    handle_click(row, col)
                    st.session_state.board_key += 1
                    st.rerun()

            if row < 2:
                st.divider()

    if (st.session_state.game_mode == "bot" and
        st.session_state.current_player == "O" and
        not st.session_state.game_over):

        st.info("🤖 Bot pensando...")
        time.sleep(0.5)

        row, col = bot_move()
        if row is not None:
            handle_click(row, col)
            st.session_state.board_key += 1
            st.rerun()

    if st.session_state.game_over:
            st.divider()
            if st.session_state.winner == "draw":
                st.warning("🤝 Empate! Tente novamente.")
            else:
                st.balloons()  # Efeito visual de comemoração
                st.success(f"🎉 Sensacional! O Jogador {st.session_state.winner} venceu a partida! 🏆")

            if st.button("🔄 Jogar Novamente", use_container_width=True):
                reset_game()


    st.divider()
    if not st.session_state.game_over:
        st.info(f"🎯 Vez do jogador: **{st.session_state.current_player}**")
