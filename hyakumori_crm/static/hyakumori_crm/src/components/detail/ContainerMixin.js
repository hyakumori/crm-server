export default {
  props: {
    isLoading: Boolean,
    headerContent: String,
    editBtnContent: String,
    addBtnContent: String,
  },

  methods: {
    cancel() {
      this.isUpdate = false;
    },
  },
};
