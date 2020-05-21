<template>
  <v-row no-gutters class="pt-1">
    <v-col cols="7">
      <v-text-field
        outlined
        dense
        v-model="item.value"
        label="バリュー"
        hide-details
      ></v-text-field>
    </v-col>
    <v-col cols="4" class="pl-2">
      <v-text-field
        v-model="item.color"
        hide-details
        outlined
        readonly
        label="色彩"
        dense
      >
        <template v-slot:append>
          <v-menu
            v-model="item.menu"
            top
            nudge-bottom="90"
            nudge-left="0"
            :close-on-content-click="false"
          >
            <template v-slot:activator="{ on }">
              <div :style="_getItemStyle(item)" v-on="on" />
            </template>
            <v-card>
              <v-card-text class="pa-0">
                <v-color-picker
                  v-mask="'######'"
                  v-model="item.color"
                  @update:color="$event => _updateTagItemColor($event, item)"
                  hide-mode-switch
                  show-swatches
                  flat
                  label="色彩"
                  mode="hexa"
                />
              </v-card-text>
            </v-card>
          </v-menu>
        </template>
      </v-text-field>
    </v-col>
    <v-col cols="1" class="pl-2 pt-2" v-if="showDelete">
      <v-btn
        color="grey lighten-1"
        depressed
        small
        @click.stop="() => _onDeleteColorSetting(item)"
        icon
      >
        <v-icon>mdi-delete</v-icon>
      </v-btn>
    </v-col>
  </v-row>
</template>

<script>
export default {
  props: {
    getItemStyle: { type: Function, required: true },
    updateTagItemColor: { type: Function, required: true },
    item: { type: Object, required: true },
    id: { type: [String, Number] },
    showDelete: { type: Boolean, default: false },
  },
  methods: {
    _getItemStyle(item) {
      return this.getItemStyle(item);
    },
    _updateTagItemColor(val, item) {
      return this.updateTagItemColor(val, item);
    },
    _onDeleteColorSetting(item) {
      return this.$emit("setting-deleted", { item, id: this.id });
    },
  },
};
</script>
