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
        <vl-layer-tile id="osm">
          <vl-source-osm></vl-source-osm>
        </vl-layer-tile>

        <div v-if="big">
          <vl-layer-image>
            <vl-source-image-wms
              url="http://localhost:8000/geoserver/crm/wms"
              :image-load-function="imageLoader"
              layers="crm:Forests"
              projection="EPSG:4326"
            >
            </vl-source-image-wms>
          </vl-layer-image>
          <vl-layer-vector :overlay="true">
            <vl-source-vector :features.sync="features">
            </vl-source-vector>
            <vl-style-box>
              <vl-style-stroke color="#FFF" :width="1"></vl-style-stroke>
              <vl-style-fill color="red"></vl-style-fill>
            </vl-style-box>
          </vl-layer-vector>
        </div>
        <vl-layer-vector v-else render-mode="vector" :overlay="true">
          <vl-source-vector ref="geojsonSource">
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
    const layers = [];

    return {
      zoom,
      center,
      features,
      loading,
      layers,
    };
  },

  mounted() {
    this.loading = true;
    if (!this.big) {
      this.loadMapFeatures().then(f => {
        this.features = f;
        this.loading = false;
      });
    } else {
      this.loadMapFeatures().then(f => {
        this.features = f;
        this.loading = false;
      });
    }
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
        })
      },
    },
  },

  methods: {
    geometryTypeToCmpName(type) {
      return "vl-geom-" + kebabCase(type);
    },

    onMapMounted() {
      this.$refs.map.$map.getControls().extend([new ScaleLine()]);
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
  },
};
</script>
