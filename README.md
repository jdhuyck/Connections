# Connections overview

## Architecture

```mermaid
graph TD
    A[React Frontend] -->|GitHub Pages<br/>jdhuyck.github.io/Connections| B[Supabase]
    B -->|PostgreSQL| C[(Supabase DB)]
    B -->|Auth| D[Supabase Auth]
    E[User Devices] -->|HTTPS| A
    A -->|API Calls| B
    F[GitHub Actions] -->|Auto-deploy| A
```

## Front End - Github Pages /Connections subdirectory
React/ts static site
Communicates with backend via HTTPS
Stores guest session in local storage

/src
	/components
		PuzzleBoard.tsx
		CategorySelctor.tsx
	/pages
		PlayPage.tsx
		CreatePage.tsx
	/services
		api.ts

## Backend - Supabase
```mermaid
sequenceDiagram
    User->>Frontend: Plays as guest
    Frontend->>Supabase: Anonymous session
    User->>Frontend: Clicks "Save Progress"
    Frontend->>Supabase Auth: Signup (Email/OAuth)
    Supabase Auth->>Frontend: JWT
    Frontend->>Supabase DB: Store user data
```
## Database structure
```bash
create extension if not exists pgcrypto;

create table puzzles (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  categories jsonb not null,
  creator_id uuid references auth.users on delete set null,
  created_at timestamp with time zone default timezone("utc"::text, now()),
  is_public boolean default false,
  difficulty smallint
);

alter table puzzles enable row level security;

create policy "Public puzzles are visible to all"
  on puzzles for select
  using (is_public = true);

create policy "Users can manage their own puzzles"
  on puzzles for all
  using (auth.uid() = creator_id);
```