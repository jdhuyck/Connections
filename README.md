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
```mermaid
-- Public puzzles table
create table public.puzzles (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  creator_id uuid references auth.users,
  categories jsonb not null,
  created_at timestamp default now(),
  is_public boolean default false
);

-- Enable Row Level Security
alter table public.puzzles enable row level security;

-- Create policies
create policy "Public puzzles are visible"
  on public.puzzles for select
  using (is_public = true);
```