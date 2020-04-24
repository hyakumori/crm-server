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

    mapContact(info) {
      const addr = info.address;
      return {
        customer_id: info.customer_id,
        fullname:
          this.fallbackText(info.name_kanji.last_name) +
          this.fallbackText(info.name_kanji.first_name),
        telephone: info.telephone,
        mobilephone: info.mobilephone,
        address: `${this.fallbackText(info.postal_code)}
          ${this.fallbackText(addr.prefecture)}
          ${this.fallbackText(addr.municipality)}
          ${this.fallbackText(addr.sector)}`,
        email: info.email,
      };
    },
  },
};
