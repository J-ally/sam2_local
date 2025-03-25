from gui.main_window import MainWindow
import sys
import atexit
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from models.SAM2_local import select_device, set_cuda_parameters, extract_frames_from_video,\
    scan_dir_for_frames, show_mask, show_points, show_box
from sam2.build_sam import build_sam2_video_predictor


def main(video_path: str):
    """
    Main function that initializes the application and shows the main window.

    Args:
        video_path (str): path to video file to be played
    """
    app = QApplication(sys.argv)
    
    # Create and show the main window
    print(f"Creating MainWindow with video path: {video_path}")
    
    main_window = MainWindow(video_path=video_path)
    
    # Get screen geometry
    screen = QDesktopWidget().availableGeometry()
    
    # Calculate appropriate window size based on screen dimensions
    # while preserving 16:9 aspect ratio
    if screen.width() / screen.height() >= 16/9:
        # Screen is wider than 16:9, adjust based on height
        window_height = int(screen.height() * 0.8)  # 80% of screen height
        window_width = int(window_height * 16/9)     # Calculate width to maintain 16:9
    else:
        # Screen is narrower than 16:9, adjust based on width
        window_width = int(screen.width() * 0.8)    # 80% of screen width
        window_height = int(window_width * 9/16)     # Calculate height to maintain 16:9
    
    # Resize window
    main_window.resize(window_width, window_height)
    
    # Center the window on screen
    center_point = screen.center()
    main_window.move(center_point.x() - window_width // 2, 
                     center_point.y() - window_height // 2)
    
    main_window.show()
    
    # Clean exit handling
    def clean_exit():
        # Release resources properly
        if hasattr(main_window, 'video_player') and hasattr(main_window.video_player, 'media_player'):
            main_window.video_player.media_player.stop()
    
    # Register cleanup function
    atexit.register(clean_exit)
    
    # Add a closeEvent handler to MainWindow
    def safe_close():
        clean_exit()
        app.quit()
    
    # Ensure the application can be closed safely
    main_window.closeEvent = lambda event: safe_close()
    
    # Start the event loop
    return app.exec_()


if __name__ == "__main__":
    video_path = '/Users/josephallyndree/Dropbox/Joseph/A-PhD/20250224 - Benchmark Tracking/Code/video-tracking-benchmark/data/videos/20241018151929_D06_cut_5.mp4'
    
    device = select_device()
    set_cuda_parameters(device)
    
    sam2_checkpoint = "checkpoints/sam2.1_hiera_large.pt"
    model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
    video_dir = "video_frames"

    predictor = build_sam2_video_predictor(model_cfg, sam2_checkpoint, device=device)
    
    # extract_frames_from_video(video_path, video_dir)
    
    all_frames = scan_dir_for_frames(video_dir, 8)
    print(len(all_frames))
    
    sys.exit(main(video_path))