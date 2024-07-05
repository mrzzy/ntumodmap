/*
 * NTUModmap
 * modschedule
 * Time Blocking
 */

import { parse } from "date-fns";
import { Block } from "./models";
import { dayOffset, range } from "./util";

/**
 * Parse the {@link Block}s from the given block CSV.
 *
 * @param csv Block CSV. See usage information for --block for format.
 * @returns parsed blocks from the given CSV.
 */
export function parseBlock(csv: string): Block[] {
  return (
    csv
      .split("\n")
      // skip header
      .slice(1)
      .flatMap((line) => {
        const [begin, end, duration, weekday, teachingWeek] = line
          .split(",")
          .map((s) => s.trim());
        // convert begin & end to offset since start of day
        const parseTime = (timeStr: string) =>
          dayOffset(parse(timeStr, "HHmm", new Date()));
        const [beginSecs, endSecs] = [parseTime(begin), parseTime(end)];
        if (beginSecs >= endSecs) {
          throw new Error(
            "Time block interval begin time should be before end time",
          );
        }

        return {
          beginSecs,
          endSecs,
          durationSecs:
            duration.length <= 0 ? endSecs - beginSecs : parseInt(duration),
          // generate weekday & teaching week ranges
          repeats: {
            weekdays:
              weekday.length <= 0
                ? range(1, 8)
                : [parse(weekday, "EEE", new Date()).getDay()],
            teachingWeeks:
              weekday.length <= 0 ? range(1, 15) : [parseInt(teachingWeek)],
          },
        };
      })
  );
}
