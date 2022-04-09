from flask import Flask, request
import json
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def root():
    return open(os.path.join(app.root_path, "form.html")).read()


@app.route("/action", methods=["POST"])
def action():
    if request.method == "POST":
        # read from FORM data
        act = request.form.get("act")
        landmark = request.form.get("landmark")

        return json.dumps({"act": act, "landmark": landmark})


if __name__ == "__main__":
    app.run()
