import json
import logging
import requests
import paramiko


class Monitor(object):
    """
    dingWarn function is used of talk to people on groups.
    """
    def __init__(self, logPath, people):
        self.logPath = logPath
        self.people = people

    @classmethod
    def create(cls, logPath, people):
        return cls(logPath=logPath, people=people)

    def dingWarn(self, token, messages):
        """
        dingtalk warning to dingClient and @people
        :return: messages
        """
        api = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(token)
        header = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "text",
            "text": {"content": messages},
            'at': {'atMobiles': [self.people]},
            'isAtAll': 'false'
        }
        requests.post(url=api, headers=header, data=json.dumps(data).encode('utf-8'))

    def record(self, rate):
        """
        record over limit's items
        :param rate: dict type value
        :return: log file
        """
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(pathname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S', level=logging.WARNING, filename=self.logPath,
            filemode='a'
        )
        if rate['cpu'] > 0:
            logging.warning('cpu rate over limit! At: {}'.format(rate['cpu']))
        if rate['memory'] > 85:
            logging.warning('memory rate over limit! At: {}'.format(rate['memory']))
        if rate['disk'] > 90:
            logging.warning('disk rate over limit! At: {}'.format(rate['disk']))

    @staticmethod
    def gets(serverip, user, password):
        """
        get remote server cpu/memory/disk usage rate.
        :param serverip: ip address
        :param user: root
        :param password: password
        :return: rate info
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=serverip, username=user, password=password)
        try:
            _, cpu, _ = client.exec_command("vmstat | awk 'NR==3{ print $15 }'")
            _, mtotal, _ = client.exec_command("free -m | awk 'NR==2{ print $2 }'")
            _, mused, _ = client.exec_command("free -m | awk 'NR==2{ print $3 }'")
            _, dtotal, _ = client.exec_command("df | awk 'NR==2{ print $2 }'")
            _, dused, _ = client.exec_command("df | awk 'NR==2{ print $3 }'")
            rate, monitor = {}, [100 - int(cpu.read().decode('utf-8')),
                                 int(mused.read().decode('utf-8')) * 10 // int(mtotal.read().decode('utf-8')) * 10,
                                 int(dused.read().decode('utf-8')) * 10 // int(dtotal.read().decode('utf-8')) * 10]
            rate.setdefault('cpu', monitor[0])
            rate.setdefault('memory', monitor[1])
            rate.setdefault('disk', monitor[2])
        finally:
            client.close()
        return rate

