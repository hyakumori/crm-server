<template>
  <main-section class="forest-detail">
    <template #section>
      <div class="forest-detail__section px-7">
        <content-header
          content="基本情報 (登記情報)"
          editBtnContent="所有地を追加・編集"
          :update="isUpdate.basicInfo"
          @update="val => (isUpdate.basicInfo = val)"
        />
        <div class="my-4">
          <basic-info :infos="getBasicInfo" :isUpdate="isUpdate.basicInfo" />
          <update-button
            class="mt-n3 mb-12"
            v-if="isUpdate.basicInfo"
            :cancel="cancel.bind(this, 'basicInfo')"
          />
        </div>

        <content-header
          content="所有林情報"
          editBtnContent="所有者を追加・編集"
          :update="isUpdate.contact"
          @update="val => (isUpdate.contact = val)"
        />
        <contact-tab
          class="mt-5"
          :class="{ 'mb-9': !isUpdate.contact }"
          :ownerContacts="getContacts"
          :contactorContacts="getContacts"
          :isUpdate="isUpdate.contact"
        />
        <addition-button v-if="isUpdate.contact" content="連絡者を追加" />
        <update-button
          class="mb-9 mt-2"
          v-if="isUpdate.contact"
          :cancel="cancel.bind(this, 'contact')"
        />

        <content-header
          content="協議履歴"
          editBtnContent="協議記録を追加・編集"
          :update="isUpdate.discussion"
          @update="val => (isUpdate.discussion = val)"
        />
        <template v-if="isExpand">
          <history-discussion
            class="mt-4"
            :isUpdate="isUpdate.discussion"
            :discussions="getDiscussionsExpand"
          />
        </template>
        <template v-else>
          <history-discussion
            class="mt-4"
            :isUpdate="isUpdate.discussion"
            :discussions="getDiscussionsNotExpand"
          />
        </template>
        <addition-button
          class="mb-3"
          v-if="isUpdate.discussion"
          content="協議履歴を追加"
        />
        <update-button
          v-if="isUpdate.discussion"
          :cancel="cancel.bind(this, 'discussion')"
        />
        <p class="forest-detail__expand" @click="expandDiscussionList">
          {{ isExpand ? '一部表示する' : 'すべて表示する' }}
        </p>

        <content-header
          content="書類郵送記録"
          editBtnContent="書類郵送記録を追加・編集"
          :update="isUpdate.archive"
          @update="val => (isUpdate.archive = val)"
        />
        <history-discussion
          class="mt-4"
          :class="{ 'pb-9': !isUpdate.archive }"
          :discussions="getDiscussionsNotExpand"
          :isUpdate="isUpdate.archive"
        />
        <addition-button
          class="mb-3"
          v-if="isUpdate.archive"
          content="協議履歴を追加"
        />
        <update-button
          v-if="isUpdate.archive"
          :cancel="cancel.bind(this, 'archive')"
        />

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
        <forest-attribute-table :attributes="generateForestAttributeData" />
      </div>
    </template>

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
import ContactTab from "../components/detail/ContactTab";
import info from "../assets/dump/forest_detail.json";
import contacts from "../assets/dump/contact_card.json";
import discussions from "../assets/dump/history_discussion.json";
import actionLogs from "../assets/dump/action_log.json";
import HistoryDiscussion from "../components/detail/HistoryDiscussionCard";
import LogCard from "../components/detail/LogCard";
import UpdateButton from "../components/detail/UpdateButton";
import AdditionButton from "../components/AdditionButton";
import BasicInfo from "../components/detail/BasicInfo";
import ForestAttributeTable from "../components/detail/ForestAttributeTable";

export default {
  name: "forest-detail",

  mixins: [ScreenMixin],

  components: {
    MainSection,
    ContentHeader,
    ContactTab,
    HistoryDiscussion,
    LogCard,
    UpdateButton,
    AdditionButton,
    BasicInfo,
    ForestAttributeTable,
  },

  data() {
    return {
      pageIcon: this.$t("icon.forest_icon"),
      backBtnContent: this.$t("page_header.forest_list"),
      headerTagColor: "#FFC83B",
      isExpand: false,
      isUpdate: {
        basicInfo: false,
        contact: false,
        discussion: false,
        archive: false,
      },
    };
  },

  mounted() {
    const forestInfo = this.getInfo;
    if (forestInfo) {
      const headerInfo = {
        title: forestInfo.internal_id,
        subTitle: forestInfo.owner.name_kanji,
        tag: forestInfo.tag.danchi,
      };
      this.$store.dispatch("setHeaderInfo", headerInfo);
    }
  },

  methods: {
    expandDiscussionList() {
      this.isExpand = !this.isExpand;
    },

    cancel(val) {
      this.isUpdate[val] = false;
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
  },

  computed: {
    getContacts() {
      return contacts;
    },

    getDiscussionsNotExpand() {
      const discuss = discussions.slice(0, 3);
      return discuss;
    },

    getDiscussionsExpand() {
      return discussions;
    },

    getInfo() {
      return info;
    },

    getBasicInfo() {
      return [
        {
          label: "住所",
          value: info.cadastral.prefecture + info.cadastral.municipality,
        },
        {
          label: "契約期間",
          value: this.forestContractDateRange(info),
        },
        {
          label: "地番",
          value: info.cadastral.subsector,
        },
      ];
    },

    getActionLogs() {
      return actionLogs;
    },

    headerData() {
      const attr = info.forest_attributes;
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
    },

    generateForestAttributeData() {
      const attr = info.forest_attributes;
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

  &__expand {
    margin-top: 20px;
    margin-bottom: 50px;
    width: fit-content;
    color: #999999;

    &:hover {
      cursor: pointer;
    }
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
