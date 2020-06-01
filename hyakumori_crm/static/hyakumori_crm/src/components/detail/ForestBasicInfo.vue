<template>
  <ValidationObserver ref="observer">
    <v-container class="forest-basic-info pa-0">
      <template v-if="!isUpdate">
        <v-row v-if="innerInfo" dense>
          <v-col cols="6">
            <text-info label="住所" :value="fullAddress" />
          </v-col>
          <v-col cols="6">
            <text-info
              label="字"
              name="字"
              rules="max:255"
              :value="address && address.subsector"
              :isUpdate="isUpdate"
              @input="val => (address.subsector = val)"
            />
          </v-col>
        </v-row>

        <v-row dense>
          <v-col cols="6">
            <text-info
              label="地番本番"
              :value="landAttributes && landAttributes['地番本番']"
            />
          </v-col>
          <v-col cols="6">
            <text-info
              label="地番支番"
              :value="landAttributes && landAttributes['地番支番']"
            />
          </v-col>
        </v-row>

        <v-row dense>
          <v-col cols="6">
            <text-info label="契約種類" :value="contractType">
              <template #readonly-extend v-if="contractStatus">
                <v-chip
                  small
                  class="contract-status"
                  outlined
                  color="primary"
                  >{{ contractStatus }}</v-chip
                >
              </template>
            </text-info>
          </v-col>
          <v-col cols="6">
            <text-info label="契約期間" :value="formattedContractPeriod" />
          </v-col>
        </v-row>

        <v-row dense>
          <v-col cols="6">
            <text-info label="FSC認証加入" :value="fscStatus" />
          </v-col>
          <v-col cols="6">
            <text-info label="FSC認証期間" :value="formattedFscPeriod" />
          </v-col>
        </v-row>
      </template>
      <template v-else>
        <v-row v-if="innerInfo">
          <v-col cols="4">
            <text-info
              label="都道府県"
              name="都道府県"
              rules="required|max:255"
              :value="address.prefecture"
              :isUpdate="isUpdate"
              @input="val => (address.prefecture = val)"
            />
          </v-col>
          <v-col cols="4">
            <text-info
              label="市町村"
              name="市町村"
              rules="required|max:255"
              :value="address.municipality"
              :isUpdate="isUpdate"
              @input="val => (address.municipality = val)"
            />
          </v-col>
          <v-col cols="4">
            <text-info
              label="大字"
              name="大字"
              rules="max:255"
              :value="address.sector"
              :isUpdate="isUpdate"
              @input="val => (address.sector = val)"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="4">
            <text-info
              label="地番本番"
              name="地番本番"
              rules="required|min_value:1"
              :value="landAttributes['地番本番']"
              :isUpdate="isUpdate"
              @input="val => (landAttributes['地番本番'] = val)"
            />
          </v-col>

          <v-col cols="4">
            <text-info
              label="地番支番"
              name="地番支番"
              rules="max:255"
              :value="landAttributes['地番支番']"
              :isUpdate="isUpdate"
              @input="val => (landAttributes['地番支番'] = val)"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="4">
            <select-info
              :items="contractTypes"
              label="契約種類"
              :value="contractType"
              @input="updateContractType"
              :isUpdate="isUpdate"
            />
          </v-col>
          <v-col cols="4">
            <select-info
              :items="contractStatusesSelectItems"
              label="契約ステータス"
              :value="contractStatus"
              @input="updateContractStatus"
              :isUpdate="isUpdate"
            />
          </v-col>
          <v-col cols="4">
            <range-date-picker
              label="契約期間"
              :dates="contractPeriod"
              @newDates="updateContractDate"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="4">
            <select-info
              :items="contractStatusesSelectItems"
              label="FSC認証加入"
              :value="fscStatus"
              @input="updateFscStatus"
              :isUpdate="isUpdate"
            />
          </v-col>
          <v-col cols="4">
            <range-date-picker
              label="FSC契約期間"
              :dates="fscPeriod"
              @newDates="updateFscDate"
            />
          </v-col>
          <v-col cols="4"> </v-col>
        </v-row>
      </template>
    </v-container>
  </ValidationObserver>
