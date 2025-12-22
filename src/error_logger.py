"""
Error-only logging module for scraping operations.
Logs only errors to weekly log files.
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class WeeklyErrorLogger:
    """
    Logger that creates weekly log files and only logs errors.
    Automatically rotates logs to new files each week.
    """
    
    def __init__(self, log_dir: str = "logs", logger_name: str = "scraper"):
        """
        Initialize weekly error logger.
        
        Args:
            log_dir: Directory to store log files (default: "logs")
            logger_name: Name of the logger
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.logger_name = logger_name
        
        # Create logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.ERROR)  # Only log errors
        
        # Remove any existing handlers
        self.logger.handlers.clear()
        
        # Add file handler for current week
        self._setup_handler()
    
    def _get_week_file_path(self, dt: Optional[datetime] = None) -> Path:
        """
        Get log file path for the week containing the given date.
        
        Args:
            dt: Date to get week for (default: current date)
            
        Returns:
            Path to log file for that week
        """
        if dt is None:
            dt = datetime.now()
        
        # Get Monday of the week containing dt
        # ISO week starts on Monday
        days_since_monday = dt.weekday()
        monday = dt - timedelta(days=days_since_monday)
        
        # Format: logs/scraper_2025-W01.log
        week_num = monday.isocalendar()[1]
        year = monday.year
        
        filename = f"{self.logger_name}_{year}-W{week_num:02d}.log"
        return self.log_dir / filename
    
    def _setup_handler(self):
        """Setup file handler for current week."""
        log_file = self._get_week_file_path()
        
        # Create file handler
        handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(handler)
        
        self.current_log_file = log_file
        self.current_week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    
    def _check_rotation(self):
        """Check if we need to rotate to a new week's log file."""
        now = datetime.now()
        current_week_start = now - timedelta(days=now.weekday())
        
        # If we're in a new week, rotate
        if current_week_start > self.current_week_start:
            # Remove old handler
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)
            
            # Setup new handler for new week
            self._setup_handler()
    
    def error(self, message: str, exc_info: bool = False):
        """
        Log an error message.
        
        Args:
            message: Error message to log
            exc_info: Include exception information if True
        """
        self._check_rotation()
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """
        Log a critical error message.
        
        Args:
            message: Critical error message to log
            exc_info: Include exception information if True
        """
        self._check_rotation()
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message: str):
        """
        Log an exception with traceback.
        
        Args:
            message: Error message to log
        """
        self._check_rotation()
        self.logger.exception(message)
    
    @staticmethod
    def cleanup_old_logs(log_dir: str = "logs", keep_weeks: int = 4):
        """
        Clean up log files older than specified weeks.
        
        Args:
            log_dir: Directory containing log files
            keep_weeks: Number of weeks to keep (default: 4)
        """
        log_path = Path(log_dir)
        if not log_path.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(weeks=keep_weeks)
        
        for log_file in log_path.glob("*.log"):
            # Extract week from filename (format: scraper_2025-W01.log)
            try:
                parts = log_file.stem.split('_')
                if len(parts) >= 2:
                    week_str = parts[-1]  # e.g., "2025-W01"
                    year_str, week_str = week_str.split('-W')
                    year = int(year_str)
                    week = int(week_str)
                    
                    # Get first day of that week
                    # ISO calendar: week 1 is the first week with a Thursday
                    import datetime as dt
                    jan_4 = dt.date(year, 1, 4)
                    week_1_start = jan_4 - timedelta(days=jan_4.weekday())
                    week_start = week_1_start + timedelta(weeks=week - 1)
                    
                    week_datetime = datetime.combine(week_start, datetime.min.time())
                    
                    if week_datetime < cutoff_date:
                        log_file.unlink()
                        print(f"Cleaned up old log: {log_file.name}")
            
            except Exception as e:
                # If we can't parse the filename, skip it
                print(f"Warning: Could not parse log file {log_file.name}: {e}")
                continue


# Global logger instance
_global_logger: Optional[WeeklyErrorLogger] = None


def get_logger(log_dir: str = "logs", logger_name: str = "scraper") -> WeeklyErrorLogger:
    """
    Get or create the global error logger instance.
    
    Args:
        log_dir: Directory to store log files
        logger_name: Name of the logger
        
    Returns:
        WeeklyErrorLogger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = WeeklyErrorLogger(log_dir, logger_name)
    
    return _global_logger
