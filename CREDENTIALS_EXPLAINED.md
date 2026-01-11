# Neo4j Aura Credentials Explained

## Two Different Logins

### 1. Aura Dashboard Login (Google)
- **What it's for**: Logging into the Neo4j Aura website
- **Username**: Your Google email
- **Password**: Your Google password (or OAuth)
- **Where**: https://console.neo4j.io/

### 2. Database Connection Credentials (What You Need)
- **What it's for**: Connecting your Python code to the Neo4j database
- **Username**: Always `neo4j` (this is the default database user)
- **Password**: The password that was generated when you created the instance
- **Where**: In Developer Hub → Python section

## How to Find Your Database Password

### Method 1: Developer Hub (Easiest)
1. Go to your instance in Aura dashboard
2. Click **"Connect"** → **"Developer hub"**
3. Click **"Python"**
4. Look for the password field
5. If it's hidden, click **"Show"** or **"Reveal"** button
6. Copy that password

### Method 2: Reset Password
If you can't find the password:
1. Go to your instance details page
2. Look for **"Reset Password"** or **"Change Password"** option
3. Click it to generate a new password
4. **IMPORTANT**: Copy it immediately - you won't see it again!

## What Goes in Your .env File

```env
# This is the database connection, NOT your Google login
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j                    # ← Always "neo4j"
NEO4J_PASSWORD=the_password_from_developer_hub  # ← From Python section
```

## Quick Checklist

- [ ] I'm logged into Aura with Google (for the website)
- [ ] I found the connection URI in Developer Hub → Python
- [ ] I found/revealed the password in Developer Hub → Python
- [ ] I copied the username (it's `neo4j`)
- [ ] I put all three in my `.env` file

## Still Can't Find It?

If you can't see the password:
1. Try clicking on your instance name to open details
2. Look for a "Connection" or "Credentials" tab
3. Or use the "Reset Password" option to get a new one

---

**Remember**: Your Google login is separate from the database credentials. You need the database credentials (username: `neo4j` + the generated password) for your `.env` file.

