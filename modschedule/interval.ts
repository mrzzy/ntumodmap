/*
 * NTUModmap
 * modschedule
 * Timetable Evaluation
 */

import IntervalTree, { Interval as _Interval } from "@flatten-js/interval-tree";
import { Interval, Class, Block, Repeat } from "./models";
import { range } from "./util";

const DAY_SECS = 60 * 60 * 24;
const WEEK_SECS = DAY_SECS * 7;

/**
 * Generate offsets for repetitions generated given repeat parameters.
 * @param repeats Repeat parameters to generate repetitions for.
 * @returns A list of second offsets, each defining the relative start of a repetition
 *  relative to other repetitions.
 */
export function generateOffsets(repeats: Repeat): number[] {
  const { teachingWeeks, weekdays } = repeats;
  return teachingWeeks.flatMap((week) =>
    weekdays.map(
      (weekday) => (week - 1) * WEEK_SECS + (weekday - 1) * DAY_SECS,
    ),
  );
}

/**
 * Explode a Class into a list of interval options.
 * @param cls Module Class to explode into Interval options.
 * @returns A list time sorted of interval options where
 *  each inner list represents interchangeable options for fitting the Class.
 */
export function explodeClass(cls: Class): Interval[][] {
  return generateOffsets(cls.repeats).map((offset) => {
    // single interval element: classes only have 1 option.
    const begin = offset + cls.beginSecs;
    return [[begin, begin + cls.durationSecs]];
  });
}

/**
 * Explode a Block into a list of interval options.
 * @param block Time Block to explode into Interval options.
 * @returns A list of time sorted interval options where each inner list represents
 *  interchangeable options for fitting the Block.
 * @throws If given an invalid block eg. duration does not fit within block interval.
 */
export function explodeBlock(block: Block): Interval[][] {
  return generateOffsets(block.repeats).map((offset) => {
    // compute latest time block can start for blocking window
    const latestBegin = block.endSecs - block.durationSecs;
    if(latestBegin < block.beginSecs) {
      throw "Invalid block: duration does not fit within block interval.";
    }

    // generate options for all possible begin times for the block at 10 minute resolution.
    return range(block.beginSecs, latestBegin + 1).map((beginSecs) => {
      const begin = offset + beginSecs;
      return [
        begin,
        // -1 block time range ends right before end time
        begin + block.durationSecs - 1,
      ];
    });
  });
}

/** Error thrown when attempting to fit intervals fails  */
export class FitError extends Error {}

/**
 * Converts a begin, end (exclusive) interval to begin, end (inclusive) interval
 * supported by interval-tree.
 */
const toInclusive = ([begin, end]: Interval) => new _Interval(begin, end - 1);

/** Defines a collection of Intervals */
export class Intervals {
  // interval tree stores end inclusive intervals
  tree: IntervalTree<Interval>;

  constructor() {
    this.tree = new IntervalTree<Interval>();
  }

  /**
   * Non mutating check whether the given interval options fit within existing intervals.
   * @param options A list of time sorted interval options where each inner list
   *  represents interchangeable options for fitting the interval.
   * @returns List of interval options that fit with existing intervals.
   *  Guaranteed to be sorted and non overlapping.
   * @throws {@link FitError} if unable with fit any of the intervals options
   *  into existing intervals.
   */
  canFit(options: Interval[][]): Interval[] {
    // additional interval tree to check for intersections between selected options
    const nonOverlapping = new IntervalTree<Interval>();
    return options.map((intervals) => {
      // find first non overlapping interval
      const interval = intervals.find(
        (interval) =>
          !this.tree.intersect_any(toInclusive(interval)) &&
          !nonOverlapping.intersect_any(toInclusive(interval)),
      );
      if (interval == null) {
        throw new FitError(
          `Cannot fit interval set into existing intervals: ${intervals}`,
        );
      }
      nonOverlapping.insert(toInclusive(interval));
      return interval;
    });
  }

  /**
   * Fits given intervals into existing intervals.
   * Note that this method does not reject non-overlapping intervals. See {@link canFit()}.
   * @param intervals List of intervals to fit into the existing intervals.
   * @returns List of interval options that fits with existing intervals.
   */
  fit(intervals: Interval[]) {
    // interval tree uses inclusive intervals
    intervals.map(toInclusive).map((interval) => this.tree.insert(interval));
  }

  /**
   * Removes given interval from the collection of intervals.
   * Has no effect if given interval not found in collection.
   * @param interval Interval to remove from collection of intervals.
   */
  remove(interval: Interval) {
    this.tree.remove(toInclusive(interval));
  }

  get size(): number {
    return this.tree.size;
  }
}
