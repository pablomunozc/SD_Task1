import Pyro4
import time

def main():
    filter_service = Pyro4.Proxy("PYRONAME:insult.filter.service")
    
    while True:
        print("\n1. Submit text\n2. Show results\n3. Exit")
        choice = input("Choose: ")
        
        if choice == "1":
            text = input("Enter text to filter: ")
            filter_service.submit_text(text)
            print("Text submitted for processing")
        elif choice == "2":
            results = filter_service.get_filtered_texts()
            print("\nFiltered texts:", results)
        elif choice == "3":
            break
        else:
            print("Invalid choice")
        
        # Give some time for processing
        time.sleep(0.5)

if __name__ == "__main__":
    main()