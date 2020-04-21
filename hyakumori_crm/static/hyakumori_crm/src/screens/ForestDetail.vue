<template>
  <main-section class="forest-detail">
    <template #section>
      <div class="forest-detail__section px-7">
        <basic-info-container
          headerContent="基本情報 (登記情報)"
          editBtnContent="所有地を追加・編集"
          :isLoading="basicInfo.length === 0"
          :info="basicInfo"
        />

        <forest-contact-tab-container
          headerContent="所有林情報"
          editBtnContent="所有者を追加・編集"
          addBtnContent="連絡者を追加"
          :ownerContacts="ownerContacts"
        />

        <attachment-container
          class="consultation-history"
          headerContent="協議履歴"
          editBtnContent="協議記録を追加・編集"
          addBtnContent="協議履歴を追加"
          :attaches="attaches"
        />

        <attachment-container
          class="document-mailing-record"
          headerContent="書類郵送記録"
          editBtnContent="書類郵送記録を追加・編集"
          addBtnContent="協議履歴を追加"
          :attaches="attaches"
          :isRequiredExpand="false"
        />

        <div id="forest-attributes">
          <content-header
            class="mt-9"
            content="森林情報"
            :displayAdditionBtn="false"
          />
          <v-row class="forest-detail__header d-flex mx-0 mt-5">
            <template v-for="(header, index) in headerData">
              <v-col class="forest-detail__header--text" cols="3" :key="index">
                <td class="pr-2">{{ header.name }}</td>
                <td class="forest-detail__header--text__data--color">
                  {{ header.data }}
                </td>
              </v-col>
            </template>
          </v-row>
          <forest-attribute-table
            :attributes="forrestAttributes"
            :isLoading="forrestAttributes.length === 0"
          />
        </div>
      </div>
    </template>moduleName
    <template #right>
      <div class="forest-detail__log ml-6">
        <h4 class="mb-1">更新履歴</h4>
        <log-card
          v-for="(log, index) in getActionLogs"
          :key="index"
          :action="log.action"
          :date="log.date"
          :editor="log.editor"
        />
      </div>
    </template>
  </main-section>
</template>

<script>
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import ContentHeader from "../components/detail/ContentHeader";
import discussions from "../assets/dump/history_discussion.json";
import actionLogs from "../assets/dump/action_log.json";
import LogCard from "../components/detail/LogCard";
import ForestContactTabContainer from "../components/detail/ForestContactTabContainer";
import BasicInfoContainer from "../components/detail/BasicInfoContainer";
import AttachmentContainer from "../components/detail/AttachmentContainer";
import ForestAttributeTable from "../components/detail/ForestAttributeTable";
import { fetchBasicInfo, fetchForestOwner } from "../api/forest";

