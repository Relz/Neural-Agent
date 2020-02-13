from server_helper.server_helper_base import ServerHelperBase


class ServerHelperTournament:
    URL = 'https://mooped.net/local/its/tournament/agentaction/'

    user_id = None
    tournament_id = None

    def make_step(self, action):
        return ServerHelperBase.send_request(
            self.URL,
            {
                'userid': self.user_id,
                'tid': self.tournament_id,
                'passive': action.passive,
                'active': action.active,
                'checksituations': 1
            }
        )

    def __init__(self, user_id, tournament_id):
        print('Tournament:')
        print('\tUser id:', user_id)
        print('\tTournament id:', tournament_id)
        self.user_id = user_id
        self.tournament_id = tournament_id
