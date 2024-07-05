/*
 * NTUModmap
 * modschedule
 * Timetable Evaluation
 */

import { describe, expect, test } from "@jest/globals";
import {
  FitError,
  Intervals,
  explodeBlock,
  explodeClass,
  generateOffsets,
} from "./interval";
import { ClassType } from "./models";
import { range } from "./util";

describe("generateOffsets()", () => {
  test("Generates offsets for Tues, Thus for weeks 1, 3, 5", () => {
    expect(
      generateOffsets({
        weekdays: [2, 4],
        teachingWeeks: [1, 3, 5],
      }),
    ).toStrictEqual([86400, 259200, 1296000, 1468800, 2505600, 2678400]);
  });
});

describe("explodeClass()", () => {
  test("Generates Intervals for Class", () => {
    expect(
      explodeClass({
        type: ClassType.lab,
        group: "SCSF",
        beginSecs: 0,
        durationSecs: 5,
        venue: "SPL",
        repeats: {
          weekdays: [1],
          teachingWeeks: [2, 4],
        },
      }),
    ).toStrictEqual([
      // week 2, monday
      [[604800, 604805]],
      // week 4, monday
      [[1814400, 1814405]],
    ]);
  });
});

describe("explodeBlock()", () => {
  test("Generates Intervals for Class", () => {
    const durationSecs = 5;
    expect(
      explodeBlock({
        beginSecs: 0,
        endSecs: 10,
        durationSecs,
        repeats: {
          weekdays: [1],
          teachingWeeks: [1],
        },
      }),
    ).toStrictEqual([
      // week 1, monday
      range(0, 6).map((offset) => [offset, offset + durationSecs - 1]),
    ]);
  });
});

describe("Intervals.canFit()", () => {
  test("Can fit non-overlapping intervals", () => {
    const intervals = new Intervals();
    expect(
      intervals.canFit([
        [[1, 5]],
        // [4,11] option should be rejected as it does not fit with [1,5]
        [
          [4, 11],
          [5, 10],
        ],
      ]),
    ).toStrictEqual([
      [1, 5],
      [5, 10],
    ]);
    // canFit() should not alter Intervals state
    expect(intervals.size).toBe(0);
  });
  test("Rejects overlapping options with FitError", () => {
    const intervals = new Intervals();
    expect(() => intervals.canFit([[[1, 5]], [[4, 11]]])).toThrow(FitError);
    // canFit() should not alter Intervals state
    expect(intervals.size).toBe(0);
  });
});

describe("Intervals.fit()", () => {
  test("Can fit non-overlapping options", () => {
    const intervals = new Intervals();
    intervals.fit([
      [1, 5],
      [5, 10],
    ]);
    expect(intervals.size).toBe(2);
  });
});

describe("Intervals.remove()", () => {
  test("Removes interval from Intervals", () => {
    const intervals = new Intervals();
    intervals.fit([[1, 2]]);
    expect(intervals.size).toBe(1);
    intervals.remove([1, 2]);
    expect(intervals.size).toBe(0);
  });
});
