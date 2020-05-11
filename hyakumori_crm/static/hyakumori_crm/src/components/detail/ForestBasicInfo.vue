<template>
  <ValidationObserver ref="observer">
    <v-row class="forest-basic-info">
      <v-col v-if="info" cols="6">
        <template v-if="isUpdate">
          <text-info
            label="都道府県"
            name="都道府県"
            rules="max:255"
            :value="address.prefecture"
            :isUpdate="isUpdate"
            @input="val => (address.prefecture = val)"
          />
          <text-info
            label="市町村"
            name="市町村"
            rules="max:255"
            :value="address.municipality"
            :isUpdate="isUpdate"
            @input="val => (address.municipality = val)"
          />
          <text-info
            label="大字"
            name="大字"
            rules="max:255"
            :value="address.sector"
            :isUpdate="isUpdate"
            @input="val => (address.sector = val)"
          />
        </template>
        <text-info v-else label="住所" :value="fullAddress" />
        <text-info v-if="!isUpdate" label="契約期間" :value="fullDate" />
      </v-col>
      <v-col v-if="info" cols="6">
        <text-info
          label="地番"
          name="地番"
          rules="max:255"
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
  </ValidationObserver>
</template>

<script>
import TextInfo from "./TextInfo";
import RangeDatePicker from "../RangeDatePicker";
import { ValidationObserver } from "vee-validate";

export default {
  name: "forest-basic-info",

  components: {
    TextInfo,
    RangeDatePicker,
    ValidationObserver,
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
        fullDate = `${this.formatDate(contract.start_date) || ""} ${
          contract.start_date ? "-" : ""
        }
        ${this.formatDate(contract.end_date) || "未入力"}`;
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

    info: {
      deep: true,
      async handler() {
        const isValid = await this.$refs.observer.validate();
        this.$emit("forest:save-disable", !isValid);
      },
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
