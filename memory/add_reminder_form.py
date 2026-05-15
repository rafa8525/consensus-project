from flask import Flask, request, render_template_string
import datetime
import os

app = Flask(__name__)

FORM_HTML = """
<!doctype html>
<title>Add a Reminder</title>
<h2>Enter a Reminder Command</h2>
<form method=post>
  <textarea name=command cols=50 rows=3 placeholder="Remind me to water the lawn when I get home"></textarea><br>
  <input type=submit value="Submit">
</form>
{% if result %}
  <h4>Result:</h4>
  <pre>{{ result }}</pre>
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def add_reminder():
    result = None
    if request.method == 'POST':
        command = request.form['command']
        timestamp = datetime.datetime.utcnow().isoformat()
        # Save command to a file for the Project Manager agent
        with open('commands_queue.txt', 'a') as f:
            f.write(f"{timestamp}::{command}\n")
        result = f"Command received and queued: {command}"
    return render_template_string(FORM_HTML, result=result)

if __name__ == '__main__':
    app.run()
