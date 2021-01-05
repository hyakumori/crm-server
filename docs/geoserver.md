# Setting up Geoserver

Geoserver is launched by `docker-compose`. Once 


1. create workspace with the following settings:
   
        name: hyakumori
        uri: hyakumori

2. add stores. We will need two stores, one for the vector
   data stored in a postgres database and the other for the raster data 
   that is served over amazon s3.
   * vector (postgres):
        - select "PostGIS - PostGIS Database" from vector data sources
        - create store with the following settings:
            - Workspace: hyakumori
            - Data Source Name: vector
            - Description: hyakumori vector data
            - Enabled: TRUE
            - host: postgres
            - port: 5432
            - database: hyakumori
            - schema: public
            - user: postgres
            - passwd: postgres
    
3. add layers. We will add two layers in this documentation: one for 
   forest vectors (vector store) and the other for raster basemaps 
   (raster store).
   * postgres:
    - select "add a new layer" to create a new layer from the Layers menu item 
      (this is located in the Data menu heading on the menu bar that is on 
      the left hand side of the screen).
    - select `hyakumori:vector` to add the layer from.
    - click `publish` for `crm_forest`.
    - publish the layer with the following settings:
        - Name: forests
        - Title: forests
        - Abstract: Hyakumori customer-owned forests.
        - Bounding box:
            - min x: 134.17082866958322
            - min y: 34.98567598217855
            - max x: 134.59760837529205
            - max y: 35.231938332498515


## Connect to WFS layer from QGIS:
Use the following instructions to connect to the WFS layer to be able
 to read and write vectors to the database.

