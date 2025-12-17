import logging

def logger_experiment():
  logger = logging.getLogger('lilly_auth')
  #logger.setLevel(logging.DEBUG)
  logger.propagate = False
  # create file handler which logs even debug messages
  fh = logging.FileHandler('my_log_file.log', mode='w', encoding='utf-8', delay=True)

  fh.setLevel(logging.DEBUG)
  # create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.CRITICAL)
  # create formatter and add it to the handlers

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  formatter1 = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter1)
  fh.setFormatter(formatter)
  # add the handlers to logger  
  logger.addHandler(ch)
  logger.addHandler(fh)

  # 'application' code
  logger.debug('debug message')
  logger.info('info message')
  logger.warning('warn message')
  logger.error('error message')
  logger.critical('critical message')
