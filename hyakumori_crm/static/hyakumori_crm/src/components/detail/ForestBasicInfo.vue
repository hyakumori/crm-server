<template>
  <v-row class="forest-basic-info">
    <v-col v-if="info" cols="6">
      <template>
        <template v-if="isUpdate">
          <text-info
            label="都道府県"
            :value="address.prefecture"
            :isUpdate="isUpdate"
            @input="val => (address.prefecture = val)"
          />
          <text-info
            label="市町村"
            :value="address.municipality"
            :isUpdate="isUpdate"
            @input="val => (address.municipality = val)"
          />
          <text-info
            label="大字"
            :value="address.sector"
            :isUpdate="isUpdate"
            @input="val => (address.sector = val)"
          />
        </template>
        <text-info v-else label="住所" :value="fullAddress" />
        <text-info v-if="!isUpdate" label="契約期間" :value="fullDate" />
      </template>
    </v-col>
    <v-col v-if="info" cols="6">
      <text-info
        label="地番"
        :value="address.subsector"
        :isUpdate="isUpdate"
        @input="val => (address.subsector = val)"
      />
      <range-date-picker
        v-if="isUpdate"
        label="契約期間"
        :dates="dates"
        @newDates="getRangeDate"
      />
    </v-col>
  </v-row>
</template>

<script>
import TextInfo from "./TextInfo";
import RangeDatePicker from "../RangeDatePicker";

export default {
  name: "forest-basic-info",

  components: {
    TextInfo,
    RangeDatePicker,
  },

  props: {
    info: Object,
    isUpdate: Boolean,
    isSave: Boolean,
  },

  methods: {
    getRangeDate(val) {
      this.contract.start_date = val[0];
      this.contract.end_date = val[1];
    },

    formatDate(date) {
      return date && date.replace(new RegExp("-", "g"), "/");
    },
  },

  computed: {
    address() {
      return this.innerInfo.cadastral;
    },

    contract() {
      return this.innerInfo.contracts[0];
    },

    innerInfo() {
      return this.info;
    },

    fullAddress() {
      let fullAddress = "";
      const address = this.address;
      if (address) {
        fullAddress =
          address.prefecture + address.municipality + address.sector;
      }
      return fullAddress;
    },

    fullDate() {
      let fullDate = "";
      const contract = this.contract;
      if (contract) {
        fullDate = `${this.formatDate(contract.start_date) || ''} ${contract.start_date ? '-' : ''} 
        ${this.formatDate(contract.end_date) || '未入力'}`;
      }
      return fullDate;
    },

    dates() {
      return [this.contract.start_date || "", this.contract.end_date || ""];
    },
  },

  watch: {
    isSave(val) {
      if (val) {
        this.$emit("updateInfo", this.innerInfo);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.forest-basic-info {
  .text-info {
    padding-bottom: 12px;
  }
}
</style>
