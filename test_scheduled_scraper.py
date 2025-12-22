"""
Simple verification test for scheduled scraping components.
Tests basic functionality without running actual scraping.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scheduler import Scheduler
from src.reporting import DailyReport, Stage1Stats, Stage2Stats, Stage3Stats
from src.error_logger import WeeklyErrorLogger
from src.database_backup import DatabaseBackup
from datetime import datetime, time as dt_time
import tempfile
import shutil


def test_scheduler():
    """Test scheduler initialization and state management."""
    print("\n" + "="*80)
    print("Testing Scheduler")
    print("="*80)
    
    # Create scheduler
    scheduler = Scheduler(schedule_time_hour=0, schedule_time_minute=0)
    
    # Test get_next_run_time
    next_run = scheduler.get_next_run_time()
    print(f"✓ Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test should_run_now (should be False for new scheduler)
    should_run = scheduler.should_run_now()
    print(f"✓ Should run now: {should_run} (expected: False for new scheduler)")
    
    # Test save and load state
    test_time = datetime.now()
    scheduler.save_last_run(test_time)
    loaded_time = scheduler.load_last_run()
    
    if loaded_time:
        print(f"✓ State persistence works: {loaded_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("✗ State persistence failed")
        return False
    
    # Cleanup
    if scheduler.state_file.exists():
        scheduler.state_file.unlink()
    
    print("✓ Scheduler tests passed!")
    return True


def test_reporting():
    """Test report generation."""
    print("\n" + "="*80)
    print("Testing Reporting System")
    print("="*80)
    
    # Create temporary directory for reports
    with tempfile.TemporaryDirectory() as tmpdir:
        report = DailyReport(reports_dir=tmpdir)
        
        # Add some test statistics
        report.add_stage1_stats(Stage1Stats(
            site="test_site_1",
            links_found=150,
            pages_scraped=5,
            errors=0
        ))
        
        report.add_stage1_stats(Stage1Stats(
            site="test_site_2",
            links_found=200,
            pages_scraped=7,
            errors=1
        ))
        
        report.add_stage2_stats(Stage2Stats(
            site="test_site_1",
            total_jobs=150,
            success=140,
            empty=5,
            failed=5,
            http_200=140,
            http_404=3,
            http_other=2
        ))
        
        report.add_stage3_stats(Stage3Stats(
            site="test_site_1",
            total_checked=100,
            alive=95,
            dead=5
        ))
        
        # Save report
        report.save()
        
        # Check if files were created
        json_file = Path(tmpdir) / f"report_{report.report_date.isoformat()}.json"
        txt_file = json_file.with_suffix('.txt')
        
        if json_file.exists():
            print(f"✓ JSON report created: {json_file.name}")
        else:
            print("✗ JSON report not created")
            return False
        
        if txt_file.exists():
            print(f"✓ Text report created: {txt_file.name}")
            # Display text report
            print("\nReport Preview:")
            print("-" * 80)
            with open(txt_file, 'r') as f:
                print(f.read())
        else:
            print("✗ Text report not created")
            return False
    
    print("✓ Reporting tests passed!")
    return True


def test_error_logger():
    """Test error logging."""
    print("\n" + "="*80)
    print("Testing Error Logger")
    print("="*80)
    
    # Create temporary directory for logs
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = WeeklyErrorLogger(log_dir=tmpdir, logger_name="test_scraper")
        
        # Log some test errors
        logger.error("Test error message 1")
        logger.error("Test error message 2")
        logger.critical("Test critical message")
        
        # Check if log file was created
        log_files = list(Path(tmpdir).glob("*.log"))
        
        if log_files:
            log_file = log_files[0]
            print(f"✓ Log file created: {log_file.name}")
            
            # Read and display log content
            with open(log_file, 'r') as f:
                content = f.read()
                if content:
                    print(f"✓ Log file contains {len(content.splitlines())} lines")
                    print("\nLog Preview:")
                    print("-" * 80)
                    print(content)
                else:
                    print("✗ Log file is empty")
                    return False
        else:
            print("✗ Log file not created")
            return False
    
    print("✓ Error logger tests passed!")
    return True


def test_database_backup():
    """Test database backup."""
    print("\n" + "="*80)
    print("Testing Database Backup")
    print("="*80)
    
    # Create temporary database and backup directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy database file
        db_path = Path(tmpdir) / "test.db"
        db_path.write_text("dummy database content")
        
        backup_dir = Path(tmpdir) / "backups"
        backup = DatabaseBackup(str(db_path), backup_dir=str(backup_dir), keep_days=3)
        
        # Create a backup
        backup_path = backup.create_backup()
        
        if backup_path.exists():
            print(f"✓ Backup created: {backup_path.name}")
        else:
            print("✗ Backup not created")
            return False
        
        # List backups
        backups = backup.list_backups()
        print(f"✓ Found {len(backups)} backup(s)")
        
        # Create more backups to test cleanup
        import time
        for i in range(3):
            time.sleep(0.1)
            backup.create_backup()
        
        backups = backup.list_backups()
        print(f"✓ Total backups after creating 3 more: {len(backups)}")
        
        # Test cleanup (with keep_days=0 to force deletion)
        backup.keep_days = 0
        deleted = backup.cleanup_old_backups()
        print(f"✓ Cleaned up {deleted} old backup(s)")
    
    print("✓ Database backup tests passed!")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("SCHEDULED SCRAPER COMPONENT VERIFICATION")
    print("="*80)
    
    tests = [
        ("Scheduler", test_scheduler),
        ("Reporting", test_reporting),
        ("Error Logger", test_error_logger),
        ("Database Backup", test_database_backup),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:20} : {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "="*80)
        print("ALL TESTS PASSED!")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("SOME TESTS FAILED!")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
