<template>
  <div>
    <vl-map
      ref="map"
      data-projection="EPSG:4326"
      @mounted="onMapMounted"
      style="height: 400px; width: 100%;"
    >
      <vl-view :zoom.sync="zoom" :center.sync="center"></vl-view>
      <vl-layer-tile
        v-for="baseLayer in baseLayers"
        :key="baseLayer.name"
        :id="baseLayer.id"
        :visible="baseLayer.visible"
      >
        <vl-source-xyz
          v-bind="baseLayer"
          :url="baseLayer.url"
          :attributions="baseLayer.attributions"
        />
      </vl-layer-tile>
      <vl-layer-image
        v-for="raster in rasterLayers"
        :key="raster.name"
        :id="raster.id"
        :visible="raster.visible"
      >
        <vl-source-image-wms
          v-bind="raster"
          :layers="raster.layer"
          :url="raster.url"
          :image-load-function="imageLoader"
        >
        </vl-source-image-wms>
      </vl-layer-image>
      <v-menu offset-y :z-index="1005" :close-on-content-click="false">
        <template v-slot:activator="{ on, attrs }">
          <v-btn class="mapLayerBtn" color="primary" v-bind="attrs" v-on="on">
            レイヤー情報
            <v-icon>mdi-layers</v-icon>
          </v-btn>
        </template>
        <div class="panel-area">
          <v-switch
            v-for="layer of vLayers"
            :key="layer.getProperties().id"
            inset
            v-model="layer.getProperties().visible"
            @change="showMapPanelLayer(layer)"
            :label="returnLayerLabel(layer.getProperties().id)"
          >
          </v-switch>
          <v-radio-group mandatory>
            <v-radio
              v-for="layer of rLayers"
              :key="layer.name"
              :label="returnLayerLabel(layer.getProperties().id)"
              :value="layer.name"
              @change="showBaseLayer(layer.getProperties().id)"
            >
            </v-radio>
          </v-radio-group>
        </div>
      </v-menu>
      <div v-if="big">
        <vl-layer-image id="wmsLayer" :z-index="1000" :visible="true">
          <vl-source-image-wms
            url="http://localhost:8000/geoserver/crm/wms"
            :image-load-function="imageLoader"
            layers="crm:Forests"
            projection="EPSG:4326"
          >
          </vl-source-image-wms>
        </vl-layer-image>
        <vl-layer-vector id="tableLayer" :z-index="1001" :visible="true">
          <vl-source-vector :features.sync="features"> </vl-source-vector>
          <vl-style-box>
            <vl-style-stroke color="#FFF" :width="1"></vl-style-stroke>
            <vl-style-fill color="red"></vl-style-fill>
          </vl-style-box>
        </vl-layer-vector>
      </div>
      <vl-layer-image v-else id="wmsLayer" :z-index="1000" :visible="false">
        <vl-source-image-wms
          url="http://localhost:8000/geoserver/crm/wms"
          :image-load-function="imageLoader"
          layers="crm:Forests"
          projection="EPSG:4326"
        >
        </vl-source-image-wms>
      </vl-layer-image>
      <vl-layer-vector
        id="tableLayer"
        render-mode="vector"
        :z-index="10001"
        :visible="true"
      >
        <vl-source-vector>
          <vl-feature
            v-for="feature in features"
            :key="feature.id"
            :id="feature.id"
            v-bind="feature"
          >
            <component
              :is="`vl-geom-multi-polygon`"
              v-bind="feature.geometry"
            />
            <vl-style-box>
              <vl-style-stroke color="#FFF" :width="1"></vl-style-stroke>
              <vl-style-fill color="red"></vl-style-fill>
              <vl-style-text :text="feature.properties.nametag"></vl-style-text>
            </vl-style-box>
          </vl-feature>
        </vl-source-vector>
      </vl-layer-vector>
    </vl-map>
  </div>
</template>

<script>
import Vue from "vue";
import VueLayers from "vuelayers";
import VectorSource from "vuelayers";
import WmsSource from "vuelayers";
import "vuelayers/lib/style.css";
import { ScaleLine } from "ol/control";

Vue.use(WmsSource);
Vue.use(VueLayers);
Vue.use(VectorSource);

