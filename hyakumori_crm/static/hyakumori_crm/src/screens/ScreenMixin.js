export default {
  data() {
    return {
      tableSelectedRows: [],
      tagKeys: [],
      showChangeTagDialog: false,
      fetchTagsLoading: false,
      updatingTags: false,
      selectedTagForUpdate: null,
    };
  },
  mounted() {
    this.populateAppHeader();
  },
  methods: {
    populateAppHeader() {
      this.$store.dispatch("setPageHeader", this.pageHeader);
      this.$store.dispatch("setPageIcon", this.pageIcon);
      this.$store.dispatch("setHeaderTagColor", this.headerTagColor);
      this.$store.dispatch("setBackBtnContent", this.backBtnContent);
    },

    async getSelectedObject(apiUrl) {
      try {
        const objects = await this.$rest.put(apiUrl, this.selectedRowIds);
        this.tagKeys = objects.data;
      } catch (e) {
        this.showChangeTagDialog = false;
      } finally {
        this.fetchTagsLoading = false;
      }
    },

    selectedRows(val) {
      this.tableSelectedRows = val;
    },

    resetActionChoices() {
      const actionListRef = this.$refs.actionRef.$children[0];
      const actionListRefChild = actionListRef.$children[0];
      this.selectedTagForUpdate = null;
      actionListRefChild.reset();
      actionListRef.resizeInputWidth();
    },
  },
  computed: {
    requestFilters() {
      return this.$refs.filter
        ? this.$refs.filter.conditions.map(condition => {
            return {
              criteria: condition.criteria,
              keyword: condition.keyword,
            };
          })
        : [];
    },

    selectedRowIds() {
      return (
        this.tableSelectedRows.length > 0 &&
        this.tableSelectedRows.map(row => row.id)
      );
    },
  },
};
