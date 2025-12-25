"""
Test that print_threaded handles None progress_tracker gracefully.
This test verifies the fix for the error:
'NoneType' object has no attribute 'add_log_message'
"""
from src.scrape_jobs_list import print_threaded, progress_tracker, store_jobs
from src.scrape_database import ScrapeSessionLocal


def test_print_threaded_with_none_tracker():
    """Test that print_threaded doesn't crash when progress_tracker is None"""
    print("Testing print_threaded with None progress_tracker...")
    
    # The global progress_tracker should be None initially
    assert progress_tracker is None, "progress_tracker should be None initially"
    
    # This should not raise an error
    try:
        print_threaded(0, "Test message")
        print("✓ print_threaded handled None progress_tracker gracefully")
        return True
    except AttributeError as e:
        print(f"✗ print_threaded failed with None progress_tracker: {e}")
        return False


def test_store_jobs_with_none_tracker():
    """Test that store_jobs doesn't crash when progress_tracker is None"""
    print("Testing store_jobs with None progress_tracker...")
    
    # Create a test database session
    db = ScrapeSessionLocal()
    
    try:
        # Create some dummy job data
        jobs_data = [
            {
                'url': 'https://example.com/job1',
                'title': 'Test Job 1',
                'company': 'Test Company',
                'site': 'test.md'
            }
        ]
        
        # This should not raise an error even with None progress_tracker
        try:
            store_jobs(db, jobs_data)
            print("✓ store_jobs handled None progress_tracker gracefully")
            return True
        except AttributeError as e:
            print(f"✗ store_jobs failed with None progress_tracker: {e}")
            return False
    finally:
        db.rollback()  # Don't commit test data
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING PROGRESS TRACKER FIX")
    print("="*60 + "\n")
    
    test1 = test_print_threaded_with_none_tracker()
    print()
    test2 = test_store_jobs_with_none_tracker()
    
    print("\n" + "="*60)
    if test1 and test2:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("="*60 + "\n")
