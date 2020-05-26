<template>
  <v-card>
    <v-card-title class="justify-start pb-0 px-6 pt-6">
      {{ line ? `行番号のエラー: ${line}` : "エラー" }}
    </v-card-title>
    <v-card-text class="pa-6">
      <v-container fluid class="pa-0">
        <v-row no-gutters v-for="(msgs, key) in errors" :key="key">
          <v-col cols="12">
            <template v-if="key === '__root__'">
              <p v-for="(msg, msgIndex) in msgs" :key="msgIndex">{{ msg }}</p>
            </template>
            <template v-else>
              <p class="mb-0">{{ key }}</p>
              <ul>
                <li v-for="(msg, msgIndex) in msgs" :key="msgIndex">
                  {{ msg }}
                </li>
              </ul>
            </template>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: {
    line: Number,
    errors: Object,
  },
};
</script>
>
