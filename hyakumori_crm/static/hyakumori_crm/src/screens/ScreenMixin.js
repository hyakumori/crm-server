export default {
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
  },
};
