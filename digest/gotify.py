import requests

def send_gotify_notification(base_url, app_token, title, message, priority=5):
    """
    Sends a message to a Gotify server.
    
    :param base_url: The URL of your Gotify server (e.g., 'https://gotify.example.com')
    :param app_token: The application token generated in the Gotify UI
    :param title: The title of the notification
    :param message: The body of the notification
    :param priority: Priority level (0=min, 5=normal, 10=max)
    """
    
    # Construct the full URL
    url = f"{base_url}/message?token={app_token}"
    
    # Define the payload
    payload = {
        "title": title,
        "message": message,
        "priority": priority
    }
    
    try:
        response = requests.post(url, json=payload)
        
        # Raise an exception if the request was unsuccessful (e.g., 404 or 500)
        response.raise_for_status()
        
        print("Notification sent successfully!")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")
        return None
