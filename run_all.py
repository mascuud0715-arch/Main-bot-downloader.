import threading
import os

def run_main():
    os.system("python main_bot.py")

def run_admin():
    os.system("python admin_bot.py")

def run_receiver():
    os.system("python receiver_bot.py")

if __name__ == "__main__":
    t1 = threading.Thread(target=run_main)
    t2 = threading.Thread(target=run_admin)
    t3 = threading.Thread(target=run_receiver)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
