const getScopes = () => {
  let scopes = localStorage.getItem("scopes") || "";
  return (scopes && scopes.split(",")) || [];
};

const hasScope = scope => {
  return getScopes().indexOf(scope) !== -1;
};

const isLoggedIn = () => {
  return localStorage.getItem("accessToken") || false;
};

export { hasScope, getScopes, isLoggedIn };
