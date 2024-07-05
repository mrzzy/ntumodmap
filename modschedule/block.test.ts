/*
 * NTUModmap
 * modschedule
 * Time Blocking unit tests
 */

import { describe, expect, test } from "@jest/globals";
import { parseBlock } from "./block";
import { range } from "./util";

describe("parseBlock()", () => {
  test("parses time blocks", () => {
    expect(
      parseBlock(`begin,end,duration,weekday,teachingWeek
1100,1300,3600,,
1100,1300,,,
1700,1900,3000,MON,3`),
    ).toStrictEqual([
      {
        beginSecs: 39600,
        endSecs: 46800,
        durationSecs: 3600,
        repeats: {
          weekdays: range(1, 8),
          teachingWeeks: range(1, 15),
        },
      },
      {
        beginSecs: 39600,
        endSecs: 46800,
        durationSecs: 7200,
        repeats: {
          weekdays: range(1, 8),
          teachingWeeks: range(1, 15),
        },
      },
      {
        beginSecs: 61200,
        endSecs: 68400,
        durationSecs: 3000,
        repeats: {
          weekdays: [1],
          teachingWeeks: [3],
        },
      },
    ]);
  });
});
