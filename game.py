import streamlit as st
import random
from datetime import datetime, timedelta
import time
import json
import base64

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

# 세션 상태 초기화
def init_session_state():
    if 'random_number' not in st.session_state:
        st.session_state.random_number = random.randint(1, 100)
    if 'attempts' not in st.session_state:
        st.session_state.attempts = 0
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'high_scores' not in st.session_state:
        st.session_state.high_scores = []
    if 'start_time' not in st.session_state:
        st.session_state.start_time = datetime.now()
    if 'current_player' not in st.session_state:
        st.session_state.current_player = "Player 1"
    if 'players' not in st.session_state:
        st.session_state.players = {"Player 1": 0, "Player 2": 0}
    if 'game_mode' not in st.session_state:
        st.session_state.game_mode = 'single'
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'total_rounds' not in st.session_state:
        st.session_state.total_rounds = 3

init_session_state()

# 게임 리셋 함수
def reset_game():
    difficulty = st.session_state.get('current_difficulty', '보통')
    if difficulty == '쉬움':
        st.session_state.random_number = random.randint(1, 50)
    elif difficulty == '보통':
        st.session_state.random_number = random.randint(1, 100)
    else:
        st.session_state.random_number = random.randint(1, 200)
    
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.start_time = datetime.now()

# 사운드 효과 함수 (base64로 인코딩된 작은 오디오 파일을 사용)
def get_sound_html(sound_type):
    if sound_type == 'success':
        audio_file = "data:audio/wav;base64,..."  # 실제 base64 인코딩된 성공 효과음
    elif sound_type == 'error':
        audio_file = "data:audio/wav;base64,..."  # 실제 base64 인코딩된 실패 효과음
    return f'<audio autoplay><source src="{audio_file}" type="audio/wav">브라우저가 오디오를 지원하지 않습니다.</audio>'

# 메인 게임 UI
def main_game():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("🎮 고급 숫자 맞추기 게임")
        
        # 게임 모드 선택
        game_mode = st.radio("게임 모드 선택:", 
                            ['싱글플레이어', '멀티플레이어'], 
                            key='game_mode_select')
        
        # 난이도 선택
        if 'current_difficulty' not in st.session_state:
            st.session_state.current_difficulty = '보통'
            
        difficulty = st.selectbox("난이도 선택:", 
                                ['쉬움 (1-50)', '보통 (1-100)', '어려움 (1-200)'],
                                key='difficulty_select')
        
        # 시간 제한 설정
        time_limit = st.slider("시간 제한 (초):", 30, 180, 60)
        
        if st.button("새 게임 시작"):
            st.session_state.current_difficulty = difficulty.split()[0].lower()
            reset_game()
            if game_mode == '멀티플레이어':
                st.session_state.game_mode = 'multi'
                st.session_state.current_player = "Player 1"
                st.session_state.players = {"Player 1": 0, "Player 2": 0}
            else:
                st.session_state.game_mode = 'single'

    with col2:
        # 현재 게임 상태 표시
        st.subheader("게임 상태")
        if st.session_state.game_mode == 'multi':
            st.write(f"현재 플레이어: {st.session_state.current_player}")
            st.write(f"라운드: {st.session_state.current_round}/{st.session_state.total_rounds}")
        
        # 남은 시간 표시
        elapsed_time = (datetime.now() - st.session_state.start_time).seconds
        remaining_time = max(0, time_limit - elapsed_time)
        st.progress(remaining_time / time_limit)
        st.write(f"남은 시간: {remaining_time}초")

    # 게임 진행
    if not st.session_state.game_over and remaining_time > 0:
        guess = st.number_input("숫자를 입력하세요:", 
                              min_value=1, 
                              max_value=200 if difficulty == '어려움 (1-200)' else (100 if difficulty == '보통 (1-100)' else 50))
        
        if st.button("확인"):
            st.session_state.attempts += 1
            
            if guess == st.session_state.random_number:
                st.balloons()
                st.success(f"🎉 정답입니다! {st.session_state.attempts}번 만에 맞추셨네요!")
                score = calculate_score(st.session_state.attempts, elapsed_time, difficulty)
                
                if st.session_state.game_mode == 'multi':
                    st.session_state.players[st.session_state.current_player] += score
                    handle_multiplayer_round()
                else:
                    save_score(score)
                
                st.session_state.game_over = True
            
            elif guess < st.session_state.random_number:
                st.warning("더 큰 숫자입니다! ⬆️")
                st.markdown(get_sound_html('error'), unsafe_allow_html=True)
            else:
                st.warning("더 작은 숫자입니다! ⬇️")
                st.markdown(get_sound_html('error'), unsafe_allow_html=True)
    
    elif remaining_time <= 0:
        st.error("시간 초과! 게임 오버!")
        st.session_state.game_over = True

# 점수 계산 함수
def calculate_score(attempts, elapsed_time, difficulty):
    base_score = 1000
    difficulty_multiplier = {
        '쉬움 (1-50)': 1,
        '보통 (1-100)': 1.5,
        '어려움 (1-200)': 2
    }
    
    score = base_score - (attempts * 50) - (elapsed_time * 2)
    score *= difficulty_multiplier[difficulty]
    return max(int(score), 0)

# 멀티플레이어 라운드 처리
def handle_multiplayer_round():
    if st.session_state.current_player == "Player 1":
        st.session_state.current_player = "Player 2"
        reset_game()
    else:
        st.session_state.current_player = "Player 1"
        st.session_state.current_round += 1
        if st.session_state.current_round > st.session_state.total_rounds:
            determine_winner()

# 승자 결정
def determine_winner():
    if st.session_state.players["Player 1"] > st.session_state.players["Player 2"]:
        st.success("Player 1 승리! 🏆")
    elif st.session_state.players["Player 1"] < st.session_state.players["Player 2"]:
        st.success("Player 2 승리! 🏆")
    else:
        st.info("무승부!")

# 점수 저장
def save_score(score):
    new_score = {
        'score': score,
        'attempts': st.session_state.attempts,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'difficulty': st.session_state.difficulty
    }
    st.session_state.high_scores.append(new_score)
    st.session_state.high_scores.sort(key=lambda x: x['score'], reverse=True)
    st.session_state.high_scores = st.session_state.high_scores[:10]

# 사이드바 - 순위표
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

# 메인 실행
def main():
    main_game()
    show_leaderboard()

if __name__ == "__main__":
    main()
