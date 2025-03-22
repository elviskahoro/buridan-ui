import os
import platform
from datetime import datetime, timedelta


def get_file_times(file_path):
    """Get directory meta data"""

    # Get file stats
    stats = os.stat(file_path)

    # Last modified time (works on all platforms)
    modified_time = datetime.fromtimestamp(stats.st_mtime)

    # Creation time is platform-dependent
    if platform.system() == "Windows":
        # On Windows, st_ctime is the creation time
        creation_time = datetime.fromtimestamp(stats.st_ctime)
    else:
        # On Unix/Linux, st_birthtime is the creation time, but not always available
        try:
            # This works on macOS and some BSD systems
            creation_time = datetime.fromtimestamp(stats.st_birthtime)
        except AttributeError:
            # Fallback for Linux where true creation time might not be available
            creation_time = "Creation time not available on this platform"

    # Count files in the directory (non-recursive)
    file_count = len(
        [f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]
    )

    # Convert datetime objects to strings with MMM DD, YYYY format
    creation_time = creation_time.strftime("%b %d, %Y")
    modified_time = modified_time.strftime("%b %d, %Y")

    return [creation_time, modified_time, file_count]


def get_time_ago(past_time, current_time=None):
    """Convert a past datetime to a human-readable 'time ago' string"""
    if current_time is None:
        current_time = datetime.now()

    time_diff = current_time - past_time

    # Less than a minute
    if time_diff < timedelta(minutes=1):
        return "Updated just now"

    # Less than an hour
    if time_diff < timedelta(hours=1):
        minutes = time_diff.seconds // 60
        return f"Updated {minutes} minute{'s' if minutes != 1 else ''} ago"

    # Less than a day
    if time_diff < timedelta(days=1):
        hours = time_diff.seconds // 3600
        return f"Updated {hours} hour{'s' if hours != 1 else ''} ago"

    # Less than a month
    if time_diff < timedelta(days=30):
        days = time_diff.days
        return f"Updated {days} day{'s' if days != 1 else ''} ago"

    # Less than a year
    if time_diff < timedelta(days=365):
        months = time_diff.days // 30
        return f"Updated {months} month{'s' if months != 1 else ''} ago"

    # More than a year
    years = time_diff.days // 365
    return f"Updated {years} year{'s' if years != 1 else ''} ago"
