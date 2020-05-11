<template>
  <v-card class="login-form pa-0 elevation-24">
    <v-card-title class="justify-center pb-0 px-6 pt-6">
      {{ $t("page_header.not_found") }}
    </v-card-title>

    <v-card-text class="pa-6">
      <v-container fluid class="pa-0">
        <v-row no-gutters>
          <v-col cols="12">
            <img src="@/assets/img/404.png" width="100%" />
            <h2 class="text-center">
              {{ $t("messages.page_not_found_text") }}
            </h2>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-card-actions class="pa-6 pt-0">
      <v-container class="pa-0">
        <v-row class="fill-height">
          <v-col class="pt-0 pb-0 text-right" cols="12">
            <v-btn
              color="primary"
              depressed
              width="100%"
              @click="$router.go(-1)"
              >{{ $t("buttons.back") }}
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-card-actions>
  </v-card>
</template>
