import streamlit as st
import random
from datetime import datetime, timedelta
import time
import json

# 페이지 설정
st.set_page_config(
    page_title="고급 숫자 맞추기 게임",
    page_icon="🎮",
    layout="wide"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .success-animation {
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .game-over {
        color: red;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 초기 세션 상태 설정
if 'game_initialized' not in st.session_state:
    st.session_state.game_initialized = False
    st.session_state.random_number = 0
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.high_scores = []
    st.session_state.start_time = datetime.now()
    st.session_state.current_player = "Player 1"
    st.session_state.players = {"Player 1": 0, "Player 2": 0}
    st.session_state.current_round = 1
    st.session_state.total_rounds = 3
    st.session_state.current_difficulty = '보통'
    st.session_state.game_mode = 'single'

def get_number_range(difficulty):
    ranges = {
        '쉬움': (1, 50),
        '보통': (1, 100),
        '어려움': (1, 200)
    }
    return ranges.get(difficulty, (1, 100))

def reset_game():
    number_range = get_number_range(st.session_state.current_difficulty)
    st.session_state.random_number = random.randint(number_range[0], number_range[1])
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.start_time = datetime.now()
    st.session_state.game_initialized = True

def calculate_score(attempts, elapsed_time, difficulty):
    base_score = 1000
    difficulty_multiplier = {
        '쉬움': 1,
        '보통': 1.5,
        '어려움': 2
    }
    score = base_score - (attempts * 50) - (elapsed_time * 2)
    score *= difficulty_multiplier[difficulty]
    return max(int(score), 0)

def save_score(score):
    new_score = {
        'score': score,
        'attempts': st.session_state.attempts,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'difficulty': st.session_state.current_difficulty
    }
    st.session_state.high_scores.append(new_score)
    st.session_state.high_scores.sort(key=lambda x: x['score'], reverse=True)
    st.session_state.high_scores = st.session_state.high_scores[:10]

def handle_multiplayer_round():
    if st.session_state.current_player == "Player 1":
        st.session_state.current_player = "Player 2"
        reset_game()
    else:
        st.session_state.current_player = "Player 1"
        st.session_state.current_round += 1
        if st.session_state.current_round > st.session_state.total_rounds:
            determine_winner()

def determine_winner():
    if st.session_state.players["Player 1"] > st.session_state.players["Player 2"]:
        st.success("Player 1 승리! 🏆")
    elif st.session_state.players["Player 1"] < st.session_state.players["Player 2"]:
        st.success("Player 2 승리! 🏆")
    else:
        st.info("무승부!")

def main_game():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("🎮 고급 숫자 맞추기 게임")
        
        # 게임 모드 선택
        game_mode = st.radio(
            "게임 모드 선택:", 
            ['싱글플레이어', '멀티플레이어'],
            key='game_mode_select'
        )
        
        # 난이도 선택
        difficulty = st.selectbox(
            "난이도 선택:", 
            ['쉬움', '보통', '어려움'],
            index=['쉬움', '보통', '어려움'].index(st.session_state.current_difficulty),
            key='difficulty_select'
        )
        
        # 시간 제한 설정
        time_limit = st.slider("시간 제한 (초):", 30, 180, 60)

        if st.button("새 게임 시작"):
            st.session_state.current_difficulty = difficulty
            st.session_state.game_mode = 'multi' if game_mode == '멀티플레이어' else 'single'
            if st.session_state.game_mode == 'multi':
                st.session_state.current_player = "Player 1"
                st.session_state.players = {"Player 1": 0, "Player 2": 0}
            reset_game()

    with col2:
        st.subheader("게임 상태")
        if st.session_state.game_mode == 'multi':
            st.write(f"현재 플레이어: {st.session_state.current_player}")
            st.write(f"라운드: {st.session_state.current_round}/{st.session_state.total_rounds}")
        
        elapsed_time = (datetime.now() - st.session_state.start_time).seconds
        remaining_time = max(0, time_limit - elapsed_time)
        st.progress(remaining_time / time_limit)
        st.write(f"남은 시간: {remaining_time}초")

    if not st.session_state.game_initialized:
        st.info("👆 위에서 난이도를 선택하고 '새 게임 시작' 버튼을 눌러주세요!")
        return

    if not st.session_state.game_over and remaining_time > 0:
        number_range = get_number_range(st.session_state.current_difficulty)
        guess = st.number_input(
            "숫자를 입력하세요:",
            min_value=number_range[0],
            max_value=number_range[1]
        )
        
        if st.button("확인"):
            st.session_state.attempts += 1
            
            if guess == st.session_state.random_number:
                st.balloons()
                st.success(f"🎉 정답입니다! {st.session_state.attempts}번 만에 맞추셨네요!")
                score = calculate_score(st.session_state.attempts, elapsed_time, st.session_state.current_difficulty)
                
                if st.session_state.game_mode == 'multi':
                    st.session_state.players[st.session_state.current_player] += score
                    handle_multiplayer_round()
                else:
                    save_score(score)
                
                st.session_state.game_over = True
            
            elif guess < st.session_state.random_number:
                st.warning("더 큰 숫자입니다! ⬆️")
            else:
                st.warning("더 작은 숫자입니다! ⬇️")
            
    elif remaining_time <= 0:
        st.error("시간 초과! 게임 오버!")
        st.session_state.game_over = True

def show_leaderboard():
    st.sidebar.header("🏆 순위표")
    if st.session_state.high_scores:
        for i, score in enumerate(st.session_state.high_scores[:10], 1):
            st.sidebar.markdown(
                f"{i}. {score['score']}점 "
                f"({score['attempts']}회 시도, "
                f"{score['difficulty']}, "
                f"{score['date']})"
            )
    else:
        st.sidebar.markdown("아직 기록이 없습니다!")

def main():
    main_game()
    show_leaderboard()

if __name__ == "__main__":
    main()
