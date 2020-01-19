from server_helper.server_helper_base import ServerHelperBase


class ServerHelperExamination:
    URL = 'https://mooped.net/local/its/tests/agentaction/'

    hash_id = None

    def make_step(self, passive, active):
        return ServerHelperBase.send_request(
            self.URL,
            {
                'hash': self.hash_id,
                'passive': passive,
                'active': active,
                'checksituations': 1
            }
        )

    def __init__(self, hash_id):
        print('Examination:')
        print('\tHash id:', hash_id)
        self.hash_id = hash_id
