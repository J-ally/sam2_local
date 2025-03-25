from datetime import datetime

def convert_timestamp_to_seconds(timestamp):
    """Convert a timestamp in 'HH:MM:SS' format to total seconds."""
    hours, minutes, seconds = map(int, timestamp.split(':'))
    return hours * 3600 + minutes * 60 + seconds


def calculate_time_difference(start_time, end_time):
    """Calculate the difference in seconds between two timestamps."""
    start_seconds = convert_timestamp_to_seconds(start_time)
    end_seconds = convert_timestamp_to_seconds(end_time)
    return end_seconds - start_seconds


def format_seconds_to_timestamp(seconds):
    """Convert total seconds to a timestamp in 'HH:MM:SS' format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def extract_start_time_video_path (video_path : str) -> datetime:
    """Extract the start time from the video path
    Input:
        video_path (str): the path to the video file
    Outputs:
        time_dt (datetime): the start time of the video
    """
    time_str = video_path.split('/')[-1].split('_')[0]
    time_dt = datetime.strptime(time_str, '%Y%m%d%H%M%S')
    return time_dt