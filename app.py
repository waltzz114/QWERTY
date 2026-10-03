import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


# =====================================================
# PARKING DATA
# =====================================================

parking_data = {
    "slots": [0, 0, 0, 0],
    "entry": 0,
    "exit": 0,
    "lastSeen": 0
}


# =====================================================
# WEBSITE
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# ESP32 SENDS DATA HERE
# =====================================================

@app.route("/sensor", methods=["POST"])
def sensor():

    global parking_data

    try:

        data = request.get_json()

        print("Received from ESP32:")
        print(data)

        # Check that slots exist
        if "slots" not in data:
            return jsonify({
                "success": False,
                "error": "Missing slots"
            }), 400

        # Make sure there are exactly 4 slots
        if len(data["slots"]) != 4:
            return jsonify({
                "success": False,
                "error": "There must be 4 slots"
            }), 400


        # Save parking information

        parking_data = {

            "slots": [
                int(data["slots"][0]),
                int(data["slots"][1]),
                int(data["slots"][2]),
                int(data["slots"][3])
            ],

            "entry": int(
                data.get("entry", 0)
            ),

            "exit": int(
                data.get("exit", 0)
            ),

            "lastSeen": time.time()

        }


        print(
            "Parking state:",
            parking_data
        )


        return jsonify({

            "success": True,

            "message":
                "Parking data received",

            "data":
                parking_data

        })


    except Exception as error:

        print(
            "Error:",
            error
        )

        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 400


# =====================================================
# WEBSITE GETS CURRENT PARKING DATA
# =====================================================

@app.route("/value", methods=["GET"])
def value():

    global parking_data


    # Check when ESP32 last sent data

    current_time = time.time()

    last_seen = parking_data["lastSeen"]


    # ESP32 is considered online if it
    # contacted the server within 10 seconds

    if last_seen == 0:

        online = False

    else:

        online = (
            current_time - last_seen
        ) < 10


    return jsonify({

        "slots":
            parking_data["slots"],

        "entry":
            parking_data["entry"],

        "exit":
            parking_data["exit"],

        "online":
            online,

        "lastSeen":
            parking_data["lastSeen"]

    })


# =====================================================
# SERVER START
# =====================================================

if __name__ == "__main__":

    import os

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )