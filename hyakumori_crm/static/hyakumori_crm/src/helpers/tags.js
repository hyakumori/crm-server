const tags_to_array = (tags, showKey = false) => {
  /**
   * tags: object
   */
  const results = [];
  for (let key of Object.keys(tags)) {
    if (!tags[key]) {
      continue;
    }
    if (showKey) {
      results.push(`${key}:${tags[key]}`);
    } else {
      results.push(tags[key]);
    }
  }
  return results;
};

export { tags_to_array };
