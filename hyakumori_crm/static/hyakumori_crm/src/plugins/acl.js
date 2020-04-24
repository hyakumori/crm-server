import { getScopes, hasScope } from "../helpers/security";

const AclSetup = {
  install: (Vue, options) => {
    Vue.directive("acl-only", {
      inserted(el, binding, vnode, old) {
        if (
          binding.value &&
          binding.value.length > 0 &&
          binding.value.every(scope => !hasScope(scope))
        ) {
          vnode.elm.parentElement.removeChild(vnode.elm);
        }
      },
    });
  },
};

export default AclSetup;
