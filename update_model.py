from time import sleep
import schedule 

from bayes import update_model


if __name__ == "__main__":
    schedule.every(5).seconds.do(update_model)
    
    while True: 
        schedule.run_pending() 
        sleep(1)
        print("Checking for updates...")
