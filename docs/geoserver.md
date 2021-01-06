# Setting up Geoserver

Geoserver is launched by `docker-compose`. Once up and running, you can 
 access it by going to http://localhost:8600/geoserver/

If setting up or using geoserver for the first time, please change at least the default users password.
 A complete guide to the security settings can be found [here](https://docs.geoserver.org/stable/en/user/security/webadmin/index.html).

Changing the default master password:

![master password change](img/pw-change-master.png)

and the default user password:

![admin password change](img/pw-change-user.png)

## Setting up Data

This section described how to get started with geoserver by adding data that will then be served over WMS and WFS.

### Workspaces

We will create two workspaces. One for the CRM, which contains the vector data
 that is used in QGIS, and another for the raster data that are used as base maps
 and are served from S3. See the [official documentation](https://docs.geoserver.org/stable/en/user/rest/workspaces.html)
 for more in-depth explanations.

1. Create CRM workspace:
    - Basic Info:
        - name: crm
        - uri: https://100morichan.net
        - Default Workspace: TRUE
    - Security:
        - default settings should be OK.
Once this has been created, click on it to edit it and select:
    - Settings:
        - Enabled: TRUE
    - Services:
        - WFS

2. Create the raster workspace:
    - Basic Info:
        - name: raster
        - uri: https://100morichan.net
        - Default Workspace: FALSE
    - Security:
        - default settings should be OK.
Once this has been created, click on it to edit it and select:
    - Settings:
        - Enabled: TRUE
    - Services:
        - WMS

### Stores

In this documentation, we will add two stores: one for the forest vector data that is
 stored in a postgres database (belonging to the crm workspace), 
 and the other for the raster data that is served over amazon s3 
 (belonging to the raster workspace). Please see the [official documentation](https://docs.geoserver.org/stable/en/user/data/webadmin/stores.html) 
 for more detailed explanations.

   * crm_forests:
        - select "PostGIS - PostGIS Database" from Vector Data Sources.
        - create the store with the following settings:
            - Workspace: crm
            - Data Source Name: crm_forests
            - Description: hyakumori crm vector data
            - Enabled: TRUE
            - host: postgres
            - port: 5432
            - database: hyakumori
            - schema: public
            - user: postgres
            - passwd: postgres

   * raster_rgb (s3):
        - select "S3GeoTiff - Tagged Image File Format with Geographic 
          information hosted on S3" from Raster Data Sources.
        - create the store with the following settings:
            - Workspace: hyakumori
            - Data Source Name: raster_rgb
            - Description: A description of the raster served over s3
            - Enabled: TRUE
            - URL: s3://hyakumori-geodata/test/若杉天然林オルソ.cog.tif?awsRegion=AP_NORTHEAST_1
    
_note: the s3 raster is hosted in a private s3 bucket and so it requires an AWS access key. This 
is store on GitHub as a GitHub secret._
    
3. add layers. We will add two layers in this documentation: one for 
   forest vectors (crm_forests store), and the other for one of the raster base maps 
   (raster store).
   * crm_forests:
        - select "add a new layer" to create a new layer from the Layers menu item 
          (this is located in the Data menu heading on the menu bar that is on 
          the left-hand side of the screen).
        - select `crm:crm_forests` as source to add the layer from.
        - click `publish` for `crm_forest`.
        - publish the layer with the following settings:
            - Data:
                - Name: Forests
                - Title: Forests
                - Abstract: Hyakumori customer-owned forests.
                - Native SRS: EPSG:2447
                - Declared SRS: EPSG:2447
                - SRS Handling: Force declared
                - Bounding boxes:
                    - Native Bounding Box: compute from SRS bounds
                    - Lat/Lon Bounding Box: compute from native bounds
            - Security:
                - Grant read and write access to `ADMIN` and `GROUP_ADMIN` only.
    * raster_rgb:
        - select "add a new layer" to create a new layer from the Layers menu item 
      (this is located in the Data menu heading on the menu bar that is on 
      the left-hand side of the screen).
        - select `raster:raster_rgb` as source to add the layer from.
        - publish layer name `若杉天然林オルソ.cog` with the following settings:
            - Data:
                - fill in title, name, and abstract
                - make sure `Enabled` and `Advertised` are selected
                - make sure all SRS settings are correct (all should be EPSG:2447)
                - compute the bounding box size from the data
            - Security:
                - optionally restrict base maps to only admins.
    

## Connect to WFS layer from QGIS:
Use the following instructions to connect to the WFS layer to be able
 to read and write forest vectors to the database.

1. Click "Layer > Add Layer > Add WFS Layer ..."

![Add WFS Layer ...](img/add-layer.png)

2. Click `New Connection` and enter the following connection details:

![Connection Details](img/connection.png)

3. This requires creating an authentication configuration. Click the "Plus" icon to 
   add a new configuration (recommended) or create a new "Basic" authentication setting 
   by clicking on the `Basic` tab.
   
4. Enter the following authentication settings then save and click `OK` for the connection details:

![Authentication Configuration](img/connection.png)

You must use admin level credentials for geoserver.

5. Click `Connect` under "Server Connections".

6. Select the layer `crm_forest` and click `Add`.

![Add WFS Layer](img/add-wfs.png)

![View WFS Layer](img/crm_forests.png)
