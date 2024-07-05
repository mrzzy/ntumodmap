/*
 * NTUModmap
 * modschedule
 * Timetable Search Unit Tests
 */

import { describe, test, expect } from "@jest/globals";
import { searchTimetable } from "./search";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { range } from "./util";

describe("searchTimetable()", () => {
  test("Searches for valid timetables", () => {
    const readModule = (code: string) => {
      return JSON.parse(
        readFileSync(join(__dirname, "resources", `${code}.json`)).toString(),
      );
    };
    expect(
      searchTimetable(
        ["SC2000", "SC2001", "SC2005", "SC2006", "SC2207", "CC0007"].map(
          readModule,
        ),
        [
          {
            // 1730
            beginSecs: 17.5 * 3600,
            // 1830
            endSecs: 18.5 * 3600,
            // 1 hour
            durationSecs: 3600,
            repeats: {
              // Mon-Sun
              weekdays: range(1, 6),
              // 1-14
              teachingWeeks: range(1, 15),
            },
          },
        ],
        42,
      ),
    ).toMatchObject({
      CC0007: "83000",
      SC2000: "10185",
      SC2001: "10212",
      SC2005: "10273",
      SC2006: "10296",
      SC2207: "10341",
    });
  });
});
