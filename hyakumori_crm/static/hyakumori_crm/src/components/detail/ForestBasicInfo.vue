<template>
  <v-row>
    <v-col cols="6">
      <text-info
        title="住所"
        :info="info.cadastral.prefecture + info.cadastral.municipality"
        :isUpdate="isUpdate"
      />
      <text-info
        title="地番"
        :info="info.cadastral.subsector"
        :isUpdate="isUpdate"
      />
    </v-col>
    <v-col cols="6">
      <text-info
        title="契約期間"
        :info="forestContractDateRange"
        :isUpdate="isUpdate"
      />
    </v-col>
  </v-row>
</template>

<script>
import TextInfo from "../detail/TextInfo";

export default {
  name: "forest-basic-info",

  components: {
    TextInfo,
  },

  props: {
    isUpdate: Boolean,
    info: Object,
  },

  computed: {
    forestContractDateRange() {
      const longTermContract = this.info.contracts[0];
      if (longTermContract) {
        if (longTermContract.start_date) {
          if (longTermContract.end_date) {
            return `${longTermContract.start_date} - ${longTermContract.end_date}`;
          } else {
            return `${longTermContract.start_date} - `;
          }
        } else {
          return "";
        }
      } else {
        return "";
      }
    },
  },
};
</script>
