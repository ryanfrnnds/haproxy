#!/usr/bin/env python3
from flask import Flask
import os
from agent_metrics import cpu_pct, mem_pct

app = Flask(__name__)
NAME = os.getenv("API_NAME", "api-unknown")

def calc_free_score() -> int:
    busy = max(cpu_pct(), mem_pct())
    return max(1, min(100, int(round(100 - busy))))

@app.route("/")
def hello():
    return f"Hello World from {NAME}!\n", 200

@app.route("/health")
def health():
    return f"{calc_free_score()}%\n", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
