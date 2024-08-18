# Crypto Price Notifier

This project allows users to get updated cryptocurrency prices and monitor the market trends.

## System Requirements:
- **Python Version**: 3.12.5
- **PostgreSQL Database Server**
- **RabbitMQ**: For messaging between components.
- **API**: An external API is used to fetch the updated cryptocurrency prices.

## Usage:
1. **Registration**: Users need to register to create an account.
2. **Login**: After registration, log in to access the system.
3. **Configuration**:
   - Navigate to the "Configuration" page.
   - Select the cryptocurrencies you're interested in.
   - Choose how often you want to get updates: **Minutes**, **Hourly**, or **Daily**.
   - Click the "Save" button to store your preferences.
4. **Prices Report**: Click on "Prices Report" to view the highest and lowest prices of your selected cryptocurrencies.
5. **Logout**: Click the "Logout" button to exit the application.

## Additional Information:
- The app ensures real-time updates and analysis, enabling users to stay informed of market fluctuations.
- Make sure the PostgreSQL database and RabbitMQ server are properly configured before running the application.

