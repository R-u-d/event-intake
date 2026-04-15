import json
import traceback

# FANCYLOG exception-tracker
def capture_exception(error, request_id, endpoint, safe_input):
    log = {
        "error_message": str(error),
        "stack": traceback.format_exc(),
        "requestId": request_id,
        "endpoint": endpoint,
        "input": safe_input
    }

    print("FANCYLOG", json.dumps(log))