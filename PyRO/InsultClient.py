import Pyro4

def main():
    insult_service = Pyro4.Proxy("PYRONAME:insult.service")
    
    while True:
        print("\n1. Add insult\n2. List insults\n3. Exit")
        choice = input("Choose: ")
        
        if choice == "1":
            insult = input("Enter insult: ")
            insult_service.add_insult(insult)
            print("Insult added!")
        elif choice == "2":
            insults = insult_service.get_insults()
            print("\nCurrent insults:", insults)
        elif choice == "3":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()