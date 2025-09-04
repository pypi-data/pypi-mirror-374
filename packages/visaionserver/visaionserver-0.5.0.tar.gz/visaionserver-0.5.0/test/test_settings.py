from visaionserver.core import SETTINGS as settings
import threading

if __name__ == "__main__":
    settings.a = 0
    print(settings.a)
    def get_and_set_settings1():
        # print(settings)
        settings.a += 1
        print(settings.a)

    def get_and_set_settings2():
        # print(settings)
        settings.a -= 1
        print(settings.a)
    threads1 = []
    for _ in range(500):  # Create 5 threads
        thread = threading.Thread(target=get_and_set_settings1)
        threads1.append(thread)
        thread.start()
        print(settings.a)
    threads2 = []
    
    for _ in range(500):  # Create 5 threads
        thread = threading.Thread(target=get_and_set_settings2)
        threads2.append(thread)
        thread.start()
        print(settings.a)

    for thread in threads1:
        thread.join()
    for thread in threads2:
        thread.join()
    print(settings)
