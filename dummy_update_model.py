from time import sleep
import schedule 

def update_model():
    sleep(10)
    print("Model updated")

if __name__ == "__main__":
    schedule.every(5).minutes.do(update_model)
    
    while True: 
        schedule.run_pending() 
        sleep(1)
        print("Checking for updates...")
