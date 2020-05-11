<template>
  <div>
    <v-card class="log-card d-hover" flat>
      <div class="d-flex pa-4">
        <v-icon class="align-self-start">{{ icon }}</v-icon>

        <div class="log-card__info">
          <h5>{{ action }}</h5>
          <p>{{ info }}</p>
        </div>
      </div>

      <div class="align-self-center pr-4" v-if="!noRightAction">
        <v-btn v-acl-only="['admin', 'group_admin']" icon @click="onClick">
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>
      </div>
    </v-card>
  </div>
</template>

<script>
import { parseISO, format } from "date-fns";
export default {
  name: "log-card",

  props: {
    icon: String,
    action: String,
    date: String,
    editor: Object,
    type: String,
    noRightAction: { type: Boolean, default: false },
  },

  methods: {
    onClick() {
      // Handle click navigate
    },
  },

  computed: {
    editorFullname() {
      return `${this.editor.last_name} ${this.editor.first_name}`;
    },
    info() {
      if (this.date) {
        if (this.editor) {
          return `${format(parseISO(this.date), "yyyy/MM/dd")}・${
            this.editorFullname
          }`;
        } else {
          return this.date;
        }
      } else {
        return "";
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.log-card {
  display: flex;
  justify-content: space-between;
  width: 399px;
  height: 72px;
  margin-top: 12px;
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
  border-radius: 4px;

  &__info {
    margin-left: 20px;

    h5 {
      color: #444444;
      font-size: 14px;
      font-weight: normal;
    }

    p {
      color: #999999;
      font-size: 12px;
    }
  }
}
</style>
