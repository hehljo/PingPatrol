# PingPatrol

PingPatrol is a simple web-based network monitoring tool written in Python using Flask. It regularly pings a list of devices and can send email notifications if any device becomes unreachable. The web interface allows you to configure devices, set the ping interval, change the language, and adjust the appearance.

## Features

- **Web Interface:** Configure devices, ping interval, language, and appearance via browser.
- **Device Monitoring:** Regularly pings all configured devices and logs their status.
- **Email Notifications:** Sends an email if one or more devices are unreachable (configurable).
- **Multi-language:** Supports German and English.
- **Customizable UI:** Change font and font size in the settings.
- **Log View:** See the latest ping results in the dashboard.

## Requirements

- Python 3.8+
- [Flask](https://flask.palletsprojects.com/)
- [ping3](https://github.com/kyan001/ping3)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/pingpatrol.git
    cd pingpatrol
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Configure environment variables:**

    Create a `.env` file in the project root with the following content:
    ```
    EMAIL_ADDRESS=your_email@gmail.com
    EMAIL_PASSWORD=your_app_password
    EMAIL_RECEIVER=receiver_email@example.com
    DEVICE_FILE=devices.csv
    ```

4. **Create a `devices.csv` file:**

    Each line should contain an IP address and a hostname, separated by a comma:
    ```
    192.168.1.1,Router
    192.168.1.2,Server
    ```

## Usage

Start the application with:

```sh
python pingpatrol.py
```

The web interface will be available at [http://localhost:5050](http://localhost:5050).

## Configuration

- **Devices:** Edit via the web interface or directly in `devices.csv`.
- **Ping interval:** Set in the web interface (in minutes).
- **Language:** Switch between German and English in the settings.
- **Email notifications:** Enable/disable in the settings tab.
- **Font and size:** Change in the settings tab.

## Notes

- The application logs ping results to `log.csv`.
- Email notifications use Gmail SMTP by default. You may need to create an app password for Gmail.
- The ping process runs in a background thread and updates the status at the configured interval.

## License

MIT License

---

**Made with ❤️ for simple network monitoring.**
