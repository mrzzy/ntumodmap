/*
 * NTUModmap
 * modschedule
 * Module Class Schedule
 */

import { parse as parseDate } from "date-fns";
import { Module, Class, Index, ClassType } from "./models";
import { parseDocument } from "htmlparser2";
import { Document } from "domhandler";
import { selectAll } from "css-select";
import { textContent } from "domutils";
import { dayOffset, range } from "./util";

/**
 * Parse timespan into an offset since 12am and duration.
 *
 * @param timespan timespan in the format 'HHMM-HHMM'.
 * @returns Offset to time of class in seconds since 12am and Duration of the
 *  class in seconds since start time.
 */
function parseTimespan(timespan: string): [number, number] {
  const parseTime = (timeStr: string) => parseDate(timeStr, "HHmm", new Date());
  const [begin, end] = timespan.split("-").map(parseTime);

  return [dayOffset(begin), (end.getTime() - begin.getTime()) / 1000];
}

/** Parse teaching weeks for a class from the given teaching week remark.
 *
 * @param remark Text remark to parse teaching from in one of the following formats:
 *  - 'Teaching Wk<BEGIN>-<END>[,<BEGIN>-<END>]...]
 *  - 'Teaching Wk<No.>[,<No.>...]
 *  - '' Empty. Assumes all 14 teaching weeks.
 *
 * @returns 1-index teaching week numbers on which the class is held
 *  or an empty list if no teaching weeks could be parsed.
 */
export function parseTeachingWeeks(remark: string): number[] {
  const prefix = "Teaching Wk";

  if (!remark.includes(prefix)) {
    return range(1, 15);
  }
  return remark
    .substring(prefix.length)
    .split(",")
    .flatMap((span) => {
      if (span.includes("-")) {
        // teaching week span in '<BEGIN>-<END>' format
        // generate teaching week indices from begin to end.
        const bounds = span.split("-");
        const [begin, end] = [parseInt(bounds[0]), parseInt(bounds[1])];
        return range(begin, end + 1);
      }
      // teaching week span in single index format
      return [parseInt(span)];
    });
}

/**
 * Parse class information from the given class index fields
 * @param List of class index fields to parse from
 *
 * @returns Parsed class information.
 */
function parseClass(fields: string[]): Class {
  const [offsetSecs, durationSecs] = parseTimespan(fields[4]);

  return {
    type: fields[1] as ClassType,
    group: fields[2],
    beginSecs: offsetSecs,
    durationSecs,
    venue: fields[5],
    repeats: {
      weekdays: [parseDate(fields[3], "EEE", new Date()).getDay()],
      teachingWeeks: parseTeachingWeeks(fields[6]),
    },
  };
}

/**
 * Parse module information from the given HTML document.
 *
 * @param html NTU class schedule HTML document to parse module information form.
 * @returns Parsed module information.
 */
function parseModule(document: Document): Module {
  const tables = selectAll("table", document);

  if (tables.length != 2) {
    throw new Error(
      `Expected 2 <table>s in Class Schedule HTML, got: ${tables.length}`,
    );
  }

  // first table contains module metadata
  const modMeta = selectAll("tr:first-child td", tables[0]);
  if (modMeta.length != 3) {
    throw new Error(
      `Expected 3 <tr>s in Class Schedule HTML, got: ${modMeta.length}`,
    );
  }

  // second table contains module indexes
  const indexRows = selectAll("tr", tables[1]);
  let index = null;
  // skip first header row
  const indexes = [];
  for (let i = 1; i < indexRows.length; i++) {
    // only first row of a index contains the index code
    // carry over the index code to other rows of the inde
    const fields = indexRows[i].children
      .map(textContent)
      .filter((c) => c !== "\n");
    const indexCode = fields[0];
    if (indexCode != null && indexCode !== "") {
      // new index code: create new index
      index = {
        index: indexCode,
        classes: [],
      } as Index;
      indexes.push(index);
    }

    // parse class for this index
    index!.classes.push(parseClass(fields));
  }

  return {
    code: textContent(modMeta[0]),
    indexes,
  };
}

/**
 * Fetch module information for the given module module code.
 *
 * @param year Academic year to retrieve indexes for.
 * @param semester Academic semester to retrieve indexes for.
 * @param code Module code specifying the module to retrieve indexes for.
 *
 * @returns Promise that resolves to module for given module code.
 */
export async function fetchModule(
  year: number,
  semester: number,
  code: string,
): Promise<Module> {
  // perform request on class schedule site
  const response = await fetch(
    "https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Accept: "text/html",
      },
      body: new URLSearchParams({
        acadsem: `${year};${semester}`,
        r_course_yr: "",
        r_subj_code: code,
        // F: full-time
        r_search_type: "F",
        boption: "Search",
        staff_access: "false",
      }).toString(),
    },
  );

  if (!response.ok) {
    throw new Error(
      `${response.status} status fetching class schedule: ${response.statusText}`,
    );
  }
  const text = await response.text();
  if (text.includes("Class schedule is not available.")) {
    throw new Error(
      `No class schedule for module: ${code} in year ${year} semester ${semester}`,
    );
  }
  const document = parseDocument(text);
  return parseModule(document);
}
