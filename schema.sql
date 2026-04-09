-- ============================================================
-- Catch MVP — Supabase database schema
-- Paste this into Supabase > SQL Editor > New query > Run
-- ============================================================

-- Groups table
create table if not exists groups (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  created_by  text not null,           -- user_id of creator
  invite_code text unique not null,    -- 8-char code friends use to join
  created_at  timestamptz default now()
);

-- Group members (many users ↔ many groups)
create table if not exists group_members (
  id         uuid primary key default gen_random_uuid(),
  group_id   uuid references groups(id) on delete cascade,
  user_id    text not null,
  joined_at  timestamptz default now(),
  unique(group_id, user_id)            -- prevent duplicate membership
);

-- Goals (one per user per session)
create table if not exists goals (
  id           uuid primary key default gen_random_uuid(),
  user_id      text not null,
  group_id     uuid references groups(id) on delete cascade,
  description  text not null,
  status       text default 'active' check (status in ('active', 'done')),
  started_at   timestamptz default now(),
  completed_at timestamptz
);

-- Nudges (funny photo sent from one friend to another)
create table if not exists nudges (
  id           uuid primary key default gen_random_uuid(),
  from_user_id text not null,
  to_user_id   text not null,
  group_id     uuid references groups(id) on delete cascade,
  image_url    text not null,
  caption      text default '',
  seen         boolean default false,
  sent_at      timestamptz default now()
);

-- ── Indexes for common queries ──────────────────────────────────
create index if not exists idx_group_members_group on group_members(group_id);
create index if not exists idx_group_members_user  on group_members(user_id);
create index if not exists idx_goals_group         on goals(group_id);
create index if not exists idx_goals_user          on goals(user_id);
create index if not exists idx_nudges_to_user      on nudges(to_user_id);
create index if not exists idx_nudges_group        on nudges(group_id);
