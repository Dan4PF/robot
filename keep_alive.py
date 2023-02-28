from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def main():
    return "Hanime is now alive!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    threads = []
    max_shards = 30
    for i in range(max_shards):
        t = Thread(target=run)
        threads.append(t)
        t.start()