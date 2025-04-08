from flask import Flask, request, jsonify
import zmq
import logging
from typing import Any
from config import ZMQ_PUB_BIND_ADDR, LOCAL_DOTA_HOST, LOCAL_DOTA_PORT, DEBUG_MODE

# Logging Setup
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Flask App Setup
app = Flask(__name__)


# ZeroMQ Setup
def setup_pub_socket(bind_addr: str) -> zmq.Socket:
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(bind_addr)
    logging.info(f"ZeroMQ PUB socket bound to {bind_addr}")
    return socket


pub_socket = setup_pub_socket(ZMQ_PUB_BIND_ADDR)


# Routes
@app.route("/", methods=["POST"])
def gsi() -> Any:
    data = request.json
    if not data:
        return jsonify({"status": "no data"}), 400

    logging.info("[GSI] Received update")
    pub_socket.send_json(data)
    return jsonify({"status": "published"})


@app.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok"})


# --- Run the App ---
if __name__ == "__main__":
    logging.info(
        f"Dota GSI Server running at http://{LOCAL_DOTA_HOST}:{LOCAL_DOTA_PORT}/"
    )
    app.run(host=LOCAL_DOTA_HOST, port=LOCAL_DOTA_PORT, debug=DEBUG_MODE)
