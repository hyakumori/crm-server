export default {
  props: {
    isLoading: Boolean,
    headerContent: String,
    toggleEditBtnContent: String,
    addBtnContent: String,
  },
  data() {
    return {
      isEditing: false,
      saving: false,
    };
  },
  methods: {
    cancel() {
      this.isEditing = false;
    },
  },
};
