drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  user text DEFAULT 'user',
  title text not null,
  'text' text not null
);
