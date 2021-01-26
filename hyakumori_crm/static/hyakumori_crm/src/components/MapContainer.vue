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
        ></vl-view>
        <vl-layer-tile id="osm">
          <vl-source-osm></vl-source-osm>
        </vl-layer-tile>

        <div v-if="big">
          <!-- <vl-layer-tile>
            <vl-source-wms url="http://localhost:8000/geoserver/crm/wms?service=WMS&version=1.1.0&request=GetMap&layers=crm%3AForests&bbox=134.2798973887064%2C35.14479191322252%2C134.40287614163228%2C35.252641012694866&width=768&height=673&srs=EPSG%3A4326&styles=&format=geojson" layers="crm:Forests"></vl-source-wms>
          </vl-layer-tile> -->
          <!-- <vl-layer-tile :z-index='10000' render-mode="image"> -->
          <vl-layer-image :visible="true" :z-index="10000">
            <vl-source-image-wms
              url="http://localhost:8000/geoserver/crm/wms"
              :image-load-function="imageLoader"
              layers="crm:Forests"
              projection="EPSG:4326"
            >
              <!-- :features.sync="features"> -->
            </vl-source-image-wms>
          </vl-layer-image>
          <!-- <vl-source-vector url="http://localhost:8000/geoserver/crm/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=crm:Forests&maxFeatures=10000&outputFormat=application/json"></vl-source-vector> -->
          <!-- </vl-layer-tile> -->
          <!-- <component
            v-for="layer in layers"
            :is="layer.cmp"
            :key="layer.id"
            v-bind="layer"
          >
            <component :is="layer.source.cmp" v-bind="layer.source">
              <template
                v-if="
                  layer.source.staticFeatures &&
                    layer.source.staticFeatures.length
                "
              >
                <vl-feature
                  v-for="feature in layer.source.staticFeatures"
                  :key="feature.id"
                  :id="feature.id"
                  :properties="feature.properties"
                >
                  <component
                    :is="geometryTypeToCmpName(feature.geometry.type)"
                    :coordinates.sync="feature.geometry"
                    v-bind="feature.geometry"
                  />
                </vl-feature>              url="http://localhost:8000/geoserver/crm/wms?service=WMS&version=1.1.0&request=GetMap&layers=crm:Forests&bbox=134.2798973887064,35.14479191322252,134.40287614163228,35.252641012694866&width=768&height=673&srs=EPSG:4326&styles=&format=image/png"
              </template>
            </component>
          </component> -->
        </div>
        <vl-layer-vector v-else render-mode="vector" overlay="true">
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
  </div>
</template>
<script>
import ContainerMixin from "./detail/ContainerMixin.js";
import ContentHeader from "./detail/ContentHeader";
import Vue from "vue";
import VueLayers from "vuelayers";
import VectorSource from "vuelayers";
import WmsSource, {ImageWmsSource, XyzSource} from "vuelayers";
import "vuelayers/lib/style.css"; // needs css-loader
import {ScaleLine, ZoomSlider} from "ol/control";
import {kebabCase} from "lodash";

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
    const zoom = 13;
    const center = [134.33234254149718, 35.2107812998969];
    const rotation = 0;
    const features = [];
    const loading = false;
    const layers = [];

    return {
      zoom,
      center,
      rotation,
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
      console.log("blah");
      // this.loadBigMap().then(f => {
      //   this.features = f.features;
      //   this.loading = false;
      //   console.log(this.features)
      // })
    }
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
      console.log(mapItems);

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
    // getRequestUrl(extent, resolution, projection) {
    //   // const url = 'http://localhost:8000/geoserver/crm/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=crm%3AForests&maxFeatures=100&outputFormat=application%2Fjson';
    //   const url =
    //     "http://localhost:8000/geoserver/crm/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=crm:Forests&maxFeatures=100&outputFormat=application/json";
    //   var xhr = new XMLHttpRequest();
    //   xhr.open("GET", url);
    // xhr.setRequestHeader(
    //   "Authorization",
    //   "Bearer " + localStorage.getItem("accessToken"),
    // );

    //   /**
    //    * @param {Event} event Event.
    //    * @private
    //    */
    //   xhr.onload = function(event) {
    //     console.log(event);
    //     // status will be 0 for file:// urls
    //     if (!xhr.status || (xhr.status >= 200 && xhr.status < 300)) {
    //       var source = xhr.responseText;
    //       if (!source) {
    //         source = new DOMParser().parseFromString(
    //           xhr.responseText,
    //           "application/xml",
    //         );
    //       }
    //       // if (source) {
    //       //   success.call(this, format.readFeatures(source,
    //       //     {featureProjection: projection}),
    //       //   format.readProjection(source), format.getLastExtent());
    //       // } else {
    //       //   failure.call(this);
    //       // }
    //     } else {
    //       failure.call(this);
    //     }
    //   }.bind(this);
    //   /**
    //    * @private
    //    */
    //   xhr.onerror = function() {
    //     failure.call(this);
    //   }.bind(this);
    //   xhr.send();
    // },
  },
};
</script>
