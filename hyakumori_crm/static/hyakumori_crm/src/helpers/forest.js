export function getForestDisplayName(forest) {
  const sector = forest.cadastral.sector;
  const lotnumber = forest.land_attributes["地番本番"] || "";
  const sub_lotnumber = forest.land_attributes["地番支番"]
    ? "-" + forest.land_attributes["地番支番"]
    : "";
  return `${sector} ${lotnumber}${sub_lotnumber}`;
}

export function getForestReprOwner(forest) {
  const names_kanji = forest?.attributes?.customer_cache?.repr_name_kanji || "";
  return names_kanji.split(",")[0];
}
