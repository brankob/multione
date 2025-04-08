
-- SQL Script for importing points_ppi.csv data into PostgreSql AND
-- converting data to geometry data into CRS = 3765
-- Also creating N-Grid from coordinates provided in csv file (lon,lat)
-- Data can be seen through QGIS connection with PostgreSql

DROP TABLE IF EXISTS public.points_ppi;

-- Create table
CREATE TABLE IF NOT EXISTS public.points_ppi(
	lat double precision,
 	lon double precision,
	ppi float,
	the_geom geometry(Point, 3765)
);

-- Import file - Read points_ppi.csv data 
COPY  public.points_ppi(lon, lat, ppi )
FROM '/tmp/points_ppi.csv'
WITH (FORMAT CSV, HEADER, DELIMITER ',');

-- Create index on lon & lat
-- CREATE INDEX idx_lon_ais ON public.points_ppi USING gist(lon);
-- CREATE INDEX idx_lat_ais ON public.points_ppi USING gist(lat);

-- CALCULATE POINT from lon&lat to geometry 3765 Croatian coordinate system
UPDATE  public.points_ppi
    SET the_geom = ST_Transform(ST_GeomFromText('POINT(' || lon  || ' ' || lat || ')', 4326),3765);

-- Remove NULL(Missing values) values from table
DELETE FROM public.points_ppi
WHERE lon IS NULL OR lat IS NULL OR ppi IS NULL;


----------------------------  DEFINE -> Find min easting&northing (lat&lon) (bottom left corner)  ---------------------
--------------------------               - for creating grid       --------------------------
SELECT min(ST_X(ST_Centroid(the_geom))) AS min_x,
       min(ST_Y(ST_Centroid(the_geom))) AS min_y
	  -- min(ST_X(ST_Centroid(ST_Transform(the_point, 3765)))) AS long,
	  -- min(ST_Y(ST_Centroid(ST_Transform(the_point, 3765)))) AS lat
FROM public.points_ppi;


--------------------------- Create grid     ---------------------------
-- Drop table if exists
DROP TABLE IF EXISTS public.ppi_grid;

-- Create GRID -> test radar table 
CREATE TABLE  public.ppi_grid(
         the_geom geometry(multipolygon,3765)
);

-- Create index
CREATE INDEX idx_ppi_grid ON public.ppi_grid USING gist(the_geom); 


-- Run for creating grid - multipolygon
-- Size X => 657*30m=19,710m
-- Size Y => 1106*30m=33,180m 
-- Number of cells 657*1106=726,642

INSERT INTO public.ppi_grid
SELECT ST_SetSRID(ST_Collect(cells.geom), 3765)
FROM ST_CreateFishnet(657, 1106, 30, 30, 576633, 5032476) AS cells;



-------------------------------------  Convert Grid multipolygon into  -------------------------- 
-------------------------------------  -> N polygons  --------------------------
-- Drop table if exists
DROP TABLE IF EXISTS tbl_ppi_grid_n;

-- Create GRID -> test radar table 
CREATE TABLE tbl_ppi_grid_n(
	     id serial,
         the_geom geometry(polygon,3765)
);

-- Add index
CREATE INDEX idx_ppi_grid_n ON tbl_ppi_grid_n USING gist(the_geom); 

-- Convert multipolygon to N polygons 
INSERT INTO tbl_ppi_grid_n (the_geom)
SELECT ((ST_Dump(the_geom)).geom) AS geom   
FROM ppi_grid;

	
