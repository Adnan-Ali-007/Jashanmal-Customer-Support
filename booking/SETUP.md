# Google Calendar Integration Setup

## Step 1: Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

## Step 2: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External (for testing)
   - App name: "Jashanmal Support Bot"
   - User support email: your email
   - Developer contact: your email
   - Add scope: `https://www.googleapis.com/auth/calendar`
   - Add test users: your email
4. Create OAuth client ID:
   - Application type: "Desktop app"
   - Name: "Jashanmal Calendar"
5. Download the JSON file
6. Rename it to `credentials.json`
7. Place it in the `booking/` folder

## Step 3: Install Dependencies

```bash
venv\Scripts\pip.exe install -r requirements.txt
```

## Step 4: First-Time Authentication

Run this test script to authenticate:

```bash
venv\Scripts\python.exe booking/test_calendar.py
```

This will:
- Open a browser window
- Ask you to sign in with Google
- Request calendar permissions
- Save a token for future use

## Step 5: Test the Integration

The token will be saved in `booking/token.pickle` and reused automatically.

## Troubleshooting

**Error: credentials.json not found**
- Make sure you downloaded the OAuth credentials
- Place them in `booking/credentials.json`

**Error: Access denied**
- Make sure you added yourself as a test user in OAuth consent screen
- Check that Google Calendar API is enabled

**Error: Token expired**
- Delete `booking/token.pickle`
- Run the test script again to re-authenticate

## Security Notes

- Never commit `credentials.json` or `token.pickle` to git
- These files contain sensitive authentication data
- Add them to `.gitignore`
