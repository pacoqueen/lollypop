SELECT * FROM albums WHERE id IN (
-- SQL de `database_albums.py::get_ids`. Línea 949
SELECT DISTINCT albums.rowid
  FROM albums, artists,
	   album_artists, album_genres AS AG
       , track_artists, tracks
 WHERE artists.rowid=album_artists.artist_id
       AND -9 NOT IN (SELECT album_genres.genre_id 	 	-- -9=?
                        FROM album_genres
                       WHERE AG.album_id=album_genres.album_id)
       AND AG.album_id=albums.rowid
       AND album_artists.album_id=albums.rowid
       AND (
      album_artists.artist_id=(SELECT id FROM artists WHERE name='MUTEMATH') OR -- SELECT...MUTEMATH=?
      -- album_artists.artist_id=? OR
      -- album_artists.artist_id=? OR
      1=0)
	  AND track_artists.track_id = tracks.id
	  AND (
	  track_artists.artist_id=(SELECT id FROM artists WHERE name='MUTEMATH') OR -- SELECT...MUTEMATH=?
	  -- track_artists.artist_id=? OR
	  -- track_artists.artist_id=? OR
	  1=0)
--
);


-- Todos los álbumes de un artista, sin tener en cuenta género
SELECT * FROM albums WHERE id IN (
--
SELECT DISTINCT albums.id
  FROM albums, tracks, track_artists
 WHERE tracks.album_id=albums.id
   AND track_artists.track_id = tracks.id
   AND (
	track_artists.artist_id = (SELECT id FROM artists WHERE name='MUTEMATH') OR
	-- track_artists.artist_id = ? OR
	-- track_artists.artist_id = ? OR
    1=0)
--
);


-- Todos los álbumes de un artista, teniendo en cuenta el género. Tarda 10 veces más que la original :(
SELECT * FROM albums WHERE id IN (
--
SELECT DISTINCT albums.id
  FROM albums, tracks, track_artists
       , album_genres AS AG
 WHERE tracks.album_id=albums.id
   AND track_artists.track_id = tracks.id
   AND -9 NOT IN (SELECT album_genres.genre_id 	 	-- -9=?
                    FROM album_genres
                   WHERE AG.album_id=album_genres.album_id)
   AND (
	track_artists.artist_id = (SELECT id FROM artists WHERE name='MUTEMATH') OR
	-- track_artists.artist_id = ? OR
	-- track_artists.artist_id = ? OR
    1=0)
--
);


-- No entiendo la subconsulta anidada tan solo para dejar fuera los discos de
-- género -9 (CHARTS, sea lo que sea). Esto es **mucho** más rápido y **creo**
-- que hace lo mismo. La tabla artists hay que incluirla porque después se
-- hace un ORDER BY con artists.sortname.
SELECT * FROM albums WHERE id IN (
--
SELECT DISTINCT albums.id
  FROM albums, tracks, track_artists, album_genres AS AG, artists
 WHERE tracks.album_id=albums.id
   AND track_artists.track_id = tracks.id
   AND AG.album_id = albums.id
   AND artists.id = track_artists.artist_id
   AND AG.genre_id != -9
   --AND -9 NOT IN (SELECT album_genres.genre_id 	 	-- -9=?
   --                 FROM album_genres
   --               WHERE AG.album_id=album_genres.album_id)
   AND (
	track_artists.artist_id = (SELECT id FROM artists WHERE name='MUTEMATH') OR
	-- track_artists.artist_id = ? OR
	-- track_artists.artist_id = ? OR
    1=0)
--
);
