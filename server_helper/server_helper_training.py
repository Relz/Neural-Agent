from server_helper.server_helper_base import ServerHelperBase


class ServerHelperTraining:
    URL = 'https://mooped.net/local/its/game/agentaction/'

    user_id = None
    case_id = None
    map_number = None

    def make_step(self, action):
        return ServerHelperBase.send_request(
            self.URL,
            {
                'userid': self.user_id,
                'caseid': self.case_id,
                'mapnum': self.map_number,
                'passive': action.passive,
                'active': action.active,
                'checksituations': 1
            }
        )

    def __init__(self, user_id, case_id, map_number):
        print('Training:')
        print('\tUser id:', user_id)
        print('\tCase id:', case_id)
        print('\tMap number:', map_number)
        self.user_id = user_id
        self.case_id = case_id
        self.map_number = map_number
