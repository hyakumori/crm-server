import { flattenDeep, intersection, uniq } from "lodash";
import { getScopes, hasScope } from "../helpers/security";

import { makeTitle } from "../helpers/document";

const updateDocumentTitle = to => {
  // eg. if we have /some/deep/nested/route and /some, /deep, and /nested have titles, nested's will be chosen.
  const nearestWithTitle = to.matched
    .slice()
    .reverse()
    .find(r => r.meta && r.meta.title);

  // If a route with a title was found, set the document (page) title to that value.
  if (nearestWithTitle) document.title = makeTitle(nearestWithTitle.meta.title);
};

const setupRouter = router => {
  router.beforeEach((to, from, next) => {
    updateDocumentTitle(to, from);

    if (to.matched.some(record => record.meta.isPublic)) {
      return next();
    }

    if (localStorage.getItem("accessToken") == null) {
      return next({
        path: "/auth/login",
        params: { nextUrl: to.fullPath },
      });
    }

    if (to.matched.some(record => record.meta.isAdmin)) {
      if (hasScope("admin")) {
        return next();
      } else {
        return next({ name: "error-403" });
      }
    }

    if (
      to.matched.some(
        record => record.meta.scopes && record.meta.scopes.length > 0,
      )
    ) {
      const scopes = uniq(
        flattenDeep(to.matched.map(record => record.meta.scopes)),
      );
      const matchedScopes = intersection(scopes, getScopes());

      if (matchedScopes && matchedScopes.length > 0) {
        return next();
      } else {
        return next({ name: "error-403" });
      }
    }

    next();
  });
};

export default setupRouter;
