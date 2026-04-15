# Catch — backend

Flask + Supabase backend for the Catch MVP.

---

## Setup

### 1. Clone and enter the folder
```bash
cd catch-backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up Supabase
1. Go to [supabase.com](https://supabase.com) and create a free project
2. Go to **SQL Editor** → paste the contents of `schema.sql` → click **Run**
3. Go to **Project Settings → API** and copy your URL and anon key

### 5. Configure environment variables
```bash
cp .env.example .env
# Open .env and fill in your SUPABASE_URL and SUPABASE_KEY
```

### 6. Run the server
```bash
python app.py
# Server starts at http://localhost:5000
```

---

## API endpoints

### Groups
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/groups/create` | Create a new group |
| POST | `/groups/join` | Join a group via invite code |
| GET | `/groups/<group_id>/members` | List all members |
| GET | `/groups/user/<user_id>` | Get all groups for a user |

### Goals
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/goals/set` | Set a goal and go active |
| POST | `/goals/<goal_id>/complete` | Mark a goal as done |
| GET | `/goals/group/<group_id>` | Get all goals in a group |

### Nudges
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/nudges/send` | Send a nudge with a funny photo |
| GET | `/nudges/inbox/<user_id>` | Get unread nudges |
| POST | `/nudges/<nudge_id>/seen` | Mark a nudge as seen |
| GET | `/nudges/group/<group_id>` | Get nudge history for a group |

---

## Adding Web Push notifications (next step)

Right now nudges are saved to the database and the frontend polls for them.
To make them interrupt someone mid-scroll, you'll need Web Push:

1. Generate VAPID keys: `pip install pywebpush` then run the key generator
2. Save the public/private keys to your `.env`
3. In `routes/nudges.py`, find the `# NOTE: Web Push` comment and add the push call there
4. On the frontend, register a service worker and subscribe the user

---

## Folder structure

```
catch-backend/
├── app.py              # Flask app, registers all routes
├── db.py               # Supabase client
├── schema.sql          # Database tables — paste into Supabase
├── requirements.txt    # pip packages
├── .env.example        # Template for your secrets
├── .gitignore
└── routes/
    ├── groups.py       # Create & join groups
    ├── goals.py        # Set & complete goals
    └── nudges.py       # Send & receive nudges
```
