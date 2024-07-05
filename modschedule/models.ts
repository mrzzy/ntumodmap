/*
 * NTUModmap
 * modschedule
 * Models
 */

/** Supported class types for {@link Class} */
export enum ClassType {
  lecture = "LEC/STUDIO",
  tutorial = "TUT",
  lab = "LAB",
}

/** Defines repetition parameters for repeating time intervals. */
export type Repeat = {
  /** ISO 8601 Weekdays this time interval repeats. 1 = Monday. */
  weekdays: number[];
  /** List of Teaching Weeks numbers this time time interval repeats is in effect. */
  teachingWeeks: number[];
};

/** Defines a module class */
export type Class = {
  type: ClassType;
  /** Group code. Classes with the same group are colocated. */
  group: string;
  /** No. of seconds since 12am on the day of the class this class is scheduled. */
  beginSecs: number;
  /** Duration of the class in seconds */
  durationSecs: number;
  /** Name of the venue the class is to be held */
  venue: string;
  /** Repetition parameters of this class */
  repeats: Repeat;
};

/** Defines a module index option. */
export type Index = {
  index: string;
  classes: Class[];
};

/** Defines a module. */
export type Module = {
  code: string;
  indexes: Index[];
};

/** Defines a period that the user has blocked from module scheduling. */
export type Block = {
  /* Begin of the block interval as no. of seconds since 12am on the day of the blocking window. */
  beginSecs: number;
  /* End of the block interval as no. of seconds since 12am on the day of the blocking window (exclusive). */
  endSecs: number;
  /**
   * Duration of the time block in seconds. Can be shorter than the blocking window
   * delimited by 'beginSecs' and 'endSecs', implying that 'durationSecs' should
   * be blocked anytime between 'beginSecs' and 'endSecs'.
   */
  durationSecs: number;
  /** Repetition parameters of this class */
  repeats: Repeat;
};

/** Defines a time interval as a tuple of begin & end (exclusive) second offsets. */
export type Interval = [number, number];

/** Describes a timetable allocation of module codes to index codes */
export type Timetable = Record<string, string>;
