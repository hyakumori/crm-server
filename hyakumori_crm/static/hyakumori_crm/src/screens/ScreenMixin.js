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
      const self_contact = info.self_contact;
      const addr = self_contact.address;
      const kanji_name = self_contact.name_kanji;
      return {
        customer_id: info.id,
        fullname:
          this.fallbackText(kanji_name.last_name) +
          this.fallbackText(kanji_name.first_name),
        telephone: self_contact.telephone,
        mobilephone: self_contact.mobilephone,
        forest_count: info.forests_count,
        address: `${this.fallbackText(self_contact.postal_code)}
          ${this.fallbackText(addr.prefecture)}
          ${this.fallbackText(addr.municipality)}
          ${this.fallbackText(addr.sector)}`,
        email: self_contact.email,
      };
    },
  },
};
