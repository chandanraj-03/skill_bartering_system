# Skill Bartering System

A modern web application for exchanging skills between university students. Built with Streamlit and MySQL.

## ✨ Features

### Core Features
- User registration and authentication
- Skill listing and browsing
- Exchange proposals and management
- Real-time messaging
- Rating system
- Modern UI with responsive design

### 🆕 New Features (v2.0)
- **📊 Analytics Dashboard**: Comprehensive visualizations of your activity
  - Skills distribution charts
  - Exchange status tracking
  - Achievement badges (Gold, Silver, Bronze, Newcomer)
  - Ratings visualization
- **📸 Profile Picture Upload**: Customize your profile with a photo
- **📝 Bio Editing**: Add and edit your personal bio
- **🔗 Social Media Links**: Connect LinkedIn, GitHub, Twitter, and Portfolio
- **🔔 Notification Badge**: Real-time unread message counter
- **📎 File Attachments**: Send documents, images, and videos in messages
- **👥 Group Exchanges**: Multi-user skill exchange sessions

## Installation (Local Development)

1. Clone the repository:
```bash
git clone <repository-url>
cd skill_bartering_system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=skill_barter_db
MYSQL_PORT=3306
SECRET_KEY=your_secret_key
```

4. Set up the database:
```bash
python setup_database.py
```

5. Run database migrations (for new features):
```bash
python database/migrations.py
```

6. Run the application:
```bash
streamlit run app.py
```

## Deployment to Streamlit Cloud

### Prerequisites
- A MySQL database service (recommended: [PlanetScale](https://planetscale.com) - free tier available)
- A Streamlit Cloud account

### Steps

1. **Set up external MySQL database:**
   - Sign up for PlanetScale (or similar MySQL service)
   - Create a new database
   - Note down the connection details (host, username, password, database name)

2. **Deploy to Streamlit Cloud:**
   - Fork this repository to your GitHub account
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account and select the forked repository
   - In the deployment settings, add the following secrets:
     ```
     MYSQL_HOST = "your-planetscale-host"
     MYSQL_USER = "your-planetscale-username"
     MYSQL_PASSWORD = "your-planetscale-password"
     MYSQL_DATABASE = "your-planetscale-database"
     MYSQL_PORT = 3306
     SECRET_KEY = "your-random-secret-key"
     ```
   - Click "Deploy"

3. **Initialize the database:**
   - After deployment, access your app URL
   - Run the database setup script by temporarily modifying `app.py` to call `db_manager.initialize_database()` on startup (remove after setup)

### Environment Variables

For local development, use `.env` file. For Streamlit Cloud, use the secrets management in the deployment settings.

Required environment variables:
- `MYSQL_HOST`: Database host
- `MYSQL_USER`: Database username
- `MYSQL_PASSWORD`: Database password
- `MYSQL_DATABASE`: Database name
- `MYSQL_PORT`: Database port (default: 3306)
- `SECRET_KEY`: Random secret key for session security

## Usage

### Getting Started
1. Register with your university email (@geu.ac.in or @gehu.ac.in)
2. Upload a profile picture and add your bio
3. Add your skills to the platform
4. Add social media links to showcase your work

### Finding Skills
5. Browse and search for skills offered by others
6. Use filters to find specific categories
7. View user profiles and ratings

### Exchanging Skills
8. Propose skill exchanges with other users
9. Accept or reject incoming exchange requests
10. Chat with exchange partners (with file attachments!)
11. Complete exchanges and rate your partners

### Tracking Progress
12. View your analytics dashboard
13. Check your achievement badges
14. Monitor exchange statistics
15. See skills distribution charts

### Group Exchanges
16. Create group skill exchange sessions
17. Invite multiple participants
18. Collaborate in group learning

## Database Schema

The application uses MySQL with the following main tables:
- `users`: User accounts, profiles, bios, social links, and profile pictures
- `skills`: Skills offered by users
- `exchanges`: Skill exchange proposals and status (individual and group)
- `exchange_participants`: Participants in group exchanges
- `messages`: Communication between exchange partners (with file attachments)
- `ratings`: User ratings for completed exchanges

### New Fields (v2.0)
**Users Table:**
- `profile_image` (LONGTEXT): Base64 encoded profile picture
- `linkedin_url`, `github_url`, `twitter_url`, `portfolio_url` (VARCHAR): Social media links

**Messages Table:**
- `attachment_data` (LONGTEXT): Base64 encoded file data
- `attachment_name`, `attachment_type` (VARCHAR): File metadata

## Technology Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python 3.8+
- **Database**: MySQL
- **Visualizations**: Plotly
- **Image Processing**: Pillow (PIL)
- **Authentication**: Custom password hashing

## New Features Documentation

For detailed information about all new features, see [NEW_FEATURES.md](NEW_FEATURES.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Version History

### v2.0 (November 2025)
- Added Analytics Dashboard with interactive charts
- Implemented Profile Picture Upload
- Added Bio Editing functionality
- Integrated Social Media Links
- Added Notification Count Badge
- Implemented File Attachments for messages
- Enhanced UI/UX with better styling

### v1.0 (Initial Release)
- Core skill bartering functionality
- User authentication
- Individual exchanges
- Basic messaging
- Rating system
- Group exchanges

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or suggestions, please create an issue in the repository or contact the development team.

---

**Built with ❤️ for the university community**
