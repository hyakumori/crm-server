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

/**
 * Try to convert to searchable date time format with correct timezone (local to UTC)
 * Only support `YYYY-MM-DD HH:mm`, or `YYY`, `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, `HH`, `HH:mm`
 * eg:
 * 202
 * 2020
 * 2020-01
 * 2020-01-30
 * 2020-01-30 12:00 (GMT+7) -> 2020-01-30 05:00
 * @param dateTimeString
 * @param defaultIfEmpty
 * @param keepEmptyTime
 * @returns {string}
 */
export function dateTimeKeywordSearchFormat(
  dateTimeString,
  defaultIfEmpty = undefined,
  keepEmptyTime = false,
) {
  if (!defaultIfEmpty) {
    defaultIfEmpty = {
      year: 0,
      month: 0,
      day: 0,
      hours: 12,
      minutes: 0,
      seconds: 0,
    };
  }
  if (dateTimeString.indexOf(" ") < 0) {
    //possible inputting a year
    if (dateTimeString.length > 2 && dateTimeString.indexOf(":") < 0) {
      return dateTimeString;
    }

    //input time
    const timeParts = dateTimeString.split(":");
    let date = new Date();
    date.setHours(timeParts[0]);
    if (timeParts.length === 1) {
      date = date.toISOString();
      return `${date.substr(11, 2)}`;
    }

    date.setHours(timeParts[0]);
    date.setMinutes(timeParts[1]);
    date = date.toISOString();

    return `${date.substr(11, 5)}`;
  }

  //in case input year and time
  const datetimeParts = dateTimeString.split(" ");
  const dateString = datetimeParts[0];
  const timeString = datetimeParts.length > 1 ? datetimeParts[1] : "";

  const dateParts = dateString.split("-");
  const timeParts = timeString.split(":");

  const parts = {
    year: (dateParts.length > 0 && dateParts[0]) || defaultIfEmpty.year,
    month: (dateParts.length > 1 && dateParts[1]) || defaultIfEmpty.month,
    day: (dateParts.length > 2 && dateParts[2]) || defaultIfEmpty.day,
    hours: (timeParts.length > 0 && timeParts[0]) || defaultIfEmpty.hours,
    minutes: (timeParts.length > 1 && timeParts[1]) || defaultIfEmpty.minutes,
  };

  if (parts.month === 0) {
    return parts.year;
  }
  if (parts.month > 0 && parts.day === 0) {
    return `${parts.year}-${parts.month}`;
  }

  if (parts.day === 0) {
    return dateTimeString;
  }

  if (parts.hours === 0) {
    return `${parts.year}-${parts.month}-${parts.day}`;
  }

  const utcDateTime = toUtcDatetime(dateTimeString, false);
  const date = new Date(utcDateTime).toISOString();

  if (keepEmptyTime) {
    return `${date.substr(0, 10)} ${date.substr(11, 8)}`;
  }
  if (timeParts.length === 1) {
    return `${date.substr(0, 10)} ${date.substr(11, 2)}`;
  }
  return `${date.substr(0, 10)} ${date.substr(11, 5)}`;
}

export function getTime(datetime) {
  return format(new Date(datetime), "HH:mm");
}

export function getDate(datetime) {
  return format(new Date(datetime), "yyyy-MM-dd");
}
