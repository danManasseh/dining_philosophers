import threading
import random
import time

class Philosopher(threading.Thread):
    table_list = []
    def __init__(self, name, table_number, left_fork, right_fork, table_lock, sixth_table, deadlock_flag, last_to_sixth, end_flag, join_time):
        threading.Thread.__init__(self)
        self.name = name
        self.table_number = table_number
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.table_lock = table_lock
        self.sixth_table = sixth_table
        self.deadlock_flag = deadlock_flag
        self.left_attempts = 0
        self.last_to_sixth = last_to_sixth
        self.end_flag = end_flag
        self.left_fork_acquired = False
        self.right_fork_acquired = False
        self.join_time = join_time


    def think(self):
        print(f"{self.name} is thinking.")
        time.sleep(random.randint(0, 10))

    def pick_up_forks(self):
        while True:
            self.table_lock.acquire()
            if self.left_fork.acquire(blocking=False):
                print(f"{self.name} picked up the left fork.")
                time.sleep(4)
                if self.right_fork.acquire(blocking=False):
                    print(f"{self.name} picked up the right fork.")
                    self.left_attempts = 0 
                    self.table_lock.release()
                    return True
                else:
                    self.left_fork.release()
                    self.left_attempts += 1
            else:
                self.left_attempts += 1
            self.table_lock.release()
            if self.left_attempts >= 4:
                print(f"{self.name} failed to pick up the left fork. Stopping philosopher.")
                self.end_flag.set()
                return False
            time.sleep(random.randint(0, 1))

    def eat(self):
        print(f"{self.name} is eating.")
        time.sleep(random.randint(0, 5))

    def put_down_forks(self):
        if self.left_fork_acquired :
            self.left_fork.release()
            self.left_fork_acquired = False
        if self.right_fork_acquired:
            self.right_fork.release()
            print(f"{self.name} put down the forks.")
            self.right_fork_acquired = False

    def move_to_sixth_table(self):
        if self.table_number not in self.table_list:
            self.table_list.append(self.table_number)
            self.sixth_table.acquire()
            self.deadlock_flag.set()
            self.put_down_forks()
            with self.table_lock:
                self.last_to_sixth[0] = self.name
                if self.join_time[0] is None:
                    self.join_time[0] = time.time()
            self.sixth_table.release()
            self.end_flag.set()
            print(f"{self.name} moved to the sixth table.")

        

    def run(self):
        while not self.deadlock_flag.is_set():
            self.think()
            if self.pick_up_forks():
                self.eat()
                self.put_down_forks()
            if self.end_flag.is_set():
                break
        self.move_to_sixth_table()

def simulate_dining_philosophers():
    num_tables = 5
    num_philosophers_per_table = 5

    forks = [threading.Lock() for _ in range(num_tables)]
    table_lock = threading.Lock()
    sixth_table = threading.Semaphore(num_philosophers_per_table)
    deadlock_flag = threading.Event()
    last_to_sixth = [None]
    join_time = [None]
    end_flag = threading.Event()
    

    philosophers = []
    for table_number in range(num_tables):
        for philosopher_number in range(num_philosophers_per_table):
            philosopher_name = chr(65 + table_number * num_philosophers_per_table + philosopher_number)
            left_fork = forks[table_number]
            right_fork = forks[(table_number + 1) % num_tables]
            philosopher = Philosopher(philosopher_name, table_number, left_fork, right_fork, table_lock, sixth_table, deadlock_flag, last_to_sixth, end_flag, join_time)
            philosophers.append(philosopher)
            philosopher.start()

    start_time = time.time()
    for philosopher in philosophers:
        philosopher.join()

    end_time = round(join_time[0] - start_time, 2)

    print("All philosophers have reached a deadlock.")
    print("Last philosopher to join the sixth table:", last_to_sixth[0])
    print(f"Duration until 5th philosopher joined the sixth table: {end_time} seconds")


if __name__ == "__main__":
    simulate_dining_philosophers()
