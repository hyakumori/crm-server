import { formatDistanceToNow, parseISO, format } from "date-fns";
import { zonedTimeToUtc } from "date-fns-tz";

import { ja } from "date-fns/locale";

export function fromNow(dateTimeString) {
  if (!dateTimeString) {
    return;
  }
  return formatDistanceToNow(parseISO(dateTimeString), {
    addSuffix: true,
    locale: ja,
  });
}

export function commonDatetimeFormat(datetime) {
  return datetime && format(new Date(datetime), "yyyy-MM-dd HH:mm");
}

export function toUtcDatetime(datetime, toISOString = true) {
  const currentTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const utcDateTime = zonedTimeToUtc(datetime, currentTimezone);
  if (toISOString) {
    return utcDateTime.toISOString();
  } else {
    return utcDateTime;
  }
}

export function getTime(datetime) {
  return format(new Date(datetime), "HH:mm");
}

export function getDate(datetime) {
  return format(new Date(datetime), "yyyy-MM-dd");
}

export const dateSeparator = "～";
