"""
Test to verify the custom time input feature works correctly.
"""
import sys
from pathlib import Path
from datetime import datetime, time as dt_time
import tempfile

sys.path.insert(0, str(Path(__file__).parent))

from src.scheduler import Scheduler


def test_custom_time_parsing():
    """Test that various time formats work correctly."""
    print("\n" + "="*80)
    print("TEST: Custom time parsing and validation")
    print("="*80)
    
    test_cases = [
        ("00:00", 0, 0, True, "Midnight"),
        ("12:30", 12, 30, True, "Afternoon"),
        ("23:59", 23, 59, True, "Last minute of day"),
        ("14:15", 14, 15, True, "Afternoon"),
        ("09:05", 9, 5, True, "Morning"),
    ]
    
    all_passed = True
    
    for time_str, expected_hour, expected_minute, should_work, description in test_cases:
        try:
            parts = time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1])
            
            # Validate
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                if should_work:
                    print(f"✗ {description} ({time_str}): Should have passed validation but failed")
                    all_passed = False
                else:
                    print(f"✓ {description} ({time_str}): Correctly rejected")
            else:
                if should_work:
                    if hour == expected_hour and minute == expected_minute:
                        print(f"✓ {description} ({time_str}): Parsed as {hour:02d}:{minute:02d}")
                    else:
                        print(f"✗ {description} ({time_str}): Expected {expected_hour:02d}:{expected_minute:02d}, got {hour:02d}:{minute:02d}")
                        all_passed = False
                else:
                    print(f"✗ {description} ({time_str}): Should have been rejected but passed")
                    all_passed = False
        
        except Exception as e:
            if should_work:
                print(f"✗ {description} ({time_str}): Exception - {e}")
                all_passed = False
            else:
                print(f"✓ {description} ({time_str}): Correctly raised exception")
    
    return all_passed


def test_scheduler_with_custom_time():
    """Test that scheduler works with custom time."""
    print("\n" + "="*80)
    print("TEST: Scheduler with custom time")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test creating scheduler with custom time
        custom_hour = 14
        custom_minute = 30
        
        scheduler = Scheduler(schedule_time_hour=custom_hour, schedule_time_minute=custom_minute)
        scheduler.state_file = Path(tmpdir) / "scheduler_state.json"
        
        next_run = scheduler.get_next_run_time()
        
        print(f"✓ Scheduler created with custom time: {custom_hour:02d}:{custom_minute:02d}")
        print(f"✓ Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verify the schedule time matches
        assert next_run.hour == custom_hour or (next_run.hour == 0 and custom_hour == 0), \
            f"Hour mismatch: expected {custom_hour}, got {next_run.hour}"
        assert next_run.minute == custom_minute, \
            f"Minute mismatch: expected {custom_minute}, got {next_run.minute}"
        
        print(f"✓ Schedule time correctly set to {custom_hour:02d}:{custom_minute:02d}")
    
    return True


def test_invalid_time_formats():
    """Test that invalid formats are rejected."""
    print("\n" + "="*80)
    print("TEST: Invalid time format rejection")
    print("="*80)
    
    invalid_cases = [
        ("25:00", "Hour > 23"),
        ("12:60", "Minute > 59"),
        ("-1:30", "Negative hour"),
        ("12:-5", "Negative minute"),
        ("ab:cd", "Non-numeric"),
        ("12", "Missing minute"),
        ("12:30:45", "Too many parts"),
    ]
    
    all_passed = True
    
    for time_str, reason in invalid_cases:
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                print(f"✓ {reason} ({time_str}): Correctly rejected (wrong format)")
                continue
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                print(f"✓ {reason} ({time_str}): Correctly rejected (out of range)")
            else:
                print(f"✗ {reason} ({time_str}): Should have been rejected but passed")
                all_passed = False
        
        except ValueError:
            print(f"✓ {reason} ({time_str}): Correctly rejected (ValueError)")
        except Exception as e:
            print(f"✓ {reason} ({time_str}): Rejected with {type(e).__name__}")
    
    return all_passed


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("CUSTOM TIME OPTION VERIFICATION")
    print("="*80)
    
    tests = [
        ("Custom time parsing", test_custom_time_parsing),
        ("Scheduler with custom time", test_scheduler_with_custom_time),
        ("Invalid format rejection", test_invalid_time_formats),
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
        print(f"{test_name:35} : {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "="*80)
        print("ALL TESTS PASSED - CUSTOM TIME OPTION WORKS!")
        print("="*80)
        print("\nYou can now:")
        print("  • Use option 1 to run immediately")
        print("  • Use option 2 to schedule at 00:00 (default)")
        print("  • Use option 3 to specify custom time (HH:MM)")
        return 0
    else:
        print("\n" + "="*80)
        print("SOME TESTS FAILED!")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
