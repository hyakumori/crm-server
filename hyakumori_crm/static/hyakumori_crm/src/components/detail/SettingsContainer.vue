<script>
import SectionContainerWrapper from "@/components/SectionContainerWrapper";
import ContainerMixin from "@/components/detail/ContainerMixin";
import { ValidationProvider, extend } from "vee-validate";
import { debounce } from "lodash";

export default {
  mixins: [ContainerMixin],
  components: { SectionContainerWrapper, ValidationProvider },
  data() {
    return {
      isLoading_: false,
      contractTypes: [],
      contractTypeInput: "",
    };
  },
  created() {
    extend("contractTypeDuplicate", this.contractTypeDuplicateValidate);
    this.debounceToggleActive = debounce(this.toggleActive, 300);
  },
  async mounted() {
    try {
      this.contractTypes = await this.$rest.get("/contract_type");
    } catch {}
  },
  computed: {
    contractTypeNames() {
      return this.contractTypes.map(ct => ct.name);
    },
  },
  methods: {
    async addContractTypeBtnClick() {
      try {
        const newType = await this.$rest.post("/contract_type", {
          name: this.contractTypeInput,
        });
        this.contractTypes.push(newType);
        this.contractTypeInput = "";
        this.$refs.contractTypeForm.reset();
      } catch {}
    },
    contractTypeDuplicateValidate(val) {
      return (
        !this.contractTypeNames.includes(val) ||
        "契約種類を重複することはできません"
      );
    },
    toggleActive(id, val) {
      this.$rest.put(`contract_type/${id}/toggle-active`, { active: val });
    },
  },
};
</script>

<template>
  <section-container-wrapper
    headerContent="設定"
    :toggleEditBtnContent="toggleEditBtnContent"
    :addBtnContent="addBtnContent"
    :isLoading="isLoading_"
    :isEditing="isEditing"
    @toggleEdit="val => (isEditing = val)"
    :cancelEdit="() => {}"
    :addBtnClickHandler="null"
    :saveDisabled="false"
    :save="() => {}"
    :saving="saving"
    :displayAdditionBtn="false"
  >
    <template>
      <v-row>
        <v-col cols="6" id="contract-type">
          <h5 class="mb-3">契約種類</h5>
          <ValidationProvider
            ref="contractTypeForm"
            slim
            mode="eager"
            v-slot="{ invalid, errors }"
            rules="required|contractTypeDuplicate"
            name="contract_type"
          >
            <div class="d-flex justify-space-between">
              <v-text-field
                ref="contractTypeInput"
                single-line
                dense
                outlined
                height="42"
                type="text"
                placeholder="契約種類入力"
                :error-messages="errors[0]"
                @keyup.enter="
                  () => {
                    !invalid && addContractTypeBtnClick();
                  }
                "
                v-model="contractTypeInput"
              ></v-text-field>
              <v-btn
                class="ml-3"
                color="primary"
                :disabled="invalid"
                @click="addContractTypeBtnClick"
                >{{ $t("buttons.add") }}</v-btn
              >
            </div>
          </ValidationProvider>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="font-weight-black text-left">名前</th>
                  <th class="text-left"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in contractTypes" :key="c.id">
                  <td>{{ c.name }}</td>
                  <td>
                    <v-checkbox
                      class="my-0"
                      hide-details
                      :input-value="c.attributes.assignable"
                      label="オン"
                      @change="debounceToggleActive(c.id, $event)"
                    ></v-checkbox>
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-col>
      </v-row>
    </template>
  </section-container-wrapper>
</template>
