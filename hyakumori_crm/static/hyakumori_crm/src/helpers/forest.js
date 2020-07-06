export function getForestDisplayName(forest) {
  const sector = forest.cadastral.sector;
  const lotnumber = forest.land_attributes["地番本番"] || "";
  const sub_lotnumber = forest.land_attributes["地番支番"]
    ? "-" + forest.land_attributes["地番支番"]
    : "";
  return `${sector} ${lotnumber}${sub_lotnumber}`;
}
