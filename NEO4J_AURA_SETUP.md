# Neo4j Aura Setup Guide

## Step-by-Step Instructions

### 1. Create a Neo4j Aura Account

1. Go to https://neo4j.com/cloud/aura/
2. Click **"Start Free"** or **"Sign Up"**
3. Sign up with:
   - Email address
   - Password
   - Or use Google/GitHub OAuth

### 2. Create a New Database Instance

1. Once logged in, click **"Create Instance"** (this is the same as creating a database)
2. Choose **"Free"** tier (good for development/testing)
   - Free tier includes: 1 database, 50K nodes, 175K relationships
   - Or choose a paid tier for production
3. Fill in the form:
   - **Database Name**: e.g., "knowledge_base" or "agent_memory"
   - **Region**: Choose closest to you (e.g., US East, EU West)
   - **Cloud Provider**: AWS (default) or GCP
4. Click **"Create Instance"** or **"Create"**

### 3. Wait for Instance Creation

- This takes 2-3 minutes
- You'll see a progress indicator
- You'll get an email when it's ready
- The instance will appear in your dashboard

### 4. Get Your Connection Details

Once the instance is ready, you have a few ways to get connection info:

**Method 1: From the Instance Card**
1. Find your instance in the dashboard (it will show as "Running" or "Active")
2. Click on the instance name/card to open details
3. Look for a **"Connection Details"** or **"Connection Info"** section
4. You'll see:
   - **URI**: Something like `neo4j+s://xxxxx.databases.neo4j.io`
   - **Username**: Usually `neo4j`
   - **Password**: Click "Show Password" or "Reveal Password" to see it (save this!)

**Method 2: From the Connect Button**
1. Click the **"Connect"** button (top right, with dropdown arrow)
2. Select **"Query"** or look for connection info in the dropdown
3. Or click on your instance, then look for connection details

**Method 3: Developer Hub**
1. Click **"Connect"** → **"Developer hub"**
2. Look for connection strings or connection info section
3. You should see the URI and credentials there

**What to Look For:**
- **Connection URI**: Starts with `neo4j+s://` or `neo4j://`
- **Username**: Typically `neo4j`
- **Password**: You may need to click "Show" or "Reveal" to see it

### 5. Update Your .env File

Edit your `.env` file with the Aura connection details:

```env
# Neo4j Aura Configuration
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_aura_password_here
```

**Important Notes:**
- Use the full URI including `neo4j+s://` (the `+s` means SSL/secure)
- The URI format is: `neo4j+s://[instance-id].databases.neo4j.io`
- Keep your password secure - you can't retrieve it later (only reset it)

### 6. Test the Connection

```bash
python -c "from db.connection import get_neo4j_driver; driver = get_neo4j_driver(); print('✓ Connected to Aura!')"
```

### 7. Initialize the Schema

```bash
python init_db.py
```

You should see:
```
✓ Connected to Neo4j
✓ Vector indexes created successfully
✓ Constraints created successfully
✓ Schema initialization complete
```

## Finding Connection Details (Step-by-Step)

If you're having trouble finding the connection info, try this:

1. **Look at your instance card** in the main dashboard
   - Click directly on the instance name/box
   - This opens the instance details page

2. **Check the right sidebar or info panel**
   - Connection details are often in a panel on the right
   - Look for tabs like "Details", "Connection", or "Info"

3. **Look for a "Connection URI" or "Connection String" field**
   - It will look like: `neo4j+s://[random-id].databases.neo4j.io`
   - Copy this entire string

4. **Find the password**
   - May be hidden behind "Show Password" or "Reveal" button
   - Click to reveal it
   - **IMPORTANT**: Copy this immediately - you may not be able to see it again!

5. **If you can't find it:**
   - Click "Connect" → "Query" to open Neo4j Browser
   - The connection string might be shown there
   - Or check the "Developer hub" option

## Aura Dashboard Features

Once set up, you can:

- **View Database**: Click "Open" or "Connect" → "Query" to access Neo4j Browser
- **Monitor Usage**: See node/relationship counts on the instance card
- **Reset Password**: If you lose it, there's usually a "Reset Password" option
- **Pause/Resume**: Free tier can be paused when not in use
- **Upgrade**: Scale up when needed

## Troubleshooting

### Connection Timeout
- Check your firewall allows outbound connections
- Verify the URI is correct (should start with `neo4j+s://`)

### Authentication Failed
- Double-check username (usually `neo4j`)
- Verify password (copy-paste to avoid typos)
- Try resetting password in Aura dashboard

### SSL Certificate Issues
- Aura uses SSL by default (`neo4j+s://`)
- The Neo4j driver handles SSL automatically
- If issues persist, check your Python SSL certificates

## Cost Information

- **Free Tier**: 
  - 1 database
  - 50,000 nodes
  - 175,000 relationships
  - Perfect for development/testing
  
- **Paid Tiers**: Start at ~$65/month
  - More nodes/relationships
  - Better performance
  - Support included

## Next Steps

After Aura is set up:
1. ✅ Update `.env` with Aura credentials
2. ✅ Run `python init_db.py` to initialize schema
3. ✅ Start your API: `python api.py`
4. ✅ Test with `python example_usage.py`

---

**You're all set with Neo4j Aura!** 🎉

