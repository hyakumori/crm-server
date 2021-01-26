<template>
  <div>
    <content-header :content="headerContent" />
    <div>
      <vl-map
        :load-tiles-while-animating="true"
        :load-tiles-while-interacting="true"
        ref="map"
        data-projection="EPSG:4326"
        @mounted="onMapMounted"
        style="height: 600px; width: 100%;"
      >
        <vl-view
          :zoom.sync="zoom"
          :center.sync="center"
          :rotation.sync="rotation"
          :extent="calculatedBoundingBox"
          ref="mapView"
        ></vl-view>
        <vl-layer-tile id="osm" :key="viewKey">
          <vl-source-osm></vl-source-osm>
        </vl-layer-tile>

        <div v-if="big">
          <vl-layer-image :visible="true" :z-index="10000">
            <vl-source-image-wms
              url="http://localhost:8000/geoserver/crm/wms"
              :image-load-function="imageLoader"
              layers="crm:Forests"
              projection="EPSG:4326"
            >
            </vl-source-image-wms>
          </vl-layer-image>
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
                <!-- <vl-style-fill color="rgba(21,198,166, 0.2)"></vl-style-fill> -->
                <vl-style-text
                  :text="feature.properties.nametag"
                ></vl-style-text>
              </vl-style-box>
            </vl-feature>
          </vl-source-vector>
        </vl-layer-vector>
      </vl-map>
    </div>
    <div>{{ calculatedBoundingBox }}</div>
  </div>
</template>
<script>
import ContainerMixin from "./detail/ContainerMixin.js";
import ContentHeader from "./detail/ContentHeader";
import Vue from "vue";
import VueLayers from "vuelayers";
import VectorSource from "vuelayers";
import WmsSource, { ImageWmsSource, XyzSource } from "vuelayers";
import "vuelayers/lib/style.css"; // needs css-loader
import { ScaleLine, ZoomSlider } from "ol/control";
import { kebabCase } from "lodash";

Vue.use(XyzSource);
Vue.use(WmsSource);
Vue.use(VueLayers);
Vue.use(VectorSource);
Vue.use(ImageWmsSource);

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
    const zoom = 5;
    // const center = [134.33234254149718, 35.2107812998969];
    const center = [0, 0]
    const rotation = 0;
    const features = [];
    const loading = false;
    const layers = [];
    const viewKey = 1;

    return {
      zoom,
      center,
      rotation,
      features,
      loading,
      layers,
      viewKey,
    };
  },

  mounted() {
    this.loading = true;
    if (!this.big) {
      this.loadMapFeatures().then(f => {
        this.features = f;
        this.loading = false;
      });
    }
  },

  watch: {
  	features: _.debounce(function() {
    	this.$refs.mapView.$view.fit(
      	[134.36018137680563, 35.200038484322256, 134.36136854728989, 35.1990141616881],
      )
    }, 10),
  },

  computed: {
    calculatedBoundingBox() {
      var bounds = {},
        point,
        latitude,
        longitude;
      console.log(this.forests);
      let geodataType = this.forests[0].geodata.type;
      let coordinates = this.forests.map(f => f.geodata.coordinates);

      // Loop through each "feature"
      if (geodataType === "Polygon") {
        // It's only a single Polygon
        // For each individual coordinate in this feature's coordinates...
        for (var j = 0; j < coordinates[0].length; j++) {
          console.log(coordinates[0], "[0]");
          console.log(coordinates[0][j], "[0]J");
          longitude = coordinates[0][j][0];
          latitude = coordinates[0][j][1];

          // Update the bounds recursively by comparing the current xMin/xMax and yMin/yMax with the current coordinate
          bounds.xMin = bounds.xMin < longitude ? bounds.xMin : longitude;
          bounds.xMax = bounds.xMax > longitude ? bounds.xMax : longitude;
          bounds.yMin = bounds.yMin < latitude ? bounds.yMin : latitude;
          bounds.yMax = bounds.yMax > latitude ? bounds.yMax : latitude;
        }
      } else {
        // It's a MultiPolygon
        // Loop through each coordinate set
        for (var j = 0; j < coordinates.length; j++) {
          // For each individual coordinate in this coordinate set...
          for (var k = 0; k < coordinates[j][0].length; k++) {
            longitude = coordinates[j][0][k][0];
            latitude = coordinates[j][0][k][1];

            // Update the bounds recursively by comparing the current xMin/xMax and yMin/yMax with the current coordinate
            bounds.xMin = bounds.xMin < longitude ? bounds.xMin : longitude;
            bounds.xMax = bounds.xMax > longitude ? bounds.xMax : longitude;
            bounds.yMin = bounds.yMin < latitude ? bounds.yMin : latitude;
            bounds.yMax = bounds.yMax > latitude ? bounds.yMax : latitude;
          }
        }
      }
      const boundingBox = [
        bounds.xMin[0],
        bounds.yMin[1],
        bounds.xMax[0],
        bounds.yMax[1],
      ];
      // Returns an object that contains the bounds of this GeoJSON data.
      // The keys describe a box formed by the northwest (xMin, yMin) and southeast (xMax, yMax) coordinates.
      return boundingBox;
    },
  },

  methods: {
    geometryTypeToCmpName(type) {
      return "vl-geom-" + kebabCase(type);
    },

    onMapMounted() {
      this.$refs.map.$map
        .getControls()
        .extend([new ScaleLine(), new ZoomSlider()]);
    },

    loadMapFeatures() {
      console.log(this.forests);

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
