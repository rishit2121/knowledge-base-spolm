# Finding Connection Details in Neo4j Aura

## Step-by-Step: Developer Hub Method

### 1. You're in the Right Place!
You're in the **Developer hub** - this is perfect!

### 2. Click "Python"
Since our knowledge base uses Python, click on **"Python"** in the list.

### 3. What You'll See
After clicking Python, you should see something like:

```
Connection URI: neo4j+s://xxxxx.databases.neo4j.io
Username: neo4j
Password: [hidden - click to reveal]
```

Or it might show code like:
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j+s://xxxxx.databases.neo4j.io",
    auth=("neo4j", "your-password-here")
)
```

### 4. Copy These Three Things:
1. **The URI** (starts with `neo4j+s://`)
2. **The username** (usually `neo4j`)
3. **The password** (click "Show" or "Reveal" if it's hidden)

### 5. Update Your .env File
Open your `.env` file and update it:

```env
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=the_password_you_copied
```

**Important**: 
- Copy the entire URI including `neo4j+s://`
- The password might be hidden - look for a "Show" or "Reveal" button
- Save the password somewhere safe - you may not be able to see it again!

### 6. Test It
After updating `.env`, test the connection:

```bash
python -c "from db.connection import get_neo4j_driver; driver = get_neo4j_driver(); print('✓ Connected!')"
```

---

**That's it!** Once you have those three pieces of information, you're ready to connect.

