import requests, time

url: str = f"http://host.docker.internal:8042/changes"

while True:

    try:

        print(requests.get(url).text)

    except requests.exceptions.ConnectionError as ce:

        pass

    time.sleep(1)