## Simple Shutdown Tracker

**Description**

A Python-based Telegram bot that monitors power outages for users by checking URLs and IPv4 addresses at regular intervals. This project is designed to be:

- **User-friendly:** Easy to set up and use for monitoring critical infrastructure or personal internet connectivity.
- **Configurable:** Supports adding and managing URLs/IP addresses, allowing customization based on individual needs.
- **Informative:** Provides detailed outage reports, including duration, start/end times, and historical data.

**Getting Started**

1. **Prerequisites:**
   - Docker: Install Docker Desktop or Docker Engine ([https://www.docker.com/get-started](https://www.docker.com/get-started))
   - Docker Hub account (optional, but recommended for sharing and updates)

2. **Clone the Repository:**

   ```bash
   git clone https://github.com/trikrapka/power-outage-tracker-router/git
   cd power-outage-tracker-router
   ```

3. **Set Up Environment Variables:**

   - Create a `.env` file in the project's root directory with the following line, replacing `<YOUR_BOT_TOKEN>` with your actual Telegram bot token:

     ```
     TG_BOT_TOKEN=<YOUR_BOT_TOKEN>
     ```

   **Important:** Do not commit the `.env` file to your Git repository.


4. **Run the Bot in Docker:**


   ```bash
   docker compose up -d --build
   ```

5. **View Logs:** Use `docker logs powerbot` to view the bot's logs.

**Using the Bot**

1. **Add the Bot to Your Telegram Chat**

   Use the Telegram app to search for `@your_bot_username` (replace with your bot's username) and start a chat with it.

2. **Start Monitoring URLs or IP Addresses**

   Use the following commands:

   - `/start`: Initiates the bot and provides instructions.
   - `/set_url <URL>`: Adds a URL to the monitoring list (maximum of 2 URLs allowed).
   - `/set_ip <IP_ADDRESS>`: Adds an IPv4 address to the monitoring list (maximum of 2 IP addresses allowed).
   - `/list_urls`: Lists all monitored URLs.
   - `/list_ips`: Lists all monitored IP addresses.
   - `/delete_url <URL>`: Removes a URL from the monitoring list.
   - `/delete_ip <IP_ADDRESS>`: Removes an IP address from the monitoring list.

**Additional Features**

- **Weekly Reports:** On Sundays at 11 PM (UTC), the bot sends weekly outage reports for each monitored entity, detailing shutdown counts, average length, longest and shortest shutdowns, and total downtime.

**Configuration**

- The maximum number of URLs and IP addresses that can be monitored is configurable in the `MAX_URLS` and `MAX_IPS` constants in the `bot.py` file (default: 2).
- The monitoring interval (in seconds) is configurable in the `MONITORING_INTERVAL` constant in `bot.py` (default: 60 seconds).
- Logging levels and behavior can be adjusted in the `logging` configuration within `bot.py`.
- The container's time zone can be set using the `-e TZ=Europe/Kiev` option during `docker run` (example: Europe/Kiev).

The provided `Dockerfile` creates a minimal image based on `python:3.9-slim`:
