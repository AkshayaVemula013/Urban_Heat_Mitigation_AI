// 1. Tell the computer to look at Chennai
var chennai_point = ee.Geometry.Point([80.2707, 13.0827]);
Map.centerObject(chennai_point, 11);

// 2. Look at Landsat 8 satellite pictures from peak summer 2024
var images = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterBounds(chennai_point)
  .filterDate('2024-03-01', '2024-06-30') // Core high-heat summer 2024
  .filter(ee.Filter.lt('CLOUD_COVER', 40)); // Relaxed filter to ensure image capture

// 3. Take the average of those pictures to get rid of random clouds
var clean_picture = images.median();

// 4. Show the real satellite picture on the map below
Map.addLayer(clean_picture, {bands: ['SR_B4', 'SR_B3', 'SR_B2'], min: 0, max: 20000}, 'Chennai From Space');

// 5. Calculate Land Surface Temperature (LST) in Celsius
var thermalBand = clean_picture.select('ST_B10');
var lstKelvin = thermalBand.multiply(0.00341802).add(149.0);
var lstCelsius = lstKelvin.subtract(273.15);

// 6. Color code the temperature (Blue = Cool, Red = Hot)
var heatPalette = ['blue', 'limegreen', 'yellow', 'orange', 'red'];
Map.addLayer(lstCelsius, {min: 28, max: 48, palette: heatPalette}, 'Heat Map (Celsius)');

// 7. Calculate Vegetation Cover (NDVI)
var ndvi = clean_picture.normalizedDifference(['SR_B5', 'SR_B4']);
Map.addLayer(ndvi, {min: 0.0, max: 0.5, palette: ['brown', 'yellow', 'green']}, 'Green Map (Trees)');

// 8. Calculate Built-up Density (NDBI)
var ndbi = clean_picture.normalizedDifference(['SR_B6', 'SR_B5']);
Map.addLayer(ndbi, {min: -0.1, max: 0.4, palette: ['white', 'grey', 'purple']}, 'Concrete Map (Buildings)');

// =========================================================================
// STEP 1.2: ADD WEATHER DATA (AIR TEMPERATURE)
// =========================================================================

// 9. Fetch weather data matching our 2024 summer window
var weatherData = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
  .filterBounds(chennai_point)
  .filterDate('2024-03-01', '2024-06-30')
  .select('temperature_2m') 
  .median(); 

// 10. Convert the weather temperature from Kelvin to Celsius
var airTempCelsius = weatherData.subtract(273.15);

// 11. Show the Air Temperature on our map
Map.addLayer(airTempCelsius, {min: 28, max: 40, palette: ['yellow', 'orange', 'darkred']}, 'Air Weather Map', false);

// =========================================================================
// STEP 1.3: DATA ALIGNMENT (STACKING THE DATA PIECES TOGETHER)
// =========================================================================

// 12. Force the blurry Air Temperature map to match the sharp Heat Map grid
var alignedAirTemp = airTempCelsius.reproject({
  crs: lstCelsius.projection(),
  scale: 30 
});

// 13. Stack all 4 ingredients into one final AI Master Dataset
var aiMasterDataset = lstCelsius.rename('LST')
  .addBands(ndvi.rename('NDVI'))
  .addBands(ndbi.rename('NDBI'))
  .addBands(alignedAirTemp.rename('Air_Temp'));

print('--- PHASE 1 COMPLETE ---');

// =========================================================================
// PHASE 2: FIXED HOTSPOT IDENTIFICATION
// =========================================================================

// 15. Find areas where the Ground Temperature (LST) is higher than 40°C
var hotZones = lstCelsius.gt(40);

// 16. Mask it so we hide the cooler areas (0) and only keep the hot pixels (1)
var cleanHotspots = hotZones.updateMask(hotZones.eq(1));

// 17. Display the final hotspots as a bright RED overlay on top of the city
Map.addLayer(cleanHotspots, {palette: ['red']}, 'AI Identified Hotspots');

print('--- PHASE 2 COMPLETE ---');

// =========================================================================
// PHASE 3: FIXED DATA SAMPLING (LIGHTWEIGHT)
// =========================================================================

var chennai_box = ee.Geometry.BBox(80.15, 13.00, 80.32, 13.15);

var trainingPoints = aiMasterDataset.sample({
  region: chennai_box, 
  scale: 30,           
  numPixels: 500, 
  geometries: true     
});

Map.addLayer(trainingPoints, {color: 'yellow'}, 'AI Training Points (Fixed)');

print('--- FIXED PHASE 3 COMPLETE ---');

// =========================================================================
// STEP 3.2: EXPORT TO GOOGLE DRIVE
// =========================================================================

Export.table.toDrive({
  collection: trainingPoints,
  description: 'Chennai_Urban_Heat_AI_Data_V4', // Fresh version name
  fileFormat: 'CSV',
  selectors: ['LST', 'NDVI', 'NDBI', 'Air_Temp'] 
});

print('--- SYSTEM: EXPORT TASK GENERATED ---');
