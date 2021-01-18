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
          <component
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
                </vl-feature>
              </template>
            </component>
          </component>
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
      <div> {{forests}} </div>
      <div> STuff </div>
    </div>
  </div>
</template>
<script>
import ContainerMixin from "./detail/ContainerMixin.js";
import ContentHeader from "./detail/ContentHeader";
import Vue from "vue";
import VueLayers from "vuelayers";
import VectorSource from "vuelayers";
import "vuelayers/lib/style.css"; // needs css-loader
import { ScaleLine, ZoomSlider } from "ol/control";
import { kebabCase } from "lodash";

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
      this.layers.push({
        id: "wfs",
        title: "WFS",
        cmp: "vl-layer-vector",
        visible: true,
        renderMode: "image",
        features: [],
        source: {
          cmp: "vl-source-vector",
          url: "http://localhost:8600/geoserver/crm/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=crm%3AForests&outputFormat=application%2Fjson",
            // "http://localhost:8600/geoserver/crm/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=crm%3AForests&outputFormat=application%2Fjson",
          layers: "crm:forests",
          extParams: { TILED: true },
          serverType: "geoserver",
        },
      });
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
      console.log(mapItems)

      return new Promise(resolve => {
        resolve(mapItems);
      });
    },
  },
};
</script>
