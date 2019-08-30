from monitor_agent import agent


monitor = agent.Monitor.create('monitor.log', '15222401953')
usage = monitor.gets(serverip='192.168.161.10', user='root', password='1')
monitor.record(rate=usage)
monitor.dingWarn(token='29d923806d11a9f1836b51c8882e94cda74eded55ccd2aeac9ffa98523e14af0', messages=usage)

