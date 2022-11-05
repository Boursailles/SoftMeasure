import threading
import time

# Pour le programme:
# Créer les threads des plots avant de lancer ceux du PS et VNA. Ensuite, entrer les event.set dans le thread function du PS et à chaque fin du VNA.

# Peut-être meilleure solution, à chaque fois que le fichier est modifié:
# https://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes

event = threading.Event()
x = 0
def myFunction():
    global x
    while True:
        event.wait()
        if event.is_set():
            print("event is set : " + str(x))
            x += 1
            event.clear()

th1 = threading.Thread(target=myFunction)
th1.start()
while True:
    event.set()
    time.sleep(1)