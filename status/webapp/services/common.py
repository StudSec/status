from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests
import socket
import time
import ssl


class Service:
    def __init__(self):
        self.name = ""
        self.uuid = ""
        self.secret = ""
        self.status = ""
        self.last_updated = 0
        self.report_hook = ""

    def update_test(self):
        pass

    def report(self, message):
        # report to Discord webhook
        print(message)
        pass

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "last_checked": datetime.utcfromtimestamp(self.last_updated).strftime('%Y-%m-%d %H:%M')
        }

    def __iter__(self):
        return iter(self.to_dict().items())


class WebService(Service):
    def __init__(self):
        super().__init__()
        self.url = ""

    def update_test(self):
        self.last_updated = time.time()

        result = self.check_up(self.url)
        if result:
            self.status = "Down"
            self.report(result)
            return

        result = self.check_certificate(self.url)
        if result:
            self.status = "Faulty"
            self.report(result)
            return

    @staticmethod
    def check_up(url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return f"URL is accessible, but returned status code {response.status_code}."
        except requests.exceptions.RequestException as e:
            return f"Failed to connect to the URL: {e}"

    @staticmethod
    def check_certificate(url):
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.netloc if parsed_url.netloc else parsed_url.path

            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssl_sock:
                    cert = ssl_sock.getpeercert()

            # Extract certificate expiration date
            cert_expiry_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            days_until_expiry = (cert_expiry_date - datetime.utcnow()).days

            if days_until_expiry < 0:
                return "The SSL certificate has already expired."
            elif days_until_expiry <= 30:
                return f"The SSL certificate will expire in {days_until_expiry} days."
        except ssl.SSLError as e:
                return f"SSL error: {e}"
