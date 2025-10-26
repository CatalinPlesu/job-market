from src.scrape_jobs_list import scrape_jobs_list
from src.scrape_job_details import scrape_job_details
from src.scrape_job_recheck import recheck_alive_jobs, recheck_all_jobs
from src.structure_data_with_llm import structure_data_with_llm
from src.process_data import process_data
from src.generate_html_page import generate_html_page


def exit_app():
    print("Exiting...")
    exit()


def print_menu():
    print("\033c", end="")  # Clear screen
    print("="*50)
    print("DATA PROCESSING CONSOLE APP")
    print("="*50)

    functions = [
        ("Scrape Job Listings (Stage 1)", scrape_jobs_list),
        ("Scrape Job Details (Stage 2)", scrape_job_details),
        ("Re-check Alive Jobs", recheck_alive_jobs),
        ("Re-check All (Including Rotten) Jobs", recheck_all_jobs),
        ("Structure Data with LLM", structure_data_with_llm),
        ("Process Data", process_data),
        ("Generate HTML Page", generate_html_page),
        ("Exit", exit_app)
    ]

    for i, (label, _) in enumerate(functions, 1):
        print(f"{i}. {label}")

    print("-"*50)
    return functions


def run():
    while True:
        functions = print_menu()
        try:
            choice = int(input("Select an option (1-5): ").strip())
            if 1 <= choice <= len(functions):
                _, func = functions[choice - 1]
                func()
                input("Press Enter to continue...")
            else:
                print("Invalid option. Please try again.")
                import time
                time.sleep(1)
        except ValueError:
            print("Invalid input. Please enter a number.")
            import time
            time.sleep(1)


if __name__ == "__main__":
    run()
