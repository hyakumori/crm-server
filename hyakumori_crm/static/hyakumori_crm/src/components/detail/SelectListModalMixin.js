import { debounce, reject } from "lodash";

export default {
  created() {
    this.debounceLoadInitItemsForAdding = debounce(
      this.loadInitItemsForAdding,
      500,
    );
  },
  data() {
    /*
     * itemsForAddingUrl: { type: String }
     */
    return {
      itemsForAddingLoading: false,
      itemsForAdding: { results: [] },
      showSelect: false,
      modalSelectingId: null,
      modalSelectingIndex: null,
      showNotFoundMsg: false,
      showOutOfDataMsg: false,
    };
  },
  methods: {
    onCancel() {
      this.modalSelectingId = null;
      this.modalSelectingIndex = null;
    },
    async loadInitItemsForAdding(keyword) {
      let reqConfig = keyword
        ? {
            params: {
              search: keyword || "",
            },
          }
        : {};
      this.itemsForAddingLoading = true;
      let resp = { next: this.itemsForAddingUrl };
      while (resp.next) {
        resp = await this.$rest.get(resp.next, reqConfig);
        this.itemsForAdding = {
          next: resp.next,
          previous: resp.previous,
          results: reject(resp.results, this.itemsForAddingResultFilter),
        };
        this.showNotFoundMsg =
          !resp.next && !resp.previous && resp.results.length === 0;
        if (this.itemsForAdding.results.length > 5) break;
        if (resp.next && resp.next.indexOf("page=") > -1) reqConfig = {};
      }
      this.itemsForAddingLoading = false;
    },
    async handleLoadMore() {
      if (!this.itemsForAdding.next || this.itemsForAddingLoading) return;
      this.itemsForAddingLoading = true;
      const resp = await this.$rest.get(this.itemsForAdding.next);
      this.itemsForAdding = {
        next: resp.next,
        previous: resp.previous,
        results: [
          ...this.itemsForAdding.results,
          ...reject(resp.results, this.itemsForAddingResultFilter),
        ],
      };
      this.itemsForAddingLoading = false;
    },
  },
  watch: {
    showSelect(val) {
      if (val && this.itemsForAdding.results.length === 0) {
        if (this.$refs.selectListModal.isSearchEmpty)
          this.loadInitItemsForAdding();
        else {
          // this will auto triggers load items
          this.$refs.selectListModal.clearSearch();
        }
      }
    },
  },
};
