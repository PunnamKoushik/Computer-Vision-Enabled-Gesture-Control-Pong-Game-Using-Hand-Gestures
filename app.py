import streamlit as st
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import tempfile
import os
from PIL import Image
import time

# Set page configuration
st.set_page_config(
    page_title="Hand Tracking Pong Game",
    page_icon="🏓",
    layout="wide"
)

# Add title and description
st.title("Hand Tracking Pong Game")
st.markdown("""
Use your hands to control the paddles and play pong! 
- Left hand controls the left paddle
- Right hand controls the right paddle
- Score points by hitting the ball past your opponent
""")

# Create a placeholder for the game feed
game_placeholder = st.empty()

# Add alpha channel if not present
def add_alpha_channel(image):
    if image.shape[2] == 3:
        b, g, r = cv2.split(image)
        alpha = np.ones(b.shape, dtype=b.dtype) * 255  # Fully opaque
        return cv2.merge([b, g, r, alpha])
    return image

# Function to save uploaded files to temp files
def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
            f.write(uploaded_file.getbuffer())
            return f.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

# Sidebar for game controls and image uploads
with st.sidebar:
    st.header("Game Controls")
    
    start_button = st.button("Start Game")
    stop_button = st.button("Stop Game")
    reset_button = st.button("Reset Game")
    
    st.header("Game Settings")
    
    # Image uploads
    st.subheader("Upload Game Assets (Optional)")
    background_file = st.file_uploader("Background Image", type=["jpg", "jpeg", "png"])
    ball_file = st.file_uploader("Ball Image", type=["jpg", "jpeg", "png"])
    bat1_file = st.file_uploader("Left Bat Image", type=["jpg", "jpeg", "png"])
    bat2_file = st.file_uploader("Right Bat Image", type=["jpg", "jpeg", "png"])
    
    # Game difficulty
    game_speed = st.slider("Game Speed", min_value=5, max_value=25, value=15, step=1)

# Initialize session state variables if they don't exist
if 'game_running' not in st.session_state:
    st.session_state.game_running = False
if 'score' not in st.session_state:
    st.session_state.score = [0, 0]
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'ball_pos' not in st.session_state:
    st.session_state.ball_pos = [100, 100]
if 'speed_x' not in st.session_state:
    st.session_state.speed_x = 15
if 'speed_y' not in st.session_state:
    st.session_state.speed_y = 15

# Handle button clicks
if start_button:
    st.session_state.game_running = True
if stop_button:
    st.session_state.game_running = False
if reset_button:
    st.session_state.game_running = False
    st.session_state.score = [0, 0]
    st.session_state.game_over = False
    st.session_state.ball_pos = [100, 100]
    st.session_state.speed_x = game_speed
    st.session_state.speed_y = game_speed
    time.sleep(0.5)  # Small delay to ensure reset takes effect
    st.session_state.game_running = True

