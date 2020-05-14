<template>
  <div class="attachments">
    <content-header
      class="mb-3"
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="loading"
      @toggleEdit="handleToggleEdit"
    />
    <document-card
      class="my-2"
      v-for="(doc, index) in documents"
      flat
      :isUpdating="isUpdate"
      :key="index"
      :fileName="doc.filename || doc.name"
      :attachment="doc"
      :added="doc.added"
      :deleted="doc.deleted"
      :loading="doc.loading"
      :deleteClick="onDeleteClick.bind(this, doc, index)"
      :downloadClick="onDownloadClick.bind(this, doc)"
      @undoDelete="handleUndoDelete(doc, index)"
    />
    <template v-if="isUpdate">
      <div class="attachments__addition-container">
        <addition-button
          class="mb-2"
          :content="addBtnContent"
          :click="onAdditionClick.bind(this)"
        />
        <input
          class="attachments__addition-container__file"
          ref="fileInput"
          type="file"
          accept=".xlsx, .xls, .csv, .doc, .docx, .pdf, .zip, .png, .jpg, .gif, .bmp, .tif"
          multiple
          @change="onFileChange"
        />
      </div>
      <update-button
        :cancel="cancel.bind(this)"
        :save="save.bind(this)"
        :save-disabled="saveDisabled"
        :saving="updateAttachmentLoading"
      />
      <v-dialog v-model="showDuplicateFileDialog" max-width="500">
        <v-card color="white">
          <v-card-title>
            以下のファイルが既に存在します。古いファイルを削除してから再度アップロードしてください。
          </v-card-title>
          <v-card-text>
            <ul>
              <li v-for="(file, index) in duplicateUploadFiles" :key="index">
                {{
                  (file.attributes && file.attributes.original_file_name) ||
                    file.name
                }}
              </li>
            </ul>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              text
              color="primary"
              @click="showDuplicateFileDialog = false"
              >{{ $t("raw_text.agree") }}</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>
    </template>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import DocumentCard from "./DocumentCard";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";
import { unionWith, isNil, cloneDeep, intersectionWith } from "lodash";
import { saveAs } from "file-saver";

export default {
  name: "archive-document-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    DocumentCard,
    UpdateButton,
    AdditionButton,
  },

  data() {
    return {
      id: this.$route.params.id,
      isUpdate: false,
      documents: [],
      fileRef: this.$refs.fileInput,
      updateAttachmentLoading: false,
      loading: false,
      deleteDocuments: [],
      immutableDocs: [],
      showDuplicateFileDialog: false,
      duplicateUploadFiles: [],
    };
  },

  mounted() {
    this.fetchAttachments();
  },

  methods: {
    handleToggleEdit(val) {
      this.isUpdate = val;
      this.immutableDocs = cloneDeep(this.documents);
    },

    cancel() {
      this.isUpdate = false;
      this.documents = this.immutableDocs;
      this.deleteDocuments = [];
    },

    async fetchAttachments() {
      this.loading = true;
      const attachments = await this.$rest(`/archives/${this.id}/attachments`);
      if (attachments) {
        this.loading = false;
        this.documents = attachments.data;
      }
    },

    onAdditionClick() {
      this.$refs.fileInput.click();
    },

    onDeleteClick(doc, index) {
      if (doc.added) {
        this.documents.splice(index, 1);
      } else {
        this.deleteDocuments.push(doc);
        this.$set(doc, "deleted", true);
      }
    },

    onDownloadClick(doc) {
      this.$set(doc, "loading", true);
      this.$rest
        .get(`/archives/${this.id}/attachments/${doc.id}/download`)
        .then(res => {
          const baseUrl = this.$rest.defaults.baseURL;
          const filename = res.filename;
          saveAs(baseUrl + res.url, filename);
          this.$set(doc, "loading", false);
        });
    },

    getDuplicateFiles(files1, files2) {
      return intersectionWith(
        files1,
        files2,
        (f1, f2) => (f1.attributes?.original_file_name || f1.name) === f2.name,
      );
    },

    removeDuplicateFiles(files1, files2) {
      return unionWith(files1, files2, (f1, f2) => {
        return (f1.name || f1.filename) === f2.name || f1.size === f2.size;
      });
    },

    onFileChange(e) {
      const files = e.target.files;
      const originalDocs = [...this.documents, ...files];
      this.duplicateUploadFiles = this.getDuplicateFiles(this.documents, files);
      const filteredDocs = this.removeDuplicateFiles(this.documents, files);
      if (originalDocs.length !== filteredDocs.length) {
        this.showDuplicateFileDialog = true;
      }
      this.documents = filteredDocs;
      this.documents.forEach(doc => {
        if (!doc.id) {
          doc.added = true;
        }
      });
    },

    async save() {
      if (this.documents.length === 0) {
        this.isUpdate = false;
        this.deleteDocuments = [];
      } else {
        this.updateAttachmentLoading = true;
        const data = new FormData();
        const newDocs = this.documents.filter(doc => isNil(doc.id));
        newDocs.forEach(doc => data.append("file", doc));
        if (newDocs.length > 0) {
          const newDocuments = await this.$rest.post(
            `archives/${this.id}/attachments`,
            data,
          );
          if (newDocuments) {
            this.documents.splice(
              this.documents.length - 1 - (newDocs.length - 1),
              newDocs.length,
              ...newDocuments.data,
            );
          }
        }
        if (this.deleteDocuments.length > 0) {
          this.deleteDocuments.forEach(doc => {
            this.$rest.delete(`/archives/${this.id}/attachments/${doc.id}`);
          });
        }
        this.documents = this.documents.filter(doc => !doc.deleted);
        this.updateAttachmentLoading = false;
        this.isUpdate = false;
        this.deleteDocuments = [];
      }
    },

    handleUndoDelete(doc, index) {
      this.$set(doc, "deleted", false);
      this.deleteDocuments.splice(index, 1);
    },
  },

  computed: {
    saveDisabled() {
      return (
        this.documents.filter(doc => doc.added || doc.deleted).length === 0
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.attachments {
  &__addition-container {
    position: relative;
    display: flex;

    &__file {
      position: absolute;
      height: 0;
      width: 0;
    }
  }
}
</style>
