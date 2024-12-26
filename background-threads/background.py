import threading
import time
import random
import os

# Global stop marker file path
STOP_MARKER_FILE = "stop_marker.txt"


class BaseWorker:
    def __init__(self, name, interval_range, startup_delay_range):
        """
        Base worker class to define common functionality.
        :param name: Name of the worker.
        :param interval_range: Tuple (min, max) for the interval between executions.
        :param startup_delay_range: Tuple (min, max) for random startup delay.
        """
        self.name = name
        self.interval_range = interval_range
        self.startup_delay_range = startup_delay_range
        self.last_run_time = 0  # Time when work was last done

    def run(self):
        """Main loop for the worker."""
        startup_delay = random.uniform(*self.startup_delay_range)
        print(f"{self.name}: Delaying startup for {startup_delay:.2f} seconds.")
        time.sleep(startup_delay)

        while not self.should_stop():

            # Check if enough time has passed to do work
            time_since_last_work = time.time() - self.last_run_time
            if time_since_last_work >= random.randint(*self.interval_range):
                self.do_work()
                self.last_run_time = time.time()  # Update last work time

            # Wake up every 10 seconds to see if we need to stop
            time.sleep(10)

        print(f"{self.name} received stop signal. Exiting...")

    def do_work(self):
        """Override this method in subclasses to define the actual work."""
        raise NotImplementedError("Subclasses must implement this method.")

    @staticmethod
    def should_stop():
        """Check for the existence of the stop marker file."""
        return os.path.exists(STOP_MARKER_FILE)


class SampleWorker(BaseWorker):
    def __init__(self, name, interval_range, startup_delay_range, context):
        super().__init__(name, interval_range, startup_delay_range)
        self.context = context

    def do_work(self):
        """Perform the work specific to this worker."""
        print(f"{self.name} is doing work...")
        time.sleep(random.randint(1, 5))
        print(f"{self.name} finished work.")



def start_workers(worker_configs):
    threads = []
    for config in worker_configs:
        worker_class = config.pop("class")
        worker = worker_class(**config)
        thread = threading.Thread(target=worker.run)
        thread.daemon = False
        thread.start()
        threads.append(thread)

    # Now wait for all threads to finish
    for thread in threads:
        thread.join()
    return threads


def main():
    context = {"name": "theContext", "aString": "a string", "anInteger": 3}
    worker_configs = [
        {
            "class": SampleWorker,
            "name": "Worker1",
            "interval_range": (5, 10),
            "startup_delay_range": (5, 10),
            "context": context
        },
        {
            "class": SampleWorker,
            "name": "Worker2",
            "interval_range": (10, 15),
            "startup_delay_range": (10, 15),
            "context": context
        }
    ]

    workers = start_workers(worker_configs)

    print("All threads have completed, exiting the program.")


if __name__ == "__main__":
    main()