# Main game function
def run_game():
    # Initialize the hand detector
    detector = HandDetector(detectionCon=0.8, maxHands=2)
    
    # Load default images or use uploaded ones
    def load_images():
        # Default paths
        default_bg = "Background.jpg"
        default_ball = "ball.jpg"
        default_bat1 = "bat1.jpg"
        default_bat2 = "bat2.jpg"
        
        # Use uploaded images if available
        bg_path = save_uploaded_file(background_file) if background_file else default_bg
        ball_path = save_uploaded_file(ball_file) if ball_file else default_ball
        bat1_path = save_uploaded_file(bat1_file) if bat1_file else default_bat1
        bat2_path = save_uploaded_file(bat2_file) if bat2_file else default_bat2
        
        try:
            imgBackground = cv2.imread(bg_path)
            imgGameOver = cv2.imread(bg_path)  # Using same background for game over
            imgBall = cv2.imread(ball_path)
            imgBat1 = cv2.imread(bat1_path, cv2.IMREAD_UNCHANGED)
            imgBat2 = cv2.imread(bat2_path, cv2.IMREAD_UNCHANGED)
            
            # If any image fails to load, use colored rectangles instead
            if imgBackground is None:
                imgBackground = np.ones((720, 1280, 3), dtype=np.uint8) * 100  # Dark gray
            if imgGameOver is None:
                imgGameOver = np.ones((720, 1280, 3), dtype=np.uint8) * 100  # Dark gray
            if imgBall is None:
                imgBall = np.ones((50, 50, 3), dtype=np.uint8) * 255  # White ball
                cv2.circle(imgBall, (25, 25), 25, (0, 0, 255), -1)  # Red circle
            if imgBat1 is None:
                imgBat1 = np.ones((150, 30, 3), dtype=np.uint8) * 255  # White bat
                cv2.rectangle(imgBat1, (0, 0), (30, 150), (255, 0, 0), -1)  # Blue rectangle
            if imgBat2 is None:
                imgBat2 = np.ones((150, 30, 3), dtype=np.uint8) * 255  # White bat
                cv2.rectangle(imgBat2, (0, 0), (30, 150), (0, 255, 0), -1)  # Green rectangle
            
            # Add alpha channel to bats
            imgBat1 = add_alpha_channel(imgBat1)
            imgBat2 = add_alpha_channel(imgBat2)
            
            return imgBackground, imgGameOver, imgBall, imgBat1, imgBat2
            
        except Exception as e:
            st.error(f"Error loading images: {e}")
            # Create default colored images
            imgBackground = np.ones((720, 1280, 3), dtype=np.uint8) * 100  # Dark gray
            imgGameOver = np.ones((720, 1280, 3), dtype=np.uint8) * 100  # Dark gray
            imgBall = np.ones((50, 50, 3), dtype=np.uint8) * 255  # White ball
            cv2.circle(imgBall, (25, 25), 25, (0, 0, 255), -1)  # Red circle
            imgBat1 = np.ones((150, 30, 4), dtype=np.uint8) * 255  # White bat with alpha
            cv2.rectangle(imgBat1, (0, 0), (30, 150), (255, 0, 0, 255), -1)  # Blue rectangle
            imgBat2 = np.ones((150, 30, 4), dtype=np.uint8) * 255  # White bat with alpha
            cv2.rectangle(imgBat2, (0, 0), (30, 150), (0, 255, 0, 255), -1)  # Green rectangle
            return imgBackground, imgGameOver, imgBall, imgBat1, imgBat2
    
    # Load images
    imgBackground, imgGameOver, imgBall, imgBat1, imgBat2 = load_images()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Error: Camera not accessible.")
        return
    
    cap.set(3, 1280)
    cap.set(4, 720)
    
    # Update game speed from slider
    st.session_state.speed_x = game_speed
    st.session_state.speed_y = game_speed
    
    # Main game loop
    while st.session_state.game_running:
        success, img = cap.read()
        if not success:
            st.error("Failed to get frame from camera")
            break
        
        img = cv2.flip(img, 1)
        imgRaw = img.copy()
        
        # Find hands
        hands, img = detector.findHands(img, flipType=False)
        
        # Resize background to match camera frame
        imgBackground_resized = cv2.resize(imgBackground, (img.shape[1], img.shape[0]))
        img = cv2.addWeighted(img, 0.2, imgBackground_resized, 0.8, 0)
        
        # Handle hands and paddles
        if hands:
            for hand in hands:
                x, y, w, h = hand['bbox']
                h1, w1, _ = imgBat1.shape
                y1 = np.clip(y - h1 // 2, 20, img.shape[0] - h1 - 20)
                
                if hand['type'] == "Left":
                    img = cvzone.overlayPNG(img, imgBat1, (59, y1))
                    if 59 < st.session_state.ball_pos[0] < 59 + w1 and y1 < st.session_state.ball_pos[1] < y1 + h1:
                        st.session_state.speed_x = -st.session_state.speed_x
                        st.session_state.ball_pos[0] += 30
                        st.session_state.score[0] += 1
                
                if hand['type'] == "Right":
                    img = cvzone.overlayPNG(img, imgBat2, (img.shape[1] - w1 - 59, y1))
                    if img.shape[1] - w1 - 59 < st.session_state.ball_pos[0] < img.shape[1] - 59 and y1 < st.session_state.ball_pos[1] < y1 + h1:
                        st.session_state.speed_x = -st.session_state.speed_x
                        st.session_state.ball_pos[0] -= 30
                        st.session_state.score[1] += 1
        
        # Check if game is over
        if st.session_state.ball_pos[0] < 40 or st.session_state.ball_pos[0] > img.shape[1] - 40:
            st.session_state.game_over = True
        
        # Game logic
        if not st.session_state.game_over:
            # Ball bounces off top and bottom
            if st.session_state.ball_pos[1] >= img.shape[0] - 10 or st.session_state.ball_pos[1] <= 10:
                st.session_state.speed_y = -st.session_state.speed_y
            
            # Update ball position
            st.session_state.ball_pos[0] += st.session_state.speed_x
            st.session_state.ball_pos[1] += st.session_state.speed_y
            
            # Draw ball
            ball_height, ball_width, _ = imgBall.shape
            ball_x1 = int(st.session_state.ball_pos[0] - ball_width // 2)
            ball_y1 = int(st.session_state.ball_pos[1] - ball_height // 2)
            
            if 0 <= ball_x1 < img.shape[1] - ball_width and 0 <= ball_y1 < img.shape[0] - ball_height:
                img[ball_y1:ball_y1 + ball_height, ball_x1:ball_x1 + ball_width] = imgBall
            
            # Display score
            cv2.putText(img, str(st.session_state.score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
            cv2.putText(img, str(st.session_state.score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
        
        else:
            # Game over screen
            img_height, img_width = img.shape[:2]
            go_height, go_width = imgGameOver.shape[:2]
            
            # Resize game over image if needed
            if go_height > img_height or go_width > img_width:
                imgGameOver = cv2.resize(imgGameOver, (img_width, img_height))
            
            # Overlay game over image
            img[0:imgGameOver.shape[0], 0:imgGameOver.shape[1]] = imgGameOver
            
            # Determine winner
            if st.session_state.score[0] > st.session_state.score[1]:
                winner_text = "Player 1 Wins!"
            elif st.session_state.score[1] > st.session_state.score[0]:
                winner_text = "Player 2 Wins!"
            else:
                winner_text = "It's a Draw!"
            
            # Display game over text
            cv2.putText(img, winner_text, (400, 350), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)
            cv2.putText(img, f"Final Score: {st.session_state.score[0]} - {st.session_state.score[1]}", (420, 450), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 0), 5)
            cv2.putText(img, "Press Reset to Play Again", (400, 550), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 5)
        
        # Add raw camera feed in corner
        resized_imgRaw = cv2.resize(imgRaw, (213, 120))
        img[580:580 + resized_imgRaw.shape[0], 20:20 + resized_imgRaw.shape[1]] = resized_imgRaw
        
        # Convert to RGB for Streamlit
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Display the image in Streamlit
        # Display the image in Streamlit
        game_placeholder.image(img_rgb, channels="RGB", use_container_width=True)

        
        # Check if game should be stopped
        if not st.session_state.game_running:
            break
            
    # Release camera when done
    cap.release()

# Display instructions when game is not running
# Display instructions when game is not running
# Display instructions when game is not running
# Display instructions when game is not running
if not st.session_state.game_running:
    st.markdown("""
    ## How to Play
    1. Click the "Start Game" button to begin
    2. Use your left hand to control the left paddle
    3. Use your right hand to control the right paddle
    4. Try to hit the ball past your opponent
    5. First player to reach 10 points wins!
    
    ## Game Controls
    - *Start Game*: Begin playing
    - *Stop Game*: Pause the current game
    - *Reset Game*: Start a new game
    
    ## Tips
    - Make sure you have good lighting for better hand detection
    - Keep your hands clearly visible to the camera
    - Move your hands up and down to control the paddles
    """)
    
    # Create simple instruction visuals using text
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Left Hand")
        st.markdown("Controls left paddle")
        # Create a simple colored box to represent the left paddle
        st.markdown(
            """
            <div style="background-color: #3498db; height: 150px; width: 30px; margin: auto;"></div>
            """, 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown("### Ball Movement")
        st.markdown("Bounces between paddles")
        # Create a simple colored circle to represent the ball
        st.markdown(
            """
            <div style="background-color: #e74c3c; height: 50px; width: 50px; border-radius: 50%; margin: auto;"></div>
            """, 
            unsafe_allow_html=True
        )
    with col3:
        st.markdown("### Right Hand")
        st.markdown("Controls right paddle")
        # Create a simple colored box to represent the right paddle
        st.markdown(
            """
            <div style="background-color: #2ecc71; height: 150px; width: 30px; margin: auto;"></div>
            """, 
            unsafe_allow_html=True
        )

# Run the game when it's active
if st.session_state.game_running:
    run_game()

# Add footer
st.markdown("---")
st.markdown("### Hand Tracking Pong Game | Created with Streamlit, OpenCV, and CVZone")
st.markdown("Camera access is required to play this game. All processing is done locally on your device.")

# Add camera permission info
with st.expander("Camera Permissions"):
    st.markdown("""
    This app requires access to your camera to track hand movements. 
    - No video data is stored or transmitted
    - All processing happens in your browser
    - You can stop camera access at any time by clicking "Stop Game"
    """)

# Add troubleshooting section
with st.expander("Troubleshooting"):
    st.markdown("""
    *Camera not working?*
    1. Make sure your browser has permission to access your camera
    2. Try refreshing the page
    3. Check if another application is using your camera
    
    *Game running slowly?*
    1. Close other applications to free up resources
    2. Reduce the game speed in the sidebar
    3. Try using a computer with better specifications
    
    *Hands not being detected?*
    1. Improve lighting in your room
    2. Make sure your hands are clearly visible to the camera
    3. Keep your hands within the camera frame
    """)