export default {
  name: "map-container",

  props: {
    forests: {
      type: Array,
      required: true,
    },
    big: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    const zoom = 11;
    const center = [134.33234254149718, 35.2107812998969];
    const features = [];
    const loading = false;
    const mapLayers = [];
    const panelOpen = false;
    const mapVisible = true;

    const baseLayers = [
      {
        name: "標準地図",
        id: "std",
        visible: true,
        url: "https://maps.gsi.go.jp/xyz/std/{z}/{x}/{y}.png?_=20201001a",
        attributions:
          '© <a href="https://maps.gsi.go.jp/development/ichiran.html"> 国土地理院 </a>',
      },
    ];

    const rasterLayers = [
      {
        name: "赤色立体図",
        id: "red",
        visible: false,
        url: "http://localhost:8000/geoserver/raster/wms",
        layer: "raster:赤色立体図データ",
        projection: "EPSG:4326",
      },
      {
        name: "DEM",
        id: "dem",
        visible: false,
        url: "http://localhost:8000/geoserver/raster/wms",
        layer: "raster:DEMデータ",
        projection: "EPSG:4326",
      },
      {
        name: "航空写真",
        id: "rgb",
        visible: false,
        url: "http://localhost:8000/geoserver/raster/wms",
        layer: "raster:航空写真データ",
        projection: "EPSG:4326",
      },
    ];

    return {
      zoom,
      center,
      features,
      loading,
      mapLayers,
      panelOpen,
      mapVisible,
      baseLayers,
      rasterLayers,
    };
  },

  mounted() {
    this.loading = true;
    this.loadMapFeatures().then(f => {
      this.features = f;
      this.loading = false;
    });
  },

  computed: {
    calculatedBoundingBox() {
      const coordinates = this.forests
        .map(f => f.geodata.coordinates)
        .flat(Infinity);

      const latitudes = coordinates.filter((a, i) => i % 2);
      const longitudes = coordinates.filter((a, i) => !(i % 2));

      const xmin = Math.min(...longitudes);
      const xmax = Math.max(...longitudes);
      const ymin = Math.min(...latitudes);
      const ymax = Math.max(...latitudes);

      const c_lon = xmin + (xmax - xmin) / 2;
      const c_lat = ymin + (ymax - ymin) / 2;
      const z_lon = Math.log(180 / Math.abs(c_lon - xmin)) / Math.log(2);
      const z_lat = Math.log(90 / Math.abs(c_lat - ymin)) / Math.log(2);
      const z_center = Math.floor((z_lon + z_lat) / 2);
      return [[xmin, ymin, xmax, ymax], z_center];
    },
    vLayers() {
      const allLayers = this.mapLayers;
      return allLayers.filter(function(el) {
        return ["wmsLayer", "tableLayer"].includes(el.getProperties().id);
      });
    },
    rLayers() {
      const allLayers = this.mapLayers;
      return allLayers.filter(function(el) {
        return ["std", "red", "dem", "rgb"].includes(el.getProperties().id);
      });
    },
  },

  watch: {
    features: _.debounce(function() {
      this.zoom =
        this.calculatedBoundingBox[1] > 18 ? 18 : this.calculatedBoundingBox[1];
      this.center = this.calculatedBoundingBox[0];
    }, 10),

    forests: {
      handler() {
        this.loadMapFeatures().then(f => {
          this.features = f;
        });
      },
    },
  },

  methods: {
    onMapMounted() {
      this.$refs.map.$map.getControls().extend([new ScaleLine()]);
      this.returnMapLayers().then(l => {
        this.mapLayers = l;
      });
    },

    returnLayerLabel(layerId) {
      const names = {
        wmsLayer: "全ての地番",
        tableLayer: "表内の情報",
        dem: "DEM",
        red: "赤色立体図",
        std: "標準地図",
        rgb: "航空写真",
      };
      return names[layerId];
    },

    returnMapLayers() {
      const layers = this.$refs.map.getLayers();
      return new Promise(resolve => {
        resolve(layers);
      });
    },

    loadMapFeatures() {
      const mapItems = this.forests.map(f => {
        return {
          type: "Feature",
          id: f.id,
          geometry: f.geodata,
          properties: {
            customer: f.attributes.customer_cache,
            internal_id: f.internal_id,
            nametag: f.tags["団地"] + " " + f.internal_id,
          },
        };
      });

      return new Promise(resolve => {
        resolve(mapItems);
      });
    },

    imageLoader(im, src) {
      const xhr = new XMLHttpRequest();
      xhr.open("GET", src);
      xhr.setRequestHeader(
        "Authorization",
        "Bearer " + localStorage.getItem("accessToken"),
      );
      xhr.responseType = "arraybuffer";
      xhr.onload = function() {
        const arrayBufferView = new Uint8Array(this.response);
        const blob = new Blob([arrayBufferView], { type: "image/png" });
        const urlCreator = window.URL || window.webkitURL;
        im.getImage().src = urlCreator.createObjectURL(blob);
      };
      xhr.send();
    },

    showMapPanelLayer(layer) {
      layer.getProperties().visible
        ? layer.setVisible(false)
        : layer.setVisible(true);
    },

    showBaseLayer(id) {
      let currentLayer =
        this.baseLayers.find(layer => layer.visible) ||
        this.rasterLayers.find(layer => layer.visible);
      currentLayer.visible = false;
      let newLayer =
        this.baseLayers.find(layer => layer.id === id) ||
        this.rasterLayers.find(layer => layer.id === id);
      newLayer.visible = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.panel-area {
  padding: 5px;
  background-color: rgb(238, 232, 232);
  color: black;
  font-size: 1.2em;
  box-shadow: 0 0.25em 0.5em transparentize(#343a3a, 0.8);
}

.mapLayerBtn {
  position: relative;
  float: right;
  right: 10px;
  top: 50px;
  z-index: 1010;
}

.base-layers-panel {
  position: relative;
  float: right;
  top: 90%;
  z-index: 1010;
}
</style>
