import requests as req


class ServerHelperBase:
    @staticmethod
    def send_request(url, params):
        response = req.get(
            url,
            params,
            # proxies={
            #     "http": "http://10.0.0.4:3128",
            #     "https": "https://10.0.0.4:3128"
            # },
            verify=False
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None
