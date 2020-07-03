export function getForestDisplayName(forest) {
  const sector = forest.cadastral.sector ? forest.cadastral.sector + "_" : "";
  const subsector = forest.cadastral.subsector
    ? forest.cadastral.subsector + "_"
    : "";
  const lotnumber = forest.land_attributes["地番本番"] || "";
  const sub_lotnumber = forest.land_attributes["地番支番"]
    ? "_" + forest.land_attributes["地番支番"]
    : "";
  return `${sector}${subsector}${lotnumber}${sub_lotnumber}`;
}
