# SocialHub Manager (Windows starter)

A Windows desktop starter for planning content across Facebook, Instagram, YouTube and WhatsApp Business. It builds on GitHub Actions; you do not need to install Node.js or Python on your own PC.

## Important current scope
This first build includes:
- Modern desktop dashboard and post queue
- Create drafts and schedule local content records
- Caption/hashtag starter suggestions
- CSV export
- Local SQLite database under `%USERPROFILE%\SocialHubManager\socialhub.db`
- A GitHub Actions workflow that builds `SocialHubManager.exe`

**It does not yet connect to live social accounts.** It does not actually upload posts or fetch real views/followers/likes/comments. Scheduled items become `Needs API setup` when due rather than pretending they were published. Live publishing and analytics require official API OAuth flows, app credentials, permissions, and testing; those credentials should not be hard-coded into this public repository.

## Build EXE from GitHub
1. Create a new GitHub repository (e.g. `socialhub-manager`).
2. Upload all files and folders from this ZIP. Make sure `.github/workflows/build-windows.yml` is included.
3. Open the repository's **Actions** tab.
4. Select **Build SocialHub Manager for Windows**.
5. Click **Run workflow** (or push a commit to `main`).
6. Open the completed workflow run and download artifact **SocialHubManager-Windows**.
7. Extract the downloaded artifact ZIP and run `SocialHubManager.exe` on Windows.

No local Node.js/Python/command line required. GitHub account is required. The first Windows build may show a SmartScreen warning because the EXE is not code-signed.

## Official API requirements and limitations
### Facebook
- Use Meta for Developers and a Meta app.
- Publishing is for Pages using a Page access token and permissions such as `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
- App Review / business verification may be needed when serving other users or requesting advanced permissions.
- Personal profile posting is not generally available like Page posting through the standard Pages API.

### Instagram
- Use a Professional (Business or Creator) account and configure the relevant Instagram API login flow.
- Publishing/insights require relevant permissions, such as `instagram_basic`, `instagram_content_publish`, and where needed `instagram_manage_insights`.
- Instagram API publishing has media-format and product-specific limitations. Some flows require the media URL to be publicly reachable.
- Personal consumer accounts are not supported by the classic Facebook Login Instagram API.

### YouTube
- Create a Google Cloud project and enable YouTube Data API v3.
- OAuth scope `https://www.googleapis.com/auth/youtube.upload` allows uploads; YouTube Analytics uses `https://www.googleapis.com/auth/yt-analytics.readonly`.
- OAuth consent / Google verification can be required. API quota and project restrictions apply.
- Video uploads can be set private/unlisted/public; analytics data is available only for authorized channel content.

### WhatsApp Business
- Use Meta WhatsApp Business Platform Cloud API, a business phone number, and valid access credentials.
- WhatsApp is a messaging channel, not a public social feed. It can send approved template messages and supported media to recipients subject to WhatsApp policies and opt-in rules.
- Business-initiated conversations generally require approved templates; pricing and messaging limits may apply.

## Security
- Never commit app secrets, refresh tokens, access tokens, or phone credentials to GitHub.
- The app stores local planning records in a SQLite database on your PC.
- This starter is not production-ready for multi-user account management. Live integrations should be added one platform at a time and tested with official developer accounts.

## Documentation
- Meta Instagram API: https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api
- YouTube video upload: https://developers.google.com/youtube/v3/docs/videos/insert
- YouTube Analytics: https://developers.google.com/youtube/analytics
- Google OAuth installed apps: https://developers.google.com/youtube/reporting/guides/authorization/installed-apps
- Meta Pages permissions: https://developers.facebook.com/docs/permissions/
- WhatsApp Cloud API: https://developers.facebook.com/docs/whatsapp/cloud-api/
