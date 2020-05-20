<template>
  <main-section class="forest-detail">
    <template #section>
      <div class="forest-detail__section px-7">
        <forest-basic-info-container
          headerContent="基本情報 (登記情報)"
          toggleEditBtnContent="追加・編集"
          @forest:basic-info-updated="$store.dispatch('forest/getForest', id)"
          :isLoading="$store.state.forest.forestLoading"
          :info="$store.state.forest.forest"
        />

        <forest-contact-tab-container
          v-acl-only="['manage_customer', 'view_customer']"
          headerContent="所有者情報"
          toggleEditBtnContent="追加・編集"
          addBtnContent="追加"
          :customers="$store.state.forest.customers"
          :customersContacts="$store.state.forest.customersContacts"
          :customerIdNameMap="$store.getters['forest/customerIdNameMap']"
          :isLoading="$store.state.forest.customersLoading"
          @saved="$store.dispatch('forest/getCustomers', id)"
          @savedCustomersContacts="
            $store.dispatch('forest/getCustomersContacts', id)
          "
          :id="id"
        />

        <attachment-container
          v-acl-only="['manage_archive', 'view_archive']"
          class="consultation-history"
          headerContent="協議履歴"
          toggleEditBtnContent="追加・編集"
          addBtnContent="追加"
          :archives="$store.state.forest.archives"
        />

        <div id="forest-attributes">
          <content-header
            class="mt-9"
            content="森林情報"
            :permissions="['just_unnecessary']"
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
    </template>
    <template #right>
      <div>
        <memo-input
          :api-url="`/forests/${$route.params.id}/memo`"
          object-type="forest"
          v-model="forestInfo"
        ></memo-input>
        <tag-detail-card
          app-name="crm"
          object-type="forest"
          :object-id="$route.params.id"
          :tags="forestInfo && forestInfo.tags"
          @input="$store.dispatch('setHeaderTagInfo', $event)"
        ></tag-detail-card>
        <action-log
          app-name="crm"
          object-type="forest"
          :object-id="$route.params.id"
        ></action-log>
      </div>
    </template>
  </main-section>
</template>

<script>
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import ContentHeader from "../components/detail/ContentHeader";
import ForestContactTabContainer from "../components/detail/ForestContactTabContainer";
import ForestBasicInfoContainer from "../components/detail/ForestBasicInfoContainer";
import AttachmentContainer from "../components/detail/AttachmentContainer";
import ForestAttributeTable from "../components/detail/ForestAttributeTable";
import ActionLog from "../components/detail/ActionLog";
import MemoInput from "../components/detail/MemoInput";
import TagDetailCard from "../components/tags/TagDetailCard";

export default {
  name: "forest-detail",

  mixins: [ScreenMixin],

  components: {
    MainSection,
    ContentHeader,
    ActionLog,
    MemoInput,
    TagDetailCard,
    ForestAttributeTable,
    ForestBasicInfoContainer,
    AttachmentContainer,
    ForestContactTabContainer,
  },
  props: {
    id: String,
  },
  data() {
    return {
      forestOwners: null,
      pageIcon: this.$t("icon.forest_icon"),
      backBtnContent: this.$t("page_header.forest_mgmt"),
      headerTagColor: "#FFC83B",
    };
  },
  created() {
    this.$store.dispatch("forest/getForest", this.id).then(() => {
      this.$store.dispatch(
        "setHeaderInfo",
        this.$store.getters["forest/headerInfo"],
      );
    });
    this.$store.dispatch("forest/getCustomers", this.id);
    this.$store.dispatch("forest/getCustomersContacts", this.id);
    this.$store.dispatch("forest/getArchives", this.id);
  },
  methods: {
    fallbackText(text) {
      return text || "";
    },
  },
  computed: {
    forestInfo: {
      get() {
        return this.$store.state.forest.forest;
      },
      set(val) {
        this.$store.commit("forest/setForest", val);
      },
    },

    headerData() {
      let headerData = [];
      const forestInfo = this.forestInfo;

      if (forestInfo) {
        const attr = forestInfo.forest_attributes;
        return (
          attr && [
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
          ]
        );
      }
      return headerData;
    },

    forrestAttributes() {
      let attributes = [];
      const forestInfo = this.$store.state.forest.forest;
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
