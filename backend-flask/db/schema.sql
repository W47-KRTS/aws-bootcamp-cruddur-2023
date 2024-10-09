CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- schema is like the excel file, tables/views are like the sheets in it
-- public.users explication
-- when you are building out microservices aplicattions you want to have diffrent domains
-- for the app. What works really well, when starting, you can be a monolith,
-- and then transition to having different databases per domain.
-- this works well with the schema name spaces in postgres

CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY, -- specify the type as being an uuid
  display_name text,
  handle text
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);

CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);