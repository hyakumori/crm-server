<template>
  <div>
    <content-header :content="headerContent" />
    <div>
      <vl-map
        ref="map"
        data-projection="EPSG:4326"
        @mounted="onMapMounted"
        style="height: 600px; width: 100%;"
      >
        <vl-view
          :zoom.sync="zoom"
          :center.sync="center"
          ref="mapView"
        ></vl-view>
        <vl-layer-tile title="base" id="osm" :visible="true">
          <vl-source-osm layer-name="base"></vl-source-osm>
        </vl-layer-tile>
        <v-menu offset-y :z-index="1005" :close-on-content-click="false">
          <template v-slot:activator="{ on, attrs }">
            <v-btn class="mapLayerBtn" color="primary" v-bind="attrs" v-on="on">
              レヤー地図
              <v-icon>mdi-layers</v-icon>
            </v-btn>
          </template>
          <div class="panel-area">
            <v-switch
              v-for="layer in mapLayers"
              :key="layer.getProperties().id"
              v-model="layer.visible"
              @change="showMapPanelLayer(layer)"
              :label="layer.values_.name"
            >
            </v-switch>
          </div>
        </v-menu>
        <div v-if="big">
          <vl-layer-image
            layer-name="WMS image"
            :z-index="1000"
            :visible="true"
          >
            <vl-source-image-wms
              url="http://localhost:8000/geoserver/crm/wms"
              :image-load-function="imageLoader"
              layers="crm:Forests"
              projection="EPSG:4326"
            >
            </vl-source-image-wms>
          </vl-layer-image>
          <vl-layer-vector layer-name="Vectors" :z-index="1001" :visible="true">
            <vl-source-vector :features.sync="features"> </vl-source-vector>
            <vl-style-box>
              <vl-style-stroke color="#FFF" :width="1"></vl-style-stroke>
              <vl-style-fill color="red"></vl-style-fill>
            </vl-style-box>
          </vl-layer-vector>
        </div>
        <vl-layer-vector
          v-else
          layer-name="Vectors"
          render-mode="vector"
          :z-index="1000"
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
                :is="geometryTypeToCmpName(feature.geometry.type)"
                v-bind="feature.geometry"
              />
              <vl-style-box>
                <vl-style-stroke color="#FFF" :width="1"></vl-style-stroke>
                <vl-style-fill color="red"></vl-style-fill>
                <vl-style-text
                  :text="feature.properties.nametag"
                ></vl-style-text>
              </vl-style-box>
            </vl-feature>
          </vl-source-vector>
        </vl-layer-vector>
      </vl-map>
    </div>
  </div>
</template>
<script>
import ContainerMixin from "./detail/ContainerMixin.js";
import ContentHeader from "./detail/ContentHeader";
import Vue from "vue";
import VueLayers from "vuelayers";
import VectorSource from "vuelayers";
import WmsSource from "vuelayers";
import "vuelayers/lib/style.css";
import { ScaleLine } from "ol/control";
import { kebabCase } from "lodash";

Vue.use(WmsSource);
Vue.use(VueLayers);
Vue.use(VectorSource);

export default {
  name: "map-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
  },

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
    return {
      zoom,
      center,
      features,
      loading,
      mapLayers,
      panelOpen,
    };
  },

  mounted() {
    this.loading = true;
    this.loadMapFeatures().then(f => {
      this.features = f;
      this.loading = false;
    });
    this.loading = false;
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
  },

  watch: {
    features: _.debounce(function() {
      this.zoom = this.calculatedBoundingBox[1];
      this.center = this.calculatedBoundingBox[0];
    }, 1000),

    forests: {
      handler() {
        this.loadMapFeatures().then(f => {
          this.features = f;
        });
      },
    },
    mapLayers: {
      handler(val) {
        let i = 1
        for (const layer of val) {
          layer.set('name', `レヤー ${i}`)
          i += 1
        }
      },
    },
  },

  methods: {
    geometryTypeToCmpName(type) {
      return "vl-geom-" + kebabCase(type);
    },

    onMapMounted() {
      this.$refs.map.$map.getControls().extend([new ScaleLine()]);
      this.returnMapLayers().then(l => {
        this.mapLayers = l;
      })
    },

    returnMapLayers() {
      const layers = this.$refs.map.getLayers();
      return new Promise(resolve => {
        resolve(layers)
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
      layer.visible === true ? layer.setVisible(false) : layer.setVisible(true);
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
  left: 85%;
  top: 10%;
  z-index: 1010;
}
</style>
