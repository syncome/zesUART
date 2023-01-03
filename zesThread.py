import threading

class FsmThread(threading.Thread):
    def __init__(self, channel, threadID, correlation_id, seq_id, func):
        threading.Thread.__init__(self)
        self.channel = channel
        self.threadID = threadID
        self.func = func
        self.seq_id = seq_id
        self.state = "NOT_STARTED"
        self.condition = threading.Condition()
        self.correlation_id = correlation_id
        self.is_pl_power_on = False
        self.will_power_on = False
    def run(self):
        print("Starting " + self.seq_id)
        self.func(self)
        print("Exiting " + self.seq_id)