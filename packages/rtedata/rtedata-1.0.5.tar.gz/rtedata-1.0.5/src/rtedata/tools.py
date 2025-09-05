import logging

class Logger:
    def __init__(self):
        self.name = "rtedata"
        self.level = logging.INFO
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        
        if not self.logger.handlers:
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