export default {
  name: "forest-detail",

  mixins: [ScreenMixin],

  components: {
    MainSection,
    ContentHeader,
    LogCard,
    ForestAttributeTable,
    BasicInfoContainer,
    AttachmentContainer,
    ForestContactTabContainer,
  },

  data() {
    return {
      forestId: this.$route.params.id,
      forestInfo: null,
      forestOwners: null,
      pageIcon: this.$t("icon.forest_icon"),
      backBtnContent: this.$t("page_header.forest_mgmt"),
      headerTagColor: "#FFC83B",
    };
  },

  mounted() {
    this.$rest
      .all([fetchBasicInfo(this.forestId), fetchForestOwner(this.forestId)])
      .then(
        this.$rest.spread((basicInfo, owners) => {
          this.forestInfo = basicInfo;
          this.forestOwners = owners.results;
          this.setHeaderInfo(basicInfo);
        }),
      )
      .catch(() => this.$router.push({ name: "not-found" }));
  },

  methods: {
    setHeaderInfo(info) {
      const headerInfo = {
        title: info.internal_id,
        subTitle: info.owner.name_kanji,
        tag: [info.tag.danchi],
        backUrl: { name: "forests" },
      };
      this.$store.dispatch("setHeaderInfo", headerInfo);
    },

    forestContractDateRange(info) {
      const longTermContract = info.contracts[0];
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

    fallbackText(text) {
      return text || "";
    },
  },

  computed: {
    ownerContacts() {
      let owners = [];
      if (this.forestOwners) {
        return this.forestOwners.map(owner => this.mapContact(owner));
      }
      return owners;
    },

    attaches() {
      return discussions;
    },

    basicInfo() {
      let basicInfo = [];
      const forestInfo = this.forestInfo;
      if (forestInfo) {
        const cadas = forestInfo.cadastral;
        basicInfo = [
          {
            label: "住所",
            value: cadas.prefecture + cadas.municipality + cadas.sector,
          },
          {
            label: "契約期間",
            value: this.forestContractDateRange(forestInfo),
          },
          {
            label: "地番",
            value: cadas.subsector,
          },
        ];
      }
      return basicInfo;
    },

    getActionLogs() {
      return actionLogs;
    },

    headerData() {
      let headerData = [];
      const forestInfo = this.forestInfo;
      if (forestInfo) {
        const attr = forestInfo.forest_attributes;
        return [
          {
            name: "地番面積_ha",
            data: attr["地番面積_ha"],
          },
          {
            name: "面積_ha",
            data: attr["面積_ha"],
          },
          {
            name: "面積_m2",
            data: attr["面積_m2"],
          },
          {
            name: "平均傾斜度",
            data: attr["平均傾斜度"],
          },
        ];
      }
      return headerData;
    },

    forrestAttributes() {
      let attributes = [];
      const forestInfo = this.forestInfo;
      if (forestInfo) {
        const attr = forestInfo.forest_attributes;
        return [
          {
            area: "林相ID",
            unit: "",
            first_area: attr["第1林相ID"],
            second_area: attr["第2林相ID"],
            third_area: attr["第3林相ID"],
          },
          {
            area: "林相名",
            unit: "ha",
            first_area: attr["第1林相名"],
            second_area: attr["第2林相名"],
            third_area: attr["第3林相名"],
          },
          {
            area: "Area",
            unit: "",
            first_area: attr["第1Area"],
            second_area: attr["第2Area"],
            third_area: attr["第3Area"],
          },
          {
            area: "面積_ha",
            unit: "",
            first_area: attr["第1面積_ha"],
            second_area: attr["第2面積_ha"],
            third_area: attr["第3面積_ha"],
          },
          {
            area: "立木本",
            unit: "",
            first_area: attr["第1立木本"],
            second_area: attr["第2立木本"],
            third_area: attr["第3立木本"],
          },
          {
            area: "立木密",
            unit: "本/ha",
            first_area: attr["第1立木密"],
            second_area: attr["第2立木密"],
            third_area: attr["第3立木密"],
          },
          {
            area: "平均樹",
            unit: "m",
            first_area: attr["第1平均樹"],
            second_area: attr["第2平均樹"],
            third_area: attr["第3平均樹"],
          },
          {
            area: "樹冠長 ",
            unit: "%",
            first_area: attr["第1樹冠長"],
            second_area: attr["第2樹冠長"],
            third_area: attr["第3樹冠長"],
          },
          {
            area: "平均DBH",
            unit: "cm",
            first_area: attr["第1平均DBH"],
            second_area: attr["第2平均DBH"],
            third_area: attr["第3平均DBH"],
          },
          {
            area: "合計材",
            unit: "m2",
            first_area: attr["第1合計材"],
            second_area: attr["第2合計材"],
            third_area: attr["第3合計材"],
          },
          {
            area: "ha材積 ",
            unit: "m2/ha",
            first_area: attr["第1ha材積"],
            second_area: attr["第2ha材積"],
            third_area: attr["第3ha材積"],
          },
          {
            area: "収量比",
            unit: "",
            first_area: attr["第1収量比"],
            second_area: attr["第2収量比"],
            third_area: attr["第3収量比"],
          },
          {
            area: "相対幹",
            unit: "",
            first_area: attr["第1相対幹"],
            second_area: attr["第2相対幹"],
            third_area: attr["第3相対幹"],
          },
          {
            area: "形状比",
            unit: "%",
            first_area: attr["第1形状比"],
            second_area: attr["第2形状比"],
            third_area: attr["第3形状比"],
          },
        ];
      }
      return attributes;
    },
  },
};
</script>

<style lang="scss" scoped>
@import "../styles/variables";

.forest-detail {
  &__section {
    @extend %detail-section-shared;
  }

  &__header {
    &--text {
      display: flex;
      justify-content: center;
      font-size: 14px;
      color: #444444;
      font-weight: bold;

      &__data--color {
        color: #579513;
      }
    }
  }
}
</style>