</template>

<script>
import TextInfo from "./TextInfo";
import SelectInfo from "./SelectInfo";
import RangeDatePicker from "../RangeDatePicker";
import { ValidationObserver } from "vee-validate";
import { get as _get, cloneDeep as _cloneDeep } from "lodash";

export default {
  name: "forest-basic-info",

  components: {
    TextInfo,
    SelectInfo,
    RangeDatePicker,
    ValidationObserver,
  },

  props: {
    info: Object,
    isUpdate: Boolean,
    isSave: Boolean,
  },

  data() {
    return {
      contractTypes: [],
      contractStatuses: {},
      innerInfo: {
        contracts: { contract_type: "" },
      },
    };
  },

  methods: {
    getRangeDate(val) {
      this.contract.start_date = val[0];
      this.contract.end_date = val[1];
    },
    formatDate(date) {
      return date; // && date.replace(new RegExp("-", "g"), "/");
    },
    async getContractTypes() {
      try {
        const response = await this.$rest.get("/contract_type");
        if (response) {
          this.contractTypes = response
            .filter(item => item.attributes && item.attributes.assignable)
            .map(item => ({
              text: item.name,
              value: item.name,
            }));
        }
      } catch {
        this.contractTypes = [];
      }
    },
    async getContractStatuses() {
      try {
        const response = await this.$rest.get("/contract_type/statuses");
        if (response) {
          this.contractStatuses = response;
        }
      } catch {
        this.contractStatuses = [];
      }
    },

    updateContractType(selected) {
      this.innerInfo.contracts.contract_type = selected.value;
    },
    updateContractDate(val) {
      this.innerInfo.contracts.contract_start_date = val[0];
      this.innerInfo.contracts.contract_end_date = val[1];
    },
    updateContractStatus(selected) {
      this.innerInfo.contracts.contract_status = selected.value;
    },
    updateFscStatus(selected) {
      this.innerInfo.contracts.fsc_status = selected.value;
    },
    updateFscDate(val) {
      this.innerInfo.contracts.fsc_start_date = val[0];
      this.innerInfo.contracts.fsc_end_date = val[1];
    },
  },

  async mounted() {
    await this.getContractTypes();
    await this.getContractStatuses();
    this.innerInfo = _cloneDeep(this.info);
  },

  computed: {
    fscStatus() {
      return _get(this.info, "contracts.fsc_status");
    },
    fscPeriod() {
      let start_date = _get(this.innerInfo, "contracts.fsc_start_date");
      let end_date = _get(this.innerInfo, "contracts.fsc_end_date");
      return [start_date || "", end_date || ""];
    },
    formattedFscPeriod() {
      let fullDate = "";
      const contract = this.contract;
      if (contract) {
        fullDate = `${this.formatDate(contract.fsc_start_date) || ""} ${
          contract.fsc_start_date ? " ～ " : ""
        }
        ${this.formatDate(contract.fsc_end_date) || "未入力"}`;
      }
      return fullDate;
    },
    contractType() {
      return _get(this.info, "contracts.contract_type");
    },
    contractStatus() {
      return _get(this.info, "contracts.contract_status");
    },
    address() {
      return this.innerInfo && this.innerInfo.cadastral;
    },
    contract() {
      return _get(this.innerInfo, "contracts");
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
    formattedContractPeriod() {
      let fullDate = "";
      const contract = this.contract;
      if (contract) {
        fullDate = `${this.formatDate(contract.contract_start_date) || ""} ${
          contract.contract_start_date ? " ～ " : ""
        }
        ${this.formatDate(contract.contract_end_date) || "未入力"}`;
      }
      return fullDate;
    },
    contractPeriod() {
      return [
        this.contract.contract_start_date || "",
        this.contract.contract_end_date || "",
      ];
    },
    contractStatusesSelectItems() {
      const items = Object.keys(this.contractStatuses).map(key => ({
        text: this.contractStatuses[key],
        value: this.contractStatuses[key],
      }));
      return items;
    },
    landAttributes() {
      return this.innerInfo && this.innerInfo["land_attributes"];
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
        this.innerInfo = _cloneDeep(this.info);
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